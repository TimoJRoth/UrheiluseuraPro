"""
Lähdetason havainto: yksi seuratietue yhdestä lähteestä yhdellä keruuhetkellä.

Ingestorit tuottavat ClubObservation-tietueita. Ne normalisoidaan,
deduplikoidaan ja yhdistetään Club-master-tietueisiin.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from urheiluseurapro.models.contact_person import ObservationContactPerson
from urheiluseurapro.models.enums import ClubStatus, ClubType, LegalForm, MatchConfidence, MatchStatus


class ClubObservation(BaseModel):
    """
    Lähteen raakahavainto ennen master-yhdistämistä.

    Sisältää sekä alkuperäiset että normalisoidut kentät.
    """

    # --- Tunnisteet ---
    observation_id: str = Field(description="UUID, havainnon pääavain")
    source_id: str = Field(description="Lähteen tunniste, esim. suomisport")
    source_record_key: str | None = Field(
        default=None,
        description="Lähteen oma avain (API ID, URL-polku tms.)",
    )
    source_url: HttpUrl | str | None = None
    ingestion_run_id: str | None = None

    # --- Identiteetti (raaka + normalisoitu) ---
    name_raw: str = Field(min_length=1)
    name_normalized: str | None = None
    name_official: str | None = None
    name_short: str | None = None
    aliases_raw: list[str] = Field(default_factory=list)

    # --- Laji ---
    sports_raw: list[str] = Field(default_factory=list)
    sports_normalized: list[str] = Field(default_factory=list)
    primary_sport: str | None = None

    # --- Sijainti ---
    municipality_raw: str | None = None
    municipality_normalized: str | None = None
    municipality_code: str | None = None
    region_raw: str | None = None
    region_normalized: str | None = None
    postal_code: str | None = None
    address_raw: str | None = None
    address_normalized: str | None = None

    # --- Yhteystiedot ---
    website_raw: str | None = None
    website_normalized: str | None = None
    email_raw: str | None = None
    email_normalized: str | None = None
    phone_raw: str | None = None
    phone_normalized: str | None = None

    # --- Yhteyshenkilöt ---
    contact_persons: list[ObservationContactPerson] = Field(default_factory=list)
    # Legacy-yksittäiskentät (tuettu yhteensopivuuden vuoksi)
    contact_person_name: str | None = None
    contact_person_role: str | None = None
    contact_person_email: str | None = None
    contact_person_phone: str | None = None

    # --- Rekisteri ---
    business_id_raw: str | None = None
    business_id_normalized: str | None = None
    legal_form: LegalForm = LegalForm.UNKNOWN
    club_type: ClubType = ClubType.UNKNOWN
    suomisport_id: str | None = None
    federation_id: str | None = None

    # --- Toiminta ---
    status: ClubStatus = ClubStatus.UNKNOWN
    founded_year: int | None = None
    member_count: int | None = None

    # --- Deduplikointi ---
    match_status: MatchStatus = MatchStatus.UNMATCHED
    match_confidence: MatchConfidence = MatchConfidence.NO_MATCH
    matched_master_club_id: str | None = None
    match_score: float | None = Field(default=None, ge=0.0, le=1.0)
    match_reason: str | None = None

    # --- Metadata ---
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    first_seen_at: datetime | None = Field(
        default=None,
        description="Ensimmäinen havaintoaika (oletus: collected_at)",
    )
    last_seen_at: datetime | None = Field(
        default=None,
        description="Viimeisin havaintoaika (oletus: collected_at)",
    )
    observation_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Keruutuloksen luottamus",
    )
    raw: dict[str, Any] | None = Field(default=None, description="Alkuperäinen raakadata")
    normalization_notes: list[str] = Field(default_factory=list)

    def has_blocking_key(self) -> bool:
        """Onko havainnolla vahva deduplikointiavain."""
        return bool(
            self.business_id_normalized
            or self.suomisport_id
            or (self.name_normalized and self.municipality_normalized)
        )
