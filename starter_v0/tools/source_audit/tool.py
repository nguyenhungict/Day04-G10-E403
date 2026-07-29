from __future__ import annotations

from collections import Counter
from typing import Any
from urllib.parse import urlsplit, urlunsplit


def _normalized_url(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    parsed = urlsplit(raw if "://" in raw else f"https://{raw}")
    host = (parsed.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    path = parsed.path.rstrip("/") or "/"
    return urlunsplit((parsed.scheme.lower() or "https", host, path, parsed.query, ""))


def _domain(item: dict[str, Any]) -> str:
    url = _normalized_url(str(item.get("url") or ""))
    if url:
        return (urlsplit(url).hostname or "").lower()
    source = str(item.get("source") or "").strip().lower()
    return source.removeprefix("www.")


def audit_sources(
    items: list[dict[str, Any]] | None = None,
    min_independent_sources: int = 2,
) -> dict[str, Any]:
    clean_items = [item for item in (items or []) if isinstance(item, dict)]
    threshold = max(1, int(min_independent_sources or 2))
    normalized_urls = [_normalized_url(str(item.get("url") or "")) for item in clean_items]
    url_counts = Counter(url for url in normalized_urls if url)
    duplicate_urls = sorted(url for url, count in url_counts.items() if count > 1)
    domains = sorted({domain for item in clean_items if (domain := _domain(item))})

    if not clean_items:
        verdict = "no_items"
        notes = ["Provide collected research items before auditing sources."]
    elif len(domains) >= threshold:
        verdict = "diverse"
        notes = [f"Found {len(domains)} source domains; threshold is {threshold}."]
    else:
        verdict = "needs_more_sources"
        notes = [
            f"Found {len(domains)} source domain(s); collect at least {threshold} independent domains."
        ]

    if duplicate_urls:
        notes.append(f"Found {len(duplicate_urls)} duplicated URL(s).")

    return {
        "tool": "source_audit",
        "item_count": len(clean_items),
        "unique_domain_count": len(domains),
        "unique_domains": domains,
        "duplicate_urls": duplicate_urls,
        "min_independent_sources": threshold,
        "verdict": verdict,
        "notes": notes,
    }
