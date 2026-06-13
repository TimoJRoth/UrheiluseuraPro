"""Ingestion-ajon metadata."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class IngestionRun(BaseModel):
    """Yhden keruu-/latausajon metadata."""

    run_id: str
    source_id: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    status: str = Field(default="running", description="running | success | failed | partial")
    records_fetched: int = 0
    records_normalized: int = 0
    records_matched: int = 0
    records_new: int = 0
    records_updated: int = 0
    records_needs_review: int = 0
    errors: list[str] = Field(default_factory=list)
    notes: str | None = None
