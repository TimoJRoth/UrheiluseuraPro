"""Lähteen metadata (synkronoitu sources.md:hen)."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field, HttpUrl

from urheiluseurapro.models.enums import SourceCategory, SourceFormat


class SourceFieldAvailability(BaseModel):
    """Mitä kenttiä lähde tarjoaa (K/O/E-kartoitus)."""

    name: bool = True
    sport: bool = False
    municipality: bool = False
    address: bool = False
    website: bool = False
    email: bool = False
    phone: bool = False
    contact_person: bool = False
    business_id: bool = False
    member_count: bool = False


class Source(BaseModel):
    """Tietolähteen kuvaus Master Database -järjestelmässä."""

    source_id: str = Field(min_length=1, description="Uniikki tunniste, esim. palloliitto")
    name: str = Field(description="Näyttönimi")
    url: HttpUrl | str | None = None
    category: SourceCategory
    format: list[SourceFormat] = Field(default_factory=list)
    geographic_coverage: str = Field(description="Esim. 'Koko Suomi', 'Pirkanmaa'")
    estimated_clubs: int | None = None
    priority: str = Field(default="P3", pattern=r"^P[1-4]$")
    fields: SourceFieldAvailability = Field(default_factory=SourceFieldAvailability)
    merge_priority: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Kenttäprioriteetti merge-vaiheessa (korkeampi = luotettavampi)",
    )
    robots_txt: str | None = Field(default=None, description="Sallittu / Rajoitettu / Tarkistettava")
    scraper_difficulty: int = Field(default=3, ge=1, le=5)
    notes: str | None = None
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
