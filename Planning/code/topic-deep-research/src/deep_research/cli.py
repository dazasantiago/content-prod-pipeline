from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import typer
from dotenv import load_dotenv

from deep_research.topic_discovery import ALL_SOURCES

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

app = typer.Typer(name="deep-research", add_completion=False)


def report_lines(report: dict[str, Any] | None) -> list[str]:
    """One line per source: what reached the digest and what went wrong."""
    lines: list[str] = []
    for src, row in (report or {}).get("by_source", {}).items():
        detail = ", ".join(f"{k} x{v}" for k, v in row["problems"].items())
        mark = "  !!" if row["ok"] == 0 else "    "
        lines.append(
            f"{mark}{src}: {row['ok']} ok, {row['skipped']} skipped, {row['error']} error"
            + (f"  [{detail}]" if detail else "")
        )
    return lines


def parse_sources(raw: str) -> frozenset[str]:
    """`all` or a comma-separated subset of hn, youtube, x, web."""
    if raw.strip().lower() == "all":
        return ALL_SOURCES
    chosen = frozenset(p.strip().lower() for p in raw.split(",") if p.strip())
    unknown = chosen - ALL_SOURCES
    if not chosen or unknown:
        raise typer.BadParameter(
            f"--sources takes 'all' or a comma-separated list of {sorted(ALL_SOURCES)}; "
            f"got {sorted(unknown) or raw!r}"
        )
    return chosen


@app.command()
def research(
    input: Path | None = typer.Option(None, "--input", help="Path to topic input JSON file"),
    topic: str | None = typer.Option(
        None, "--topic", help="Research a topic from scratch (no prior signals)"
    ),
    out_dir: Path = typer.Option(Path("results"), "--out-dir", help="Base output directory"),
    top_signals: int = typer.Option(20, "--top-signals", help="Max signals to enrich"),
    top_comments: int = typer.Option(10, "--top-comments", help="Max comments per post (Reddit and YouTube)"),
    per_source: int = typer.Option(
        8, "--per-source", help="Signals discovered per source in --topic mode"
    ),
    sources: str = typer.Option(
        "all",
        "--sources",
        help="--topic mode: all, or a comma-separated list of hn, youtube, x, web (e.g. youtube)",
    ),
) -> None:
    """Deep-scrape a classified topic: enrich signals and discover new sources.

    Provide exactly one of --input (pre-classified signals JSON) or --topic (discover from scratch).
    """
    if (input is None) == (topic is None):
        typer.echo("Error: provide exactly one of --input or --topic", err=True)
        raise typer.Exit(1)
    chosen_sources = parse_sources(sources)
    if input is not None and chosen_sources != ALL_SOURCES:
        typer.echo("Error: --sources only applies to --topic mode", err=True)
        raise typer.Exit(1)

    if topic is not None:
        from deep_research.pipeline import run_topic

        typer.echo(f"[{topic}] discovering signals from scratch...")
        out_path, result = run_topic(
            topic,
            top_signals=top_signals,
            top_comments=top_comments,
            per_source=per_source,
            out_dir=out_dir,
            sources=chosen_sources,
        )
    else:
        assert input is not None
        from deep_research.loader import load_topic_input
        from deep_research.pipeline import run

        if not input.exists():
            typer.echo(f"Error: input file not found: {input}", err=True)
            raise typer.Exit(1)

        topic_input = load_topic_input(input)
        typer.echo(f"[{topic_input.topic}] {len(topic_input.signals)} signals loaded")
        out_path, result = run(
            topic_input,
            top_signals=top_signals,
            top_comments=top_comments,
            out_dir=out_dir,
        )

    kept = len(result.enriched_signals)
    discarded = result.signals_attempted - kept

    typer.echo(f"\n[{result.topic_input.topic}] -> {out_path}/")
    typer.echo(
        f"  signals_enriched.json    ({kept} with content, {discarded} discarded empty)"
    )
    typer.echo(f"  discovered_sources.json  ({len(result.discovered_sources)} sources)")
    typer.echo("  run.json — what each source delivered:")
    for line in report_lines(result.run_report):
        typer.echo(line)
