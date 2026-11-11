from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest
from youtube_transcript_api import RequestBlocked, TranscriptsDisabled

from deep_research.enrichers.youtube import (
    YouTubeEnricher,
    _clock,
    _extract_video_id,
    _format_timed,
    _parse_chapters,
)
from deep_research.models import Signal


def _make_signal(
    url: str = "https://www.youtube.com/watch?v=abc123XYZ00",
    signal_type: str = "yt_video",
    description: str | None = None,
) -> Signal:
    return Signal(
        source="youtube",
        source_id="abc123XYZ00",
        title="Test video",
        url=url,
        description=description,
        posted_at=None,
        language="en",
        metrics={},
        signal_type=signal_type,  # type: ignore[arg-type]
    )


def _api(segments: list[dict[str, Any]] | None = None, error: Exception | None = None) -> MagicMock:
    """Stand-in for YouTubeTranscriptApi: `fetch()` returns the segments or raises."""
    api = MagicMock()
    if error is not None:
        api.fetch.side_effect = error
    else:
        fetched = MagicMock()
        fetched.to_raw_data.return_value = segments or []
        fetched.language_code = "en"
        fetched.is_generated = True
        api.fetch.return_value = fetched
    return api


def _client() -> httpx.Client:
    return MagicMock(spec=httpx.Client)


SEGMENTS = [{"text": "Hello world", "start": 0.0, "duration": 1.0}]


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ?t=30", "dQw4w9WgXcQ"),
        ("https://example.com/not-youtube", ""),
    ],
)
def test_extract_video_id(url: str, expected: str) -> None:
    assert _extract_video_id(url) == expected


def test_can_enrich_yt_video() -> None:
    assert YouTubeEnricher(api=_api()).can_enrich(_make_signal(signal_type="yt_video"))


def test_can_enrich_youtube_url() -> None:
    signal = _make_signal(url="https://www.youtube.com/watch?v=abc", signal_type="signal")
    assert YouTubeEnricher(api=_api()).can_enrich(signal)


def test_enrich_success_keeps_timestamps_and_metadata() -> None:
    enricher = YouTubeEnricher(force=True, api=_api(SEGMENTS))

    result = enricher.enrich(_make_signal(), _client())

    assert result.fetch_status == "ok"
    assert result.full_text == "[00:00] Hello world"
    assert result.metadata["transcript_segment_count"] == 1
    assert result.metadata["transcript_duration_s"] == 1
    assert result.metadata["transcript_language"] == "en"
    assert result.metadata["transcript_generated"] is True
    assert result.metadata["comments_fetched"] == 0


def test_format_timed_groups_by_block() -> None:
    segments = [
        {"text": "a", "start": 0.0, "duration": 5.0},
        {"text": "b\nb", "start": 10.0, "duration": 5.0},
        {"text": "c", "start": 31.0, "duration": 5.0},
        {"text": "d", "start": 65.0, "duration": 5.0},
    ]
    assert _format_timed(segments, block_seconds=30) == "[00:00] a b b\n[00:30] c\n[01:00] d"
    # default block is 15 s: the second segment (10 s) joins the first, the third starts a new line
    assert _format_timed(segments) == "[00:00] a b b\n[00:30] c\n[01:00] d"
    finer = [{"text": "x", "start": 0.0, "duration": 5.0}, {"text": "y", "start": 16.0, "duration": 5.0}]
    assert _format_timed(finer) == "[00:00] x\n[00:15] y"


def test_format_timed_empty() -> None:
    assert _format_timed([]) == ""


@pytest.mark.parametrize("seconds,expected", [(0, "00:00"), (65, "01:05"), (3725, "1:02:05")])
def test_clock(seconds: int, expected: str) -> None:
    assert _clock(seconds) == expected


def test_parse_chapters_from_description() -> None:
    description = "Intro text\n0:00 Intro\n1:30 - Pricing\n1:02:05 Day one\nlinks below"
    chapters = _parse_chapters(description)
    assert [c["title"] for c in chapters] == ["Intro", "Pricing", "Day one"]
    assert [c["start_s"] for c in chapters] == [0, 90, 3725]


def test_parse_chapters_requires_zero_start_and_three_entries() -> None:
    assert _parse_chapters("0:00 Intro\n1:00 Next") == []
    assert _parse_chapters("0:10 A\n1:00 B\n2:00 C") == []
    assert _parse_chapters("no timestamps here") == []


def test_enrich_records_chapters() -> None:
    description = "0:00 Hook\n0:40 How it works\n3:00 Risks"
    enricher = YouTubeEnricher(force=True, api=_api(SEGMENTS))
    result = enricher.enrich(_make_signal(description=description), _client())
    assert len(result.metadata["chapters"]) == 3  # type: ignore[arg-type]


def test_enrich_transcripts_disabled_is_skipped() -> None:
    enricher = YouTubeEnricher(force=True, api=_api(error=TranscriptsDisabled("abc123XYZ00")))
    result = enricher.enrich(_make_signal(), _client())
    assert result.fetch_status == "skipped"
    assert result.full_text is None


def test_enrich_blocked_ip_is_an_error_that_mentions_cookies() -> None:
    enricher = YouTubeEnricher(force=True, api=_api(error=RequestBlocked("abc123XYZ00")))
    result = enricher.enrich(_make_signal(), _client())
    assert result.fetch_status == "error"
    assert "YOUTUBE_COOKIES_FILE" in (result.fetch_error or "")


def test_enrich_unexpected_error_is_an_error() -> None:
    enricher = YouTubeEnricher(force=True, api=_api(error=ValueError("boom")))
    result = enricher.enrich(_make_signal(), _client())
    assert result.fetch_status == "error"
    assert result.fetch_error == "boom"


def test_enrich_no_url_returns_skipped() -> None:
    signal = Signal(
        source="youtube", source_id="", title="no url", url=None,
        description=None, posted_at=None, language=None, metrics={},
    )
    result = YouTubeEnricher(api=_api()).enrich(signal, _client())
    assert result.fetch_status == "skipped"


# ── comments ──────────────────────────────────────────────────────────────────

def _comments_client(items: list[dict[str, Any]], ok: bool = True) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.is_success = ok
    resp.status_code = 200 if ok else 403
    resp.json.return_value = {"items": items}
    client = MagicMock(spec=httpx.Client)
    client.get.return_value = resp
    return client


def _comment(text: str, likes: int) -> dict[str, Any]:
    return {"snippet": {"topLevelComment": {"snippet": {"textDisplay": text, "likeCount": likes}}}}


def test_top_comments_are_appended(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("YOUTUBE_API_KEY", "fake-key")
    enricher = YouTubeEnricher(force=True, top_comments=2, api=_api(SEGMENTS))
    client = _comments_client([_comment("great   explanation", 12), _comment("second", 3)])

    result = enricher.enrich(_make_signal(), client)

    assert result.full_text is not None
    assert "TOP COMMENTS (most relevant first):" in result.full_text
    assert "- (12 likes) great explanation" in result.full_text
    assert result.metadata["comments_fetched"] == 2
    params = client.get.call_args.kwargs["params"]
    assert params["order"] == "relevance" and params["maxResults"] == 2


def test_comments_unavailable_still_returns_the_transcript(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("YOUTUBE_API_KEY", "fake-key")
    enricher = YouTubeEnricher(force=True, top_comments=5, api=_api(SEGMENTS))

    result = enricher.enrich(_make_signal(), _comments_client([], ok=False))

    assert result.fetch_status == "ok"
    assert result.full_text == "[00:00] Hello world"
    assert result.metadata["comments_fetched"] == 0


def test_no_comment_calls_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    enricher = YouTubeEnricher(force=True, top_comments=5, api=_api(SEGMENTS))
    client = _comments_client([_comment("x", 1)])

    enricher.enrich(_make_signal(), client)

    client.get.assert_not_called()


# ── outlier gate (classic --input mode) ───────────────────────────────────────

@pytest.mark.parametrize("outlier_ratio", [2.0, 0.5, 0.34, 1.0])
def test_skips_mid_range_outlier_ratio(outlier_ratio: float) -> None:
    signal = _make_signal()
    signal.metrics = {"outlier_ratio": outlier_ratio}
    result = YouTubeEnricher(api=_api(SEGMENTS)).enrich(signal, _client())
    assert result.fetch_status == "skipped"
    assert "outlier_ratio" in (result.fetch_error or "")


@pytest.mark.parametrize("outlier_ratio", [3.0, 5.2, 0.33, 0.1])
def test_enriches_threshold_outlier_ratio(outlier_ratio: float) -> None:
    signal = _make_signal()
    signal.metrics = {"outlier_ratio": outlier_ratio}
    result = YouTubeEnricher(api=_api(SEGMENTS)).enrich(signal, _client())
    assert result.fetch_status == "ok"


def test_force_bypasses_outlier_gate() -> None:
    """force=True always fetches the transcript, even when outlier_ratio is in the skip range."""
    signal = _make_signal()
    signal.metrics = {}  # no outlier_ratio — default 1.0 would normally skip
    result = YouTubeEnricher(force=True, api=_api(SEGMENTS)).enrich(signal, _client())
    assert result.fetch_status == "ok"
    assert result.full_text == "[00:00] Hello world"


def test_no_force_still_skips_midrange_regression() -> None:
    signal = _make_signal()
    signal.metrics = {"outlier_ratio": 1.0}
    result = YouTubeEnricher(force=False, api=_api(SEGMENTS)).enrich(signal, _client())
    assert result.fetch_status == "skipped"
