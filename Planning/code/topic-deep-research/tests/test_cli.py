from __future__ import annotations

import pytest
import typer

from deep_research.cli import parse_sources
from deep_research.topic_discovery import ALL_SOURCES


def test_parse_sources_all() -> None:
    assert parse_sources("all") == ALL_SOURCES
    assert parse_sources(" ALL ") == ALL_SOURCES


def test_parse_sources_subset() -> None:
    assert parse_sources("youtube") == frozenset({"youtube"})
    assert parse_sources("YouTube, hn") == frozenset({"youtube", "hn"})


@pytest.mark.parametrize("raw", ["", ",", "youtube,tiktok", "reddit"])
def test_parse_sources_rejects_unknown_or_empty(raw: str) -> None:
    with pytest.raises(typer.BadParameter):
        parse_sources(raw)
