"""Relaatiotietokannan rivimallit (1:1 taulujen kanssa)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RegionRow(BaseModel):
    code: str
    name: str


class MunicipalityRow(BaseModel):
    code: str
    name: str
    region_code: str


class SportRow(BaseModel):
    id: int
    slug: str
    name_fi: str
    name_en: str | None = None
    parent_id: int | None = None


class SportAliasRow(BaseModel):
    id: int | None = None
    sport_id: int
    alias: str


class SourceRow(BaseModel):
    source_id: str
    name: str
    category: str
    url: str | None = None
    merge_priority: int = 50
    priority: str = "P3"
    active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


class OrganizationRow(BaseModel):
    """Master-taulu: organizations."""

    id: str
    canonical_key: str | None = None
    business_id: str | None = None
    legal_form: str = "tuntematon"
    club_type: str = "tuntematon"
    status: str = "tuntematon"
    founded_year: int | None = None
    needs_review: bool = False
    completeness_score: float = 0.0
    confidence_score: float = 0.0
    merge_version: int = 1
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_merged_at: datetime | None = None
    last_seen_at: datetime | None = None


class OrganizationProfileRow(BaseModel):
    """Hakukiihdytin: organization_profile (1:1, lasketut liput – ei listoja)."""

    organization_id: str
    sport_count: int = 0
    is_multi_sport: bool = False
    location_count: int = 0
    email_count: int = 0
    phone_count: int = 0
    website_count: int = 0
    contact_person_count: int = 0
    social_account_count: int = 0
    source_count: int = 0
    has_email: bool = False
    has_website: bool = False
    has_phone: bool = False
    has_contact_person: bool = False
    has_facebook: bool = False
    has_instagram: bool = False
    has_linkedin: bool = False
    has_member_count: bool = False
    has_home_field: bool = False
    has_home_hall: bool = False
    training_facility_count: int = 0
    primary_municipality_code: str | None = None
    primary_region_code: str | None = None
    primary_latitude: float | None = None
    primary_longitude: float | None = None
    profile_updated_at: datetime | None = None


class OrganizationSizeRow(BaseModel):
    """Jäsenmäärät: organization_size (1:1)."""

    organization_id: str
    member_count: int | None = None
    junior_member_count: int | None = None
    adult_member_count: int | None = None
    member_count_year: int | None = None
    updated_at: datetime | None = None


class OrganizationNameRow(BaseModel):
    id: str
    organization_id: str
    name: str
    name_type: str = "display"
    normalized_name: str | None = None
    is_primary: bool = False


class OrganizationSportRow(BaseModel):
    organization_id: str
    sport_id: int
    is_primary: bool = False


class OrganizationLocationRow(BaseModel):
    id: str
    organization_id: str
    location_type: str = "primary"
    name: str | None = None
    municipality_code: str | None = None
    region_code: str | None = None
    postal_code: str | None = None
    address_street: str | None = None
    address_extra: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_primary: bool = False


class OrganizationTrainingFacilityRow(BaseModel):
    id: str
    organization_id: str
    name: str
    facility_type: str = "training"
    location_id: str | None = None
    description: str | None = None


class OrganizationActivityRow(BaseModel):
    """Kotikenttä / kotihalli – viitteet organization_locations-riveihin."""

    organization_id: str
    home_field_location_id: str | None = None
    home_hall_location_id: str | None = None
    updated_at: datetime | None = None


class OrganizationEmailRow(BaseModel):
    id: str
    organization_id: str
    email: str
    email_type: str = "general"
    is_primary: bool = False
    verified_at: datetime | None = None


class OrganizationPhoneRow(BaseModel):
    id: str
    organization_id: str
    phone: str
    phone_type: str = "general"
    is_primary: bool = False


class OrganizationWebsiteRow(BaseModel):
    id: str
    organization_id: str
    url: str
    website_type: str = "main"
    is_primary: bool = False


class OrganizationSocialAccountRow(BaseModel):
    id: str
    organization_id: str
    platform: str
    account_url: str | None = None
    account_handle: str | None = None
    is_primary: bool = False


class OrganizationContactPersonRow(BaseModel):
    id: str
    organization_id: str
    full_name: str
    role_title: str | None = None
    email_id: str | None = None
    phone_id: str | None = None
    is_primary: bool = False


class OrganizationExternalIdRow(BaseModel):
    id: str
    organization_id: str
    id_scheme: str
    source_id: str | None = None
    external_id: str


class OrganizationSourceRow(BaseModel):
    organization_id: str
    source_id: str
    observation_id: str | None = None
    external_id: str | None = None
    source_url: str | None = None
    is_primary: bool = False
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None


class ObservationRow(BaseModel):
    id: str
    source_id: str
    ingestion_run_id: str | None = None
    source_record_key: str | None = None
    source_url: str | None = None
    matched_organization_id: str | None = None
    match_status: str = "unmatched"
    match_confidence: str = "no_match"
    match_score: float | None = None
    match_reason: str | None = None
    collected_at: datetime | None = None
    raw_payload: str | None = None


class FieldProvenanceRow(BaseModel):
    id: str
    organization_id: str
    entity_table: str
    entity_id: str
    field_name: str
    source_id: str
    observation_id: str | None = None
    merged_at: datetime | None = None
