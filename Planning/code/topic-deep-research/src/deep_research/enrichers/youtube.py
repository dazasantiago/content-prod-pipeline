from __future__ import annotations

import http.cookiejar
import logging
import os
import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx
import requests
from youtube_transcript_api import (
    IpBlocked,
    NoTranscriptFound,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
    YouTubeTranscriptApi,
)

from deep_research.enrichers.base import Enricher
from deep_research.models import EnrichedSignal, Signal

log = logging.getLogger(__name__)

_MAX_CHARS = 30_000
_BLOCK_SECONDS = 15
_COMMENT_CHARS = 300
_YT_COMMENTS = "https://www.googleapis.com/youtube/v3/commentThreads"
_CHAPTER_LINE = re.compile(r"^\s*(?:(\d{1,2}):)?(\d{1,2}):(\d{2})\s*[-–—:)\]]*\s*(.+?)\s*$")


class YouTubeEnricher(Enricher):
    """Transcript with timestamps, chapters and the most relevant comments of a video.

    The timestamps are what lets the digest read a video's *structure* (how long the hook is,
    where the sections change); the comments show what the audience reacted to.
    """

    def __init__(
        self,
        force: bool = False,
        top_comments: int = 0,
        api: YouTubeTranscriptApi | None = None,
    ) -> None:
        self._force = force
        self._top_comments = top_comments
        self._api_key = os.environ.get("YOUTUBE_API_KEY", "")
        self._api = api if api is not None else _build_api()

    def can_enrich(self, signal: Signal) -> bool:
        if signal.signal_type == "yt_video":
            return True
        url = signal.url or ""
        return "youtube.com/watch" in url or "youtu.be/" in url

    def enrich(self, signal: Signal, client: httpx.Client) -> EnrichedSignal:
        scraped_at = datetime.now(UTC).isoformat()
        video_id = _extract_video_id(signal.url or "")
        if not video_id and signal.signal_type == "yt_video":
            video_id = signal.source_id

        if not video_id:
            return _result(
                signal, scraped_at, "skipped", None, {}, "could not extract video_id from url"
            )

        raw_ratio = signal.metrics.get("outlier_ratio")
        outlier_ratio = float(raw_ratio) if isinstance(raw_ratio, (int, float)) else 1.0
        if not self._force and outlier_ratio >= 0.34 and outlier_ratio < 3.0:
            log.info("YouTube skip gate: %s outlier_ratio=%.2f", video_id, outlier_ratio)
            return _result(
                signal,
                scraped_at,
                "skipped",
                None,
                {"video_id": video_id, "outlier_ratio": outlier_ratio},
                f"outlier_ratio {outlier_ratio:.2f} outside enrichment range (>=3.0 or <=0.33)",
            )

        log.info("YouTube transcript fetch: %s (force=%s)", video_id, self._force)
        try:
            fetched = self._api.fetch(video_id, languages=["en", "es"])
            segments: list[dict[str, Any]] = fetched.to_raw_data()
        except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as exc:
            log.warning("YouTube transcript skipped: %s — %s", video_id, type(exc).__name__)
            return _result(
                signal, scraped_at, "skipped", None, {"video_id": video_id}, type(exc).__name__
            )
        except (RequestBlocked, IpBlocked) as exc:
            log.warning("YouTube blocked this IP for %s — set YOUTUBE_COOKIES_FILE", video_id)
            return _result(
                signal,
                scraped_at,
                "error",
                None,
                {"video_id": video_id},
                f"{type(exc).__name__}: YouTube blocked the request (try YOUTUBE_COOKIES_FILE)",
            )
        except Exception as exc:
            log.warning("YouTube transcript error: %s — %s", video_id, exc)
            return _result(signal, scraped_at, "error", None, {"video_id": video_id}, str(exc))

        text = _format_timed(segments)
        comments = self._fetch_comments(video_id, client) if self._top_comments > 0 else []
        if comments:
            text += "\n\nTOP COMMENTS (most relevant first):\n" + "\n".join(comments)

        last = segments[-1] if segments else {"start": 0.0, "duration": 0.0}
        metadata: dict[str, object] = {
            "video_id": video_id,
            "transcript_segment_count": len(segments),
            "transcript_duration_s": round(float(last["start"]) + float(last["duration"])),
            "transcript_language": fetched.language_code,
            "transcript_generated": fetched.is_generated,
            "chapters": _parse_chapters(signal.description or ""),
            "comments_fetched": len(comments),
        }
        log.info("YouTube transcript ok: %s (%d segments)", video_id, len(segments))
        return _result(signal, scraped_at, "ok", text, metadata, None)

    def _fetch_comments(self, video_id: str, client: httpx.Client) -> list[str]:
        """Top-level comments ordered by relevance. Empty when disabled, missing key or any error."""
        if not self._api_key:
            return []
        try:
            resp = client.get(
                _YT_COMMENTS,
                params={
                    "part": "snippet",
                    "videoId": video_id,
                    "order": "relevance",
                    "maxResults": max(1, min(self._top_comments, 100)),
                    "textFormat": "plainText",
                    "key": self._api_key,
                },
                timeout=15,
            )
            if not resp.is_success:
                log.info("YouTube comments unavailable for %s (HTTP %d)", video_id, resp.status_code)
                return []
            out: list[str] = []
            for item in resp.json().get("items", []):
                top = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                body = " ".join(str(top.get("textDisplay", "")).split())[:_COMMENT_CHARS]
                if body:
                    out.append(f"- ({int(top.get('likeCount', 0))} likes) {body}")
            return out
        except Exception as exc:
            log.warning("YouTube comments error for %s: %s", video_id, exc)
            return []


def _build_api() -> YouTubeTranscriptApi:
    """Transcript client. With YOUTUBE_COOKIES_FILE it sends the cookies of a logged-in browser,
    which is the fallback when YouTube blocks the plain request (429 / IP blocked)."""
    cookies_path = os.environ.get("YOUTUBE_COOKIES_FILE", "")
    if not cookies_path:
        return YouTubeTranscriptApi()
    jar = http.cookiejar.MozillaCookieJar(cookies_path)
    jar.load(ignore_discard=True, ignore_expires=True)
    session = requests.Session()
    session.cookies = jar  # type: ignore[assignment]
    log.info("YouTubeEnricher: using cookies from %s", cookies_path)
    return YouTubeTranscriptApi(http_client=session)


def _result(
    signal: Signal,
    scraped_at: str,
    status: str,
    text: str | None,
    metadata: dict[str, object],
    error: str | None,
) -> EnrichedSignal:
    return EnrichedSignal(
        original=signal,
        full_text=text,
        metadata=metadata,
        scraped_at=scraped_at,
        fetch_status=status,  # type: ignore[arg-type]
        fetch_error=error,
    )


def _clock(seconds: float) -> str:
    total = int(seconds)
    hours, rest = divmod(total, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"


def _format_timed(segments: list[dict[str, Any]], block_seconds: int = _BLOCK_SECONDS) -> str:
    """Join transcript segments into one line per `block_seconds`, each prefixed `[MM:SS]`."""
    lines: list[str] = []
    block_start = -1
    parts: list[str] = []
    for seg in segments:
        start = float(seg.get("start", 0.0))
        bucket = int(start // block_seconds) * block_seconds
        if bucket != block_start:
            if parts:
                lines.append(f"[{_clock(block_start)}] {' '.join(parts)}")
            block_start, parts = bucket, []
        parts.append(" ".join(str(seg.get("text", "")).split()))
    if parts:
        lines.append(f"[{_clock(block_start)}] {' '.join(parts)}")
    return "\n".join(lines)[:_MAX_CHARS]


def _parse_chapters(description: str) -> list[dict[str, object]]:
    """Chapters as YouTube defines them: a `0:00` first line and at least three timestamps."""
    chapters: list[dict[str, object]] = []
    for line in description.splitlines():
        m = _CHAPTER_LINE.match(line)
        if not m:
            continue
        hours, minutes, secs, title = m.groups()
        start = int(hours or 0) * 3600 + int(minutes) * 60 + int(secs)
        chapters.append({"start": _clock(start), "start_s": start, "title": title[:100]})
    if len(chapters) < 3 or chapters[0]["start_s"] != 0:
        return []
    return chapters


def _extract_video_id(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        qs = parse_qs(parsed.query)
        ids = qs.get("v", [])
        return ids[0] if ids else ""
    if parsed.netloc in ("youtu.be",):
        return parsed.path.lstrip("/").split("?")[0]
    # bare video_id pattern as last resort
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else ""
