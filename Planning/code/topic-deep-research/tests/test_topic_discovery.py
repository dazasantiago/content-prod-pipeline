from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest

from deep_research.models import Signal
from deep_research.topic_discovery import (
    _interleave,
    _parse_duration,
    discover_hn_signals,
    discover_topic_signals,
    discover_youtube_signals,
)


def _mock_http_get(json_body: dict[str, Any]) -> httpx.Client:
    resp = MagicMock(spec=httpx.Response)
    resp.json.return_value = json_body
    resp.raise_for_status.return_value = None
    client = MagicMock(spec=httpx.Client)
    client.get.return_value = resp
    return client


# ── HN ────────────────────────────────────────────────────────────────────────

def test_discover_hn_signals_parses_hits() -> None:
    payload = {
        "hits": [
            {
                "objectID": "12345",
                "title": "GLM 5.2 is out",
                "url": "https://example.com/glm",
                "created_at": "2026-06-01T00:00:00.000Z",
                "points": 300,
                "num_comments": 45,
            }
        ]
    }
    signals = discover_hn_signals("GLM 5.2", _mock_http_get(payload))
    assert len(signals) == 1
    s = signals[0]
    assert s.source == "hn"
    assert s.source_id == "12345"
    assert s.signal_type == "signal"
    assert s.url == "https://example.com/glm"
    assert s.metrics["points"] == 300


def test_discover_hn_signals_fallback_url_when_no_url_field() -> None:
    payload = {
        "hits": [{"objectID": "99", "title": "Ask HN: ...", "points": 10, "num_comments": 5}]
    }
    signals = discover_hn_signals("topic", _mock_http_get(payload))
    assert signals[0].url == "https://news.ycombinator.com/item?id=99"


def test_discover_hn_signals_failure_returns_empty() -> None:
    client = MagicMock(spec=httpx.Client)
    client.get.side_effect = Exception("network error")
    assert discover_hn_signals("topic", client) == []


# ── YouTube ───────────────────────────────────────────────────────────────────

_YT = "https://www.googleapis.com/youtube/v3/"


def _yt_client(
    search: dict[str, Any],
    videos: dict[str, Any] | Exception | None = None,
    channels: dict[str, Any] | Exception | None = None,
) -> MagicMock:
    """Client that answers each YouTube endpoint with its own body and records the calls."""
    bodies: dict[str, Any] = {
        _YT + "search": search,
        _YT + "videos": videos if videos is not None else {"items": []},
        _YT + "channels": channels if channels is not None else {"items": []},
    }
    calls: list[tuple[str, dict[str, Any]]] = []

    def get(url: str, **kwargs: Any) -> MagicMock:
        calls.append((url, kwargs.get("params", {})))
        body = bodies[url]
        if isinstance(body, Exception):
            raise body
        return _make_response(body)

    client = MagicMock(spec=httpx.Client)
    client.get.side_effect = get
    client.calls = calls
    return client


_SEARCH_ONE = {
    "items": [
        {
            "id": {"videoId": "vid123ABC"},
            "snippet": {
                "title": "How an IPO works",
                "description": "short…",
                "publishedAt": "2024-01-01T12:00:00Z",
                "channelTitle": "Some Channel",
            },
        }
    ]
}

_VIDEOS_ONE = {
    "items": [
        {
            "id": "vid123ABC",
            "snippet": {
                "title": "How an IPO works",
                "description": "Full description\n0:00 Intro\n1:30 Pricing\n5:00 Day one",
                "publishedAt": "2024-01-01T12:00:00Z",
                "channelId": "UC1",
                "channelTitle": "Some Channel",
                "defaultAudioLanguage": "en",
            },
            "statistics": {"viewCount": "1000", "likeCount": "50", "commentCount": "5"},
            "contentDetails": {"duration": "PT9M14S"},
        }
    ]
}

_CHANNELS_ONE = {"items": [{"id": "UC1", "statistics": {"subscriberCount": "100"}}]}


def test_discover_youtube_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    client = MagicMock(spec=httpx.Client)
    client.get.side_effect = Exception("API error")
    assert discover_youtube_signals("topic", client) == []


def test_discover_youtube_adds_statistics_and_channel(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("YOUTUBE_API_KEY", "fake-key")
    client = _yt_client(_SEARCH_ONE, _VIDEOS_ONE, _CHANNELS_ONE)

    signals = discover_youtube_signals("IPO", client)

    assert len(signals) == 1
    s = signals[0]
    assert s.signal_type == "yt_video"
    assert s.source_id == "vid123ABC"
    assert s.url == "https://www.youtube.com/watch?v=vid123ABC"
    assert s.language == "en"
    assert s.description is not None and s.description.startswith("Full description")
    assert s.metrics["view_count"] == 1000
    assert s.metrics["like_count"] == 50
    assert s.metrics["comment_count"] == 5
    assert s.metrics["duration_s"] == 554
    assert s.metrics["channel_title"] == "Some Channel"
    assert s.metrics["subscriber_count"] == 100
    assert s.metrics["views_per_subscriber"] == 10.0
    assert s.metrics["like_rate"] == 0.05
    assert isinstance(s.metrics["views_per_day"], float) and s.metrics["views_per_day"] > 0
    assert isinstance(s.metrics["age_days"], int) and s.metrics["age_days"] > 0


def test_discover_youtube_searches_relevance_and_view_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("YOUTUBE_API_KEY", "fake-key")
    client = _yt_client(_SEARCH_ONE, _VIDEOS_ONE, _CHANNELS_ONE)

    signals = discover_youtube_signals("IPO", client)

    orders = [p["order"] for url, p in client.calls if url.endswith("/search")]
    assert orders == ["relevance", "viewCount"]
    assert len(signals) == 1  # same video found by both searches → deduplicated
    assert signals[0].metrics["found_by"] == ["relevance", "viewCount"]


def test_discover_youtube_keeps_videos_when_statistics_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("YOUTUBE_API_KEY", "fake-key")
    client = _yt_client(_SEARCH_ONE, videos=Exception("quota"))

    signals = discover_youtube_signals("IPO", client)

    assert len(signals) == 1
    assert signals[0].title == "How an IPO works"
    assert "view_count" not in signals[0].metrics
    assert signals[0].metrics["found_by"] == ["relevance", "viewCount"]


def test_discover_youtube_hidden_subscribers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("YOUTUBE_API_KEY", "fake-key")
    hidden = {"items": [{"id": "UC1", "statistics": {"hiddenSubscriberCount": True}}]}
    client = _yt_client(_SEARCH_ONE, _VIDEOS_ONE, hidden)

    s = discover_youtube_signals("IPO", client)[0]

    assert s.metrics["subscriber_count"] is None
    assert "views_per_subscriber" not in s.metrics
    assert s.metrics["view_count"] == 1000


def test_discover_youtube_skips_items_without_video_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("YOUTUBE_API_KEY", "fake-key")
    client = _yt_client({"items": [{"id": {}, "snippet": {"title": "no id"}}]})
    assert discover_youtube_signals("topic", client) == []


def test_discover_youtube_failure_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("YOUTUBE_API_KEY", "fake-key")
    client = MagicMock(spec=httpx.Client)
    client.get.side_effect = Exception("API error")
    assert discover_youtube_signals("topic", client) == []


@pytest.mark.parametrize(
    "iso,expected",
    [("PT9M14S", 554), ("PT1H2M3S", 3723), ("PT45S", 45), ("P1DT1H", 90000), ("", None), ("x", None)],
)
def test_parse_duration(iso: str, expected: int | None) -> None:
    assert _parse_duration(iso) == expected


# ── discover_topic_signals (interleave) ───────────────────────────────────────

def test_discover_topic_signals_interleaves_hn_and_youtube(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("YOUTUBE_API_KEY", "fake-key")
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)

    hn_payload = {
        "hits": [{"objectID": "h1", "title": "HN post", "points": 10, "num_comments": 0}]
    }
    bodies: dict[str, Any] = {
        "https://hn.algolia.com/api/v1/search": hn_payload,
        _YT + "search": _SEARCH_ONE,
        _YT + "videos": _VIDEOS_ONE,
        _YT + "channels": _CHANNELS_ONE,
    }
    client = MagicMock(spec=httpx.Client)
    client.get.side_effect = lambda url, **kw: _make_response(bodies[url])

    signals = discover_topic_signals("topic", client, per_source=1)

    sources = [s.source for s in signals]
    assert "hn" in sources
    assert "youtube" in sources


# ── Helpers ───────────────────────────────────────────────────────────────────

def test_interleave_round_robin() -> None:
    def _sig(source: str) -> Signal:
        return Signal(
            source=source, source_id="x", title="t", url=None,
            description=None, posted_at=None, language=None, metrics={},
        )

    a = [_sig("a1"), _sig("a2")]
    b = [_sig("b1")]
    c = [_sig("c1"), _sig("c2"), _sig("c3")]

    result = _interleave(a, b, c)
    sources = [s.source for s in result]
    assert sources == ["a1", "b1", "c1", "a2", "c2", "c3"]


def _make_response(payload: dict[str, Any]) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.json.return_value = payload
    resp.raise_for_status.return_value = None
    return resp
