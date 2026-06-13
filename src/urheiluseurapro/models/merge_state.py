"""Merge-tilan mallit: havainnot ja master-valinnat."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class FieldObservation(BaseModel):
    """
    Yksittäinen kenttähavainto yhdestä lähteestä.

    Havaintoja ei koskaan poisteta merge-vaiheessa – vain lisätään.
    """

    id: str
    field_name: str
    value: str
    source_id: str
    observation_id: str
    observed_at: datetime
    source_record_key: str | None = None
    source_url: str | None = None
    observation_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Lähteen antama luottamus, jos saatavilla",
    )
    raw_value: str | None = Field(
        default=None,
        description="Alkuperäinen arvo ennen normalisointia",
    )


class MasterFieldValue(BaseModel):
    """Laskettu master-arvo yhdelle kentälle."""

    field_name: str
    value: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    supporting_sources: list[str] = Field(default_factory=list)
    supporting_observation_ids: list[str] = Field(default_factory=list)
    primary_source_id: str
    primary_observation_id: str
    selected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    has_conflict: bool = False
    conflicting_values: list[str] = Field(
        default_factory=list,
        description="Muut havaitut arvot samalle kentälle",
    )
