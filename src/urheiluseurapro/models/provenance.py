"""Provenienssi: mistä kentän arvo on peräisin."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from urheiluseurapro.models.enums import FieldSource


class FieldProvenance(BaseModel):
    """Yhden kentän alkuperä master-tietueessa."""

    field_name: str
    source_id: str
    observation_id: str | None = None
    source_record_key: str | None = None
    value_at_merge: str | None = None
    merge_method: FieldSource = FieldSource.SINGLE_SOURCE
    merged_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ClubSourceLink(BaseModel):
    """Linkki master-seuran ja lähteen välillä."""

    master_club_id: str
    source_id: str
    observation_id: str
    external_id: str | None = Field(
        default=None,
        description="Lähteen oma tunniste (esim. Suomisport club ID)",
    )
    source_url: str | None = None
    first_seen_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_primary_source: bool = False
    contributed_fields: list[str] = Field(default_factory=list)
