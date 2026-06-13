"""Lähteiden keskitetyt asetukset (SourceConfig)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SourceConfig(BaseModel):
    """
    Yhden tietolähteen asetukset.

    Kaikki collectorit lukevat arvonsa täältä – ei kovakoodattuja source_id-,
    timeout- tai user_agent -arvoja kerääjäluokissa.
    """

    source_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    enabled: bool = True
    request_timeout: float = Field(gt=0.0)
    request_delay: float = Field(ge=0.0)
    request_retries: int = Field(ge=1, le=10)
    retry_backoff_seconds: float = Field(ge=0.0)
    user_agent: str = Field(min_length=1)
    confidence_default: float = Field(ge=0.0, le=1.0)
    base_url: str | None = None
    feed_url: str | None = None

    model_config = {"frozen": True}
