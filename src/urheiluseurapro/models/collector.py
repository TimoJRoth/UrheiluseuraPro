"""Collector-keruun yhtenäinen tulosmalli."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from urheiluseurapro.models.observation import ClubObservation


class CollectorResult(BaseModel):
    """
    Yhden seuran keruutulos yhdestä lähteestä.

    Sisältää provenience-metadatan ja ClubObservation-havainnon merge-engineä varten.
    """

    source: str = Field(description="Lähteen tunniste (source_id)")
    source_url: str | None = Field(default=None, description="Alkuperäisen tietueen URL")
    confidence: float = Field(ge=0.0, le=1.0, description="Keruutuloksen luottamus")
    fetched_at: datetime = Field(description="Milloin data haettiin")
    first_seen_at: datetime = Field(description="Ensimmäinen havaintoaika")
    last_seen_at: datetime = Field(description="Viimeisin havaintoaika")
    observation: ClubObservation

    @classmethod
    def from_observation(
        cls,
        observation: ClubObservation,
        *,
        confidence: float,
        fetched_at: datetime | None = None,
    ) -> CollectorResult:
        """Rakenna tulos olemassa olevasta havainnosta."""
        ts = fetched_at or observation.collected_at
        first = observation.first_seen_at or ts
        last = observation.last_seen_at or ts
        return cls(
            source=observation.source_id,
            source_url=str(observation.source_url) if observation.source_url else None,
            confidence=confidence,
            fetched_at=ts,
            first_seen_at=first,
            last_seen_at=last,
            observation=observation,
        )
