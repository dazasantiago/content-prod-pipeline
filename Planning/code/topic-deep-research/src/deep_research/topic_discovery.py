from __future__ import annotations

import logging
import os
import re
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from deep_research.models import Signal

log = logging.getLogger(__name__)

_HN_ALGOLIA = "https://hn.algolia.com/api/v1/search"
_YT_SEARCH = "https://www.googleapis.com/youtube/v3/search"
_YT_VIDEOS = "https://www.googleapis.com/youtube/v3/videos"
_YT_CHANNELS = "https://www.googleapis.com/youtube/v3/channels"
_X_SEARCH = "https://api.x.com/2/tweets/search/all"
_X_FIELDS = "created_at,conversation_id,lang,note_tweet,public_metrics,author_id"
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; deep-research-bot/1.0)"}

# `web` is Tavily web search, run by the pipeline rather than here; it is listed so --sources can name it.
ALL_SOURCES: frozenset[str] = frozenset({"hn", "youtube", "x", "web"})


def discover_topic_signals(
    topic: str,
    http: httpx.Client,
    per_source: int = 8,
    sources: frozenset[str] = ALL_SOURCES,
) -> list[Signal]:
    """Discover signals about `topic` from HN, YouTube and X (those in `sources`), interleaved.

    Reddit is intentionally excluded: old.reddit.com/search.json blocks bots
    unreliably, and Tavily (run in the same pipeline via discover_sources) already
    surfaces the most relevant Reddit threads as discovered_sources.
    """
    hn = discover_hn_signals(topic, http, per_source) if "hn" in sources else []
    log.info("HN discovery: %d signals", len(hn))
    yt = discover_youtube_signals(topic, http, per_source) if "youtube" in sources else []
    log.info("YouTube discovery: %d signals", len(yt))
    x = discover_x_signals(topic, http, per_source) if "x" in sources else []
    log.info("X discovery: %d signals", len(x))
    combined = _interleave(hn, yt, x)
    log.info("Total interleaved: %d signals", len(combined))
    return combined


def discover_hn_signals(topic: str, http: httpx.Client, n: int = 8) -> list[Signal]:
    """Search HN via Algolia API (no key required)."""
    try:
        resp = http.get(
            _HN_ALGOLIA,
            params={"query": topic, "tags": "story", "hitsPerPage": n},
            headers=_HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        hits: list[dict[str, Any]] = resp.json().get("hits", [])
        out: list[Signal] = []
        for h in hits:
            oid = str(h.get("objectID", ""))
            url = h.get("url") or f"https://news.ycombinator.com/item?id={oid}"
            out.append(
                Signal(
                    source="hn",
                    source_id=oid,
                    title=h.get("title") or h.get("story_title") or "",
                    url=url,
                    description=None,
                    posted_at=h.get("created_at"),
                    language=None,
                    metrics={
                        "points": h.get("points", 0),
                        "num_comments": h.get("num_comments", 0),
                    },
                    signal_type="signal",
                    roles=["signal"],
                )
            )
        return out
    except Exception as exc:
        log.warning("HN discovery failed: %s", exc)
        return []


def discover_x_signals(
    topic: str,
    http: httpx.Client,
    n: int = 8,
    *,
    window_days: int = 180,
) -> list[Signal]:
    """Search X full-archive. Requires X_BEARER_TOKEN env var; returns [] if absent.

    Always sends an explicit `start_time`: omitting it silently narrows the window to
    a few days, which surfaces as an empty result rather than an error — easy to
    misread as a permissions problem.

    No local relevance filtering or ranking: this stage doesn't score. Engagement is
    kept in `metrics` for the digest to weigh, the same way HN points are. Billing is
    per post returned (the API minimum is 10 posts, ~$0.05), so `n` is the cost knob.
    """
    token = os.environ.get("X_BEARER_TOKEN", "")
    if not token:
        return []

    start = (datetime.now(UTC) - timedelta(days=window_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        resp = http.get(
            _X_SEARCH,
            params={
                "query": f"{topic} -is:retweet -is:reply",
                "start_time": start,
                "max_results": max(10, min(n, 100)),
                "tweet.fields": _X_FIELDS,
            },
            headers={"Authorization": f"Bearer {token}", **_HEADERS},
            timeout=20,
        )
        resp.raise_for_status()
        posts: list[dict[str, Any]] = resp.json().get("data", [])
    except Exception as exc:
        log.warning("X discovery failed: %s", exc)
        return []

    out: list[Signal] = []
    for p in posts:
        text = _x_text(p)
        pid = str(p.get("id", ""))
        cid = str(p.get("conversation_id", "") or pid)
        metrics: dict[str, object] = {
            "like_count": p.get("public_metrics", {}).get("like_count", 0),
            "retweet_count": p.get("public_metrics", {}).get("retweet_count", 0),
            "reply_count": p.get("public_metrics", {}).get("reply_count", 0),
            "conversation_id": cid,
            "author_id": str(p.get("author_id", "")),
            "is_thread_root": cid == pid,
        }
        out.append(
            Signal(
                source="x",
                source_id=pid,
                title=text.strip().split("\n")[0][:120],
                url=f"https://x.com/i/status/{pid}",
                description=text,
                posted_at=p.get("created_at"),
                language=p.get("lang"),
                metrics=metrics,
                signal_type="x_post",
                roles=["signal"],
            )
        )

    return out


def _x_text(post: dict[str, Any]) -> str:
    """Full post text. `note_tweet` carries the untruncated body on long posts."""
    note = post.get("note_tweet") or {}
    text = note.get("text") or post.get("text") or ""
    return str(text)


def discover_youtube_signals(topic: str, http: httpx.Client, n: int = 8) -> list[Signal]:
    """Discover YouTube videos about `topic` and attach their performance numbers.

    Two searches, deduplicated: the most relevant `n` videos (what exists on the topic) and the
    `n` most viewed (what has worked). One `videos.list` and one `channels.list` call then add
    views, likes, comments, duration and the channel's subscribers, so the digest can tell which
    videos did well *for their channel*. Cost per run: ~200 quota units (the daily limit is 10 000).
    Requires YOUTUBE_API_KEY; returns [] if absent.
    """
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if not api_key:
        log.warning("YOUTUBE_API_KEY not set — skipping YouTube discovery")
        return []
    log.info("YouTube: searching for %r (n=%d per ordering)", topic, n)
    try:
        found: dict[str, dict[str, Any]] = {}
        for order in ("relevance", "viewCount"):
            for item in _yt_search(topic, http, api_key, n, order):
                vid = str(item.get("id", {}).get("videoId", ""))
                if not vid:
                    continue
                entry = found.setdefault(vid, {"snippet": item.get("snippet", {}), "found_by": []})
                entry["found_by"].append(order)
        details = _yt_details(list(found), http, api_key)
        subs = _yt_subscribers(
            sorted({d["snippet"].get("channelId", "") for d in details.values()} - {""}),
            http,
            api_key,
        )
    except Exception as exc:
        log.warning("YouTube discovery failed: %s", exc)
        return []

    out: list[Signal] = []
    for vid, entry in found.items():
        search_snippet: dict[str, Any] = entry["snippet"]
        det = details.get(vid)
        sn: dict[str, Any] = det["snippet"] if det else search_snippet
        metrics: dict[str, object] = {"found_by": entry["found_by"]}
        if det:
            metrics.update(_yt_metrics(det, subs.get(str(sn.get("channelId", "")))))
        out.append(
            Signal(
                source="youtube",
                source_id=vid,
                title=sn.get("title", ""),
                url=f"https://www.youtube.com/watch?v={vid}",
                description=sn.get("description") or search_snippet.get("description"),
                posted_at=sn.get("publishedAt"),
                language=sn.get("defaultAudioLanguage") or sn.get("defaultLanguage"),
                metrics=metrics,
                signal_type="yt_video",
                roles=["signal"],
            )
        )
    log.info("YouTube discovery: %d videos (%d with statistics)", len(out), len(details))
    return out


def _yt_search(
    topic: str, http: httpx.Client, api_key: str, n: int, order: str
) -> list[dict[str, Any]]:
    resp = http.get(
        _YT_SEARCH,
        params={
            "part": "snippet",
            "q": topic,
            "type": "video",
            "order": order,
            "maxResults": n,
            "relevanceLanguage": "en",
            "key": api_key,
        },
        headers=_HEADERS,
        timeout=15,
    )
    if not resp.is_success:
        log.warning("YouTube search (%s) HTTP %d: %s", order, resp.status_code, resp.text[:300])
    resp.raise_for_status()
    items: list[dict[str, Any]] = resp.json().get("items", [])
    return items


def _yt_details(ids: list[str], http: httpx.Client, api_key: str) -> dict[str, dict[str, Any]]:
    """snippet + statistics + contentDetails for up to 50 videos (1 quota unit). {} on failure."""
    if not ids:
        return {}
    try:
        resp = http.get(
            _YT_VIDEOS,
            params={
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(ids[:50]),
                "key": api_key,
            },
            headers=_HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        return {str(it["id"]): it for it in resp.json().get("items", []) if it.get("id")}
    except Exception as exc:
        log.warning("YouTube videos.list failed (statistics skipped): %s", exc)
        return {}


def _yt_subscribers(
    channel_ids: list[str], http: httpx.Client, api_key: str
) -> dict[str, int | None]:
    """Subscriber count per channel (1 quota unit). Hidden counts come back as None."""
    if not channel_ids:
        return {}
    try:
        resp = http.get(
            _YT_CHANNELS,
            params={"part": "statistics", "id": ",".join(channel_ids[:50]), "key": api_key},
            headers=_HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        out: dict[str, int | None] = {}
        for it in resp.json().get("items", []):
            st = it.get("statistics", {})
            hidden = bool(st.get("hiddenSubscriberCount"))
            out[str(it["id"])] = None if hidden else _to_int(st.get("subscriberCount"))
        return out
    except Exception as exc:
        log.warning("YouTube channels.list failed (subscribers skipped): %s", exc)
        return {}


def _yt_metrics(det: dict[str, Any], subscribers: int | None) -> dict[str, object]:
    """Descriptive numbers only — no scoring. The digest decides what counts as having worked."""
    st: dict[str, Any] = det.get("statistics", {})
    sn: dict[str, Any] = det.get("snippet", {})
    views = _to_int(st.get("viewCount"))
    likes = _to_int(st.get("likeCount"))
    published = sn.get("publishedAt")
    metrics: dict[str, object] = {
        "view_count": views,
        "like_count": likes,
        "comment_count": _to_int(st.get("commentCount")),
        "duration_s": _parse_duration(det.get("contentDetails", {}).get("duration", "")),
        "channel_id": sn.get("channelId"),
        "channel_title": sn.get("channelTitle"),
        "subscriber_count": subscribers,
    }
    if views is not None and subscribers:
        metrics["views_per_subscriber"] = round(views / subscribers, 3)
    if views is not None and published:
        try:
            age = datetime.now(UTC) - datetime.fromisoformat(str(published).replace("Z", "+00:00"))
            metrics["age_days"] = age.days
            metrics["views_per_day"] = round(views / max(age.days, 1), 1)
        except ValueError:
            pass
    if views and likes is not None:
        metrics["like_rate"] = round(likes / views, 4)
    return metrics


def _to_int(value: object) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def _parse_duration(iso: str) -> int | None:
    """ISO 8601 duration (PT1H2M3S) to seconds."""
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m or not any(m.groups()):
        return None
    days, hours, minutes, secs = (int(g or 0) for g in m.groups())
    return days * 86400 + hours * 3600 + minutes * 60 + secs


def _interleave(*lists: list[Signal]) -> list[Signal]:
    """Round-robin interleave multiple lists so no source dominates the top_signals window."""
    result: list[Signal] = []
    iters = [iter(lst) for lst in lists if lst]
    while iters:
        next_iters: list[Any] = []
        for it in iters:
            try:
                result.append(next(it))
                next_iters.append(it)
            except StopIteration:
                pass
        iters = next_iters
    return result
