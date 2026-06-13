"""HTTP-vastauksen metadata collector-provenancea varten."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class HttpFetchMetadata:
    """Yhden onnistuneen HTTP-haun metadata."""

    url: str
    fetched_at: datetime
    status_code: int
    content_type: str | None
    attempt: int
