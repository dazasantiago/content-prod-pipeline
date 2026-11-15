from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from deep_research.cli import report_lines
from deep_research.models import (
    EnrichedSignal,
    Signal,
    TopicInput,
    TopicResult,
)
from deep_research.pipeline import build_run_report
from deep_research.writer import write_topic_result


def _enriched(source: str, status: str, error: str | None = None) -> EnrichedSignal:
    signal = Signal(
        source=source, source_id="x", title="t", url=None, description=None,
        posted_at=None, language=None, metrics={},
    )
    return EnrichedSignal(
        original=signal,
        full_text="text" if status == "ok" else None,
        metadata={},
        scraped_at=datetime.now(UTC).isoformat(),
        fetch_status=status,  # type: ignore[arg-type]
        fetch_error=error,
    )


def test_report_counts_per_source_and_groups_problems() -> None:
    enriched = [
        _enriched("youtube", "ok"),
        _enriched("youtube", "ok"),
        _enriched("youtube", "skipped", "NoTranscriptFound"),
        _enriched("youtube", "error", "RequestBlocked: YouTube blocked the request"),
        _enriched("hn", "ok"),
        _enriched("reddit/python", "ok"),
    ]

    report = build_run_report("topic", enriched, [], None)

    by_source = report["by_source"]
    assert isinstance(by_source, dict)
    assert by_source["youtube"] == {
        "attempted": 4,
        "ok": 2,
        "skipped": 1,
        "error": 1,
        "problems": {"NoTranscriptFound": 1, "RequestBlocked": 1},
        "failed": [
            {"id": "x", "title": "t", "reason": "NoTranscriptFound"},
            {"id": "x", "title": "t", "reason": "RequestBlocked: YouTube blocked the request"},
        ],
    }
    assert by_source["hn"]["ok"] == 1
    assert "reddit" in by_source  # subreddits roll up into their source
    assert report["sources"] is None
    assert report["signals_attempted"] == 6


def test_requested_source_with_no_signals_is_listed_with_zeros() -> None:
    report = build_run_report("topic", [], [], frozenset({"youtube", "web"}))

    by_source = report["by_source"]
    assert isinstance(by_source, dict)
    assert by_source["youtube"]["ok"] == 0
    assert "no signals discovered" in next(iter(by_source["youtube"]["problems"]))
    assert "web" not in by_source  # web is Tavily: reported as web_sources, not as a signal source
    assert report["sources"] == ["web", "youtube"]


def test_write_topic_result_writes_run_json(tmp_path: Path) -> None:
    report = build_run_report("My Topic", [_enriched("youtube", "ok")], [], frozenset({"youtube"}))
    result = TopicResult(
        topic_input=TopicInput(topic="My Topic", generated_at="now", signals=[]),
        enriched_signals=[_enriched("youtube", "ok")],
        discovered_sources=[],
        generated_at="now",
        signals_attempted=1,
        run_report=report,
    )

    out = write_topic_result(result, base=tmp_path)

    written = json.loads((out / "run.json").read_text(encoding="utf-8"))
    assert written["by_source"]["youtube"]["ok"] == 1
    assert written["sources"] == ["youtube"]


def test_report_lines_flag_a_source_with_nothing_usable() -> None:
    report = build_run_report("t", [_enriched("youtube", "error", "RequestBlocked: x")], [], None)
    lines = report_lines(report)
    assert lines[0].startswith("  !!youtube: 0 ok, 0 skipped, 1 error")
    assert "RequestBlocked x1" in lines[0]
    assert report_lines(None) == []
