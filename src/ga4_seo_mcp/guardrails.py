"""Anti-hallucination guardrails — _meta provenance on every tool response."""
from __future__ import annotations

from datetime import datetime
from typing import Any

GUARDRAIL_SUFFIX = (
    "\n\nIMPORTANT: Use ONLY the data returned by this tool. Do not speculate "
    "about figures, do not extrapolate beyond the time range queried, and cite "
    "_meta.property + _meta.period when reporting numbers to the user."
)


def with_meta(
    payload: Any,
    *,
    source: str,
    property: str,
    period: dict | None = None,
    extra: dict | None = None,
) -> dict:
    """Wraps a tool response with provenance metadata."""
    meta = {
        "source": source,
        "property": property,
        "period": period,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
    }
    if extra:
        meta.update(extra)
    return {"data": payload, "_meta": meta}
