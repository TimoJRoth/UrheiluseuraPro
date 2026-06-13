"""
Master Database -tietue: yhdistetty, deduplikoitu urheiluseura.

HUOM: Tämä on väliaikainen aggregate-DTO vientiin/API:in.
Totuuden lähde on relaatiotietokanta (db/schema.sql).
Tulevaisuudessa rakennetaan JOINeista, ei sisäkkäisinä listoina.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator

from urheiluseurapro.models.enums import ClubStatus, ClubType, LegalForm
from urheiluseurapro.models.merge_state import FieldObservation, MasterFieldValue
from urheiluseurapro.models.provenance import ClubSourceLink, FieldProvenance


class ClubContact(BaseModel):
    """Yhteystiedot (master-taso)."""

    website: HttpUrl | str | None = None
    email: str | None = None
    email_secondary: str | None = None
    phone: str | None = None
    phone_secondary: str | None = None
    facebook: str | None = None
    instagram: str | None = None
    twitter: str | None = None
    linkedin: str | None = None


class ClubContactPerson(BaseModel):
    """Yhteyshenkilö (avustusrekistereistä yleensä)."""

    name: str | None = None
    role: str | None = None
    email: str | None = None
    phone: str | None = None


class ClubLocation(BaseModel):
    """Maantieteellinen sijainti."""

    municipality: str | None = Field(default=None, description="Kunta")
    municipality_code: str | None = Field(default=None, description="Kuntanumero, esim. 837")
    region: str | None = Field(default=None, description="Maakunta")
    region_code: str | None = None
    postal_code: str | None = None
    address_street: str | None = None
    address_full: str | None = None
    country: str = Field(default="FI")
    latitude: float | None = None
    longitude: float | None = None


class ClubIdentity(BaseModel):
    """Seuran identiteetti ja nimeämistiedot."""

    name: str = Field(min_length=1, description="Master-nimi (paras saatavilla oleva)")
    name_official: str | None = Field(default=None, description="PRH/rekisterin virallinen nimi")
    name_short: str | None = Field(default=None, description="Lyhenne, esim. 'TuPy'")
    name_normalized: str | None = Field(
        default=None,
        description="Normalisoitu nimi deduplikointia varten",
    )
    aliases: list[str] = Field(default_factory=list, description="Vaihtoehtoiset nimet")


class ClubLegal(BaseModel):
    """Rekisteri- ja oikeudelliset tiedot."""

    business_id: str | None = Field(default=None, description="Y-tunnus, esim. 1234567-8")
    prh_registration_number: str | None = None
    registration_date: datetime | None = None
    legal_form: LegalForm = LegalForm.UNKNOWN
    club_type: ClubType = ClubType.UNKNOWN


class ClubSports(BaseModel):
    """Lajitiedot."""

    sports: list[str] = Field(default_factory=list, description="Lajit tekstimuodossa")
    sport_codes: list[str] = Field(
        default_factory=list,
        description="Standardoidut lajikoodit (tuleva standardi)",
    )
    primary_sport: str | None = None
    is_multi_sport: bool = False


class ClubExternalIds(BaseModel):
    """Ulkoiset tunnisteet lähteittäin."""

    suomisport_id: str | None = None
    laji_fi_id: str | None = None
    federation_ids: dict[str, str] = Field(
        default_factory=dict,
        description="source_id → ulkoinen tunniste",
    )


class ClubActivity(BaseModel):
    """Toiminnan tila ja laajuus."""

    status: ClubStatus = ClubStatus.UNKNOWN
    founded_year: int | None = Field(default=None, ge=1800, le=2100)
    member_count: int | None = Field(default=None, ge=0)
    member_count_year: int | None = None
    has_active_grant: bool | None = None
    has_facility_booking: bool | None = None
    last_activity_at: datetime | None = None


class ClubQuality(BaseModel):
    """Tietueen laatu ja ylläpidon tila."""

    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    source_count: int = Field(default=0, ge=0)
    needs_review: bool = False
    review_notes: str | None = None
    merge_version: int = Field(default=1, ge=1)


class Club(BaseModel):
    """
    Master Database -tietue (golden record).

    Yksi Club vastaa yhtä todellista urheiluseuraa, vaikka sitä
    esiintyisi useassa julkisessa lähteessä.
    """

    # --- Tunnisteet ---
    id: str = Field(description="UUID, master-tietueen pääavain")
    canonical_key: str | None = Field(
        default=None,
        description="Deterministinen avain (esim. y-tunnus tai normalisoitu nimi+kunta)",
    )

    # --- Ryhmät ---
    identity: ClubIdentity
    sports: ClubSports = Field(default_factory=ClubSports)
    legal: ClubLegal = Field(default_factory=ClubLegal)
    location: ClubLocation = Field(default_factory=ClubLocation)
    contact: ClubContact = Field(default_factory=ClubContact)
    contact_person: ClubContactPerson = Field(default_factory=ClubContactPerson)
    external_ids: ClubExternalIds = Field(default_factory=ClubExternalIds)
    activity: ClubActivity = Field(default_factory=ClubActivity)
    quality: ClubQuality = Field(default_factory=ClubQuality)

    # --- Provenienssi ---
    source_links: list[ClubSourceLink] = Field(default_factory=list)
    field_provenance: list[FieldProvenance] = Field(default_factory=list)
    field_observations: list[FieldObservation] = Field(
        default_factory=list,
        description="Kaikki lähdehavainnot kentittäin – ei koskaan automaattipoistoa",
    )
    master_values: dict[str, MasterFieldValue] = Field(
        default_factory=dict,
        description="Lasketut master-arvot ja confidence",
    )

    # --- Aikaleimat ---
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_merged_at: datetime | None = None
    last_seen_at: datetime | None = None

    # --- Laajennettavuus ---
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Lähdekohtaiset lisäkentät, joita ei ole vielä standardoitu",
    )

    @field_validator("identity")
    @classmethod
    def name_required(cls, identity: ClubIdentity) -> ClubIdentity:
        if not identity.name.strip():
            raise ValueError("Seuran nimi on pakollinen")
        return identity

    def to_export_row(self) -> dict[str, str | int | float | bool | None]:
        """Tasainen sanakirja CSV/JSON-vientiä varten."""
        return {
            "id": self.id,
            "name": self.identity.name,
            "name_official": self.identity.name_official,
            "name_short": self.identity.name_short,
            "aliases": "; ".join(self.identity.aliases) if self.identity.aliases else None,
            "primary_sport": self.sports.primary_sport,
            "sports": "; ".join(self.sports.sports) if self.sports.sports else None,
            "is_multi_sport": self.sports.is_multi_sport,
            "club_type": self.legal.club_type.value,
            "legal_form": self.legal.legal_form.value,
            "business_id": self.legal.business_id,
            "status": self.activity.status.value,
            "founded_year": self.activity.founded_year,
            "member_count": self.activity.member_count,
            "municipality": self.location.municipality,
            "municipality_code": self.location.municipality_code,
            "region": self.location.region,
            "postal_code": self.location.postal_code,
            "address_street": self.location.address_street,
            "address_full": self.location.address_full,
            "website": str(self.contact.website) if self.contact.website else None,
            "email": self.contact.email,
            "phone": self.contact.phone,
            "contact_person_name": self.contact_person.name,
            "contact_person_email": self.contact_person.email,
            "suomisport_id": self.external_ids.suomisport_id,
            "source_count": self.quality.source_count,
            "completeness_score": self.quality.completeness_score,
            "confidence_score": self.quality.confidence_score,
            "needs_review": self.quality.needs_review,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_merged_at": self.last_merged_at.isoformat() if self.last_merged_at else None,
        }
