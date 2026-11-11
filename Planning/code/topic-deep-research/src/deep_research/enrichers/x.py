from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from deep_research.enrichers.base import Enricher
from deep_research.models import EnrichedSignal, Signal
from deep_research.topic_discovery import _X_FIELDS, _X_SEARCH, _x_text

_MAX_THREAD_POSTS = 25


class XEnricher(Enricher):
    """Expands an X post into its author's full thread.

    Discovery already captured the root post's complete text (`note_tweet`), so a
    standalone post needs no extra call. A thread root is different: the substance
    usually lives in the replies the author chained onto it, which is a separate
    search — `conversation_id:<id> from:<author>` isolates the author's own chain and
    leaves out everyone else's replies.
    """

    def __init__(self, token: str) -> None:
        self._token = token

    def can_enrich(self, signal: Signal) -> bool:
        return signal.signal_type == "x_post" and bool(self._token)

    def enrich(self, signal: Signal, client: httpx.Client) -> EnrichedSignal:
        text = signal.description or ""
        metadata: dict[str, object] = {
            "conversation_id": signal.metrics.get("conversation_id"),
            "is_thread_root": signal.metrics.get("is_thread_root"),
            "thread_post_count": 1,
        }

        # Every non-reply post is its own conversation root, so the root flag alone
        # would fire a paid search for standalone posts that have no thread at all.
        replies_exist = int(str(signal.metrics.get("reply_count") or 0)) > 0
        if signal.metrics.get("is_thread_root") and replies_exist:
            replies = self._fetch_author_thread(signal, client)
            if replies:
                text = "\n\n".join([text, *replies])
                metadata["thread_post_count"] = 1 + len(replies)

        return EnrichedSignal(
            original=signal,
            full_text=text,
            metadata=metadata,
            scraped_at=datetime.now(UTC).isoformat(),
            fetch_status="ok",
            fetch_error=None,
        )

    def _fetch_author_thread(self, signal: Signal, client: httpx.Client) -> list[str]:
        cid = signal.metrics.get("conversation_id")
        author = signal.metrics.get("author_id")
        if not cid or not author:
            return []

        # The thread can't predate its own root, and an explicit window is mandatory:
        # without start_time the API quietly returns nothing.
        start = signal.posted_at or datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        resp = client.get(
            _X_SEARCH,
            params={
                "query": f"conversation_id:{cid} from:{author}",
                "start_time": start,
                "max_results": _MAX_THREAD_POSTS,
                "tweet.fields": _X_FIELDS,
            },
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=20,
        )
        resp.raise_for_status()
        posts: list[dict[str, Any]] = resp.json().get("data", [])

        ordered = sorted(posts, key=lambda p: str(p.get("created_at", "")))
        return [
            _x_text(p) for p in ordered if str(p.get("id", "")) != signal.source_id
        ]
