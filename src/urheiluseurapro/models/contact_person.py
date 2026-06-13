"""Yhteyshenkilöiden datamallit – havainnot ja master-valinnat."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ObservationContactPerson(BaseModel):
    """Yksi yhteyshenkilö yhdessä ClubObservation-havainnossa."""

    full_name: str = Field(min_length=1)
    role: str | None = Field(
        default=None,
        description="Rooli, esim. puheenjohtaja, sihteeri",
    )
    emails: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    observation_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class ContactPersonObservation(BaseModel):
    """
    Säilytetty yhteyshenkilöhavainto yhdestä lähteestä.

    Havaintoja ei koskaan poisteta tai ylikirjoiteta merge-vaiheessa.
    """

    id: str
    role: str = Field(description="Normalisoitu rooliavain")
    role_raw: str | None = None
    full_name: str
    emails: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    source_id: str
    observation_id: str = Field(description="Ylätason ClubObservation.id")
    source_record_key: str | None = None
    source_url: str | None = None
    first_seen_at: datetime
    last_seen_at: datetime
    observation_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class MasterContactPerson(BaseModel):
    """Roolikohtainen master-yhteyshenkilö (laskettu havainnoista)."""

    role: str
    full_name: str
    emails: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    supporting_sources: list[str] = Field(default_factory=list)
    supporting_observation_ids: list[str] = Field(default_factory=list)
    primary_source_id: str
    primary_contact_person_observation_id: str
    selected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    has_conflict: bool = False
    conflicting_names: list[str] = Field(default_factory=list)
