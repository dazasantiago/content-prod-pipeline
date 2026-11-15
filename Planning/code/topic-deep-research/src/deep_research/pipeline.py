from __future__ import annotations

import os
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

import httpx

from deep_research.discovery import discover_sources
from deep_research.enrichers import HNEnricher, RedditEnricher, XEnricher, YouTubeEnricher
from deep_research.enrichers.base import Enricher
from deep_research.models import DiscoveredSource, EnrichedSignal, Signal, TopicInput, TopicResult
from deep_research.writer import write_topic_result


def run(
    topic_input: TopicInput,
    *,
    top_signals: int = 20,
    top_comments: int = 10,
    out_dir: Path = Path("results"),
    force_youtube: bool = False,
    web: bool = True,
    sources: frozenset[str] | None = None,
) -> tuple[Path, TopicResult]:
    enrichers: list[Enricher] = [
        XEnricher(token=os.environ.get("X_BEARER_TOKEN", "")),
        YouTubeEnricher(force=force_youtube, top_comments=top_comments),
        RedditEnricher(top_comments=top_comments),
        HNEnricher(),
    ]

    with httpx.Client(follow_redirects=True) as http:
        enriched = _enrich_signals(
            topic_input.signals[:top_signals],
            enrichers=enrichers,
            http=http,
        )
        discovered: list[DiscoveredSource] = (
            discover_sources(topic_input.topic) if web else []  # type: ignore[assignment]
        )

    usable = [s for s in enriched if s.full_text]

    result = TopicResult(
        topic_input=topic_input,
        enriched_signals=usable,
        discovered_sources=discovered,
        generated_at=datetime.now(UTC).isoformat(),
        signals_attempted=len(enriched),
        run_report=build_run_report(topic_input.topic, enriched, discovered, sources),
    )

    out_path = write_topic_result(result, base=out_dir)
    return out_path, result


def run_topic(
    topic: str,
    *,
    top_signals: int = 20,
    top_comments: int = 10,
    per_source: int = 8,
    out_dir: Path = Path("results"),
    sources: frozenset[str] | None = None,
) -> tuple[Path, TopicResult]:
    """Discover signals for `topic` from scratch, from `sources` (default all), then enrich them."""
    from deep_research.topic_discovery import ALL_SOURCES, discover_topic_signals

    chosen = ALL_SOURCES if sources is None else sources
    with httpx.Client(follow_redirects=True) as http:
        signals = discover_topic_signals(topic, http, per_source=per_source, sources=chosen)

    topic_input = TopicInput(
        topic=topic,
        generated_at=datetime.now(UTC).isoformat(),
        signals=signals,
    )
    return run(
        topic_input,
        top_signals=top_signals,
        top_comments=top_comments,
        out_dir=out_dir,
        force_youtube=True,
        web="web" in chosen,
        sources=chosen,
    )


def build_run_report(
    topic: str,
    enriched: list[EnrichedSignal],
    discovered: list[DiscoveredSource],
    sources: frozenset[str] | None,
) -> dict[str, object]:
    """What each source actually delivered, so a silent failure shows up in `run.json`.

    `ok` is content that reached the digest. A requested source with no signals at all (missing key,
    exhausted quota, nothing found) is listed with zeros instead of being absent.
    """
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    problems: dict[str, Counter[str]] = defaultdict(Counter)
    failed: dict[str, list[dict[str, str]]] = defaultdict(list)
    for e in enriched:
        src = e.original.source.split("/")[0]
        counts[src]["attempted"] += 1
        counts[src][e.fetch_status] += 1
        if e.fetch_status != "ok" and e.fetch_error:
            problems[src][e.fetch_error.split(":")[0][:80]] += 1
        if e.fetch_status != "ok":
            failed[src].append(
                {
                    "id": e.original.source_id,
                    "title": e.original.title[:80],
                    "reason": (e.fetch_error or "unknown")[:120],
                }
            )
    for src in sorted((sources or frozenset()) - {"web"}):
        if src not in counts:
            problems[src]["no signals discovered (missing key, exhausted quota or no results)"] += 1
            counts[src]  # register the source with zero counts
    by_source: dict[str, object] = {
        src: {
            "attempted": c["attempted"],
            "ok": c["ok"],
            "skipped": c["skipped"],
            "error": c["error"],
            "problems": dict(problems[src]),
            "failed": failed[src][:20],
        }
        for src, c in sorted(counts.items())
    }
    return {
        "topic": topic,
        "generated_at": datetime.now(UTC).isoformat(),
        "sources": sorted(sources) if sources is not None else None,
        "signals_attempted": len(enriched),
        "by_source": by_source,
        "web_sources": len(discovered),
    }


def _enrich_signals(
    signals: list[Signal],
    enrichers: list[Enricher],
    http: httpx.Client,
) -> list[EnrichedSignal]:
    results: list[EnrichedSignal] = []
    for signal in signals:
        enricher = _pick_enricher(signal, enrichers)
        if enricher is None:
            results.append(_skipped(signal, "no enricher matched"))
            continue
        try:
            results.append(enricher.enrich(signal, http))
        except Exception as exc:
            results.append(_errored(signal, str(exc)))
    return results


def _pick_enricher(signal: Signal, enrichers: list[Enricher]) -> Enricher | None:
    for enricher in enrichers:
        if enricher.can_enrich(signal):
            return enricher
    return None


def _skipped(signal: Signal, reason: str) -> EnrichedSignal:
    from datetime import UTC, datetime

    return EnrichedSignal(
        original=signal,
        full_text=None,
        metadata={},
        scraped_at=datetime.now(UTC).isoformat(),
        fetch_status="skipped",
        fetch_error=reason,
    )


def _errored(signal: Signal, reason: str) -> EnrichedSignal:
    from datetime import UTC, datetime

    return EnrichedSignal(
        original=signal,
        full_text=None,
        metadata={},
        scraped_at=datetime.now(UTC).isoformat(),
        fetch_status="error",
        fetch_error=reason,
    )
