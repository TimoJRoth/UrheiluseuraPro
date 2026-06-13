-- UrheiluseuraPro – PostgreSQL tuotantoskeema v1.2.0
-- Suomen kattavin urheiluseurojen master-tietokanta

BEGIN;

CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE regions (
    code CHAR(2) PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE municipalities (
    code CHAR(3) PRIMARY KEY,
    name TEXT NOT NULL,
    region_code CHAR(2) NOT NULL REFERENCES regions(code)
);

CREATE TABLE sports (
    id SERIAL PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name_fi TEXT NOT NULL,
    name_en TEXT,
    parent_id INTEGER REFERENCES sports(id)
);

CREATE TABLE sport_aliases (
    id SERIAL PRIMARY KEY,
    sport_id INTEGER NOT NULL REFERENCES sports(id) ON DELETE CASCADE,
    alias TEXT NOT NULL,
    alias_normalized TEXT NOT NULL GENERATED ALWAYS AS (lower(trim(alias))) STORED,
    UNIQUE (sport_id, alias)
);

CREATE INDEX idx_sport_aliases_alias ON sport_aliases (alias_normalized);

CREATE TABLE sources (
    source_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    url TEXT,
    merge_priority SMALLINT NOT NULL DEFAULT 50 CHECK (merge_priority BETWEEN 0 AND 100),
    priority TEXT NOT NULL DEFAULT 'P3' CHECK (priority IN ('P1','P2','P3','P4')),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    canonical_key TEXT UNIQUE,
    business_id TEXT UNIQUE,
    legal_form TEXT NOT NULL DEFAULT 'tuntematon',
    club_type TEXT NOT NULL DEFAULT 'tuntematon',
    status TEXT NOT NULL DEFAULT 'tuntematon',
    founded_year SMALLINT,
    needs_review BOOLEAN NOT NULL DEFAULT FALSE,
    completeness_score REAL NOT NULL DEFAULT 0.0,
    confidence_score REAL NOT NULL DEFAULT 0.0,
    merge_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_merged_at TIMESTAMPTZ,
    last_seen_at TIMESTAMPTZ
);

CREATE TABLE organization_profile (
    organization_id UUID PRIMARY KEY REFERENCES organizations(id) ON DELETE CASCADE,
    sport_count INTEGER NOT NULL DEFAULT 0,
    is_multi_sport BOOLEAN NOT NULL DEFAULT FALSE,
    location_count INTEGER NOT NULL DEFAULT 0,
    email_count INTEGER NOT NULL DEFAULT 0,
    phone_count INTEGER NOT NULL DEFAULT 0,
    website_count INTEGER NOT NULL DEFAULT 0,
    contact_person_count INTEGER NOT NULL DEFAULT 0,
    social_account_count INTEGER NOT NULL DEFAULT 0,
    source_count INTEGER NOT NULL DEFAULT 0,
    has_email BOOLEAN NOT NULL DEFAULT FALSE,
    has_website BOOLEAN NOT NULL DEFAULT FALSE,
    has_phone BOOLEAN NOT NULL DEFAULT FALSE,
    has_contact_person BOOLEAN NOT NULL DEFAULT FALSE,
    has_facebook BOOLEAN NOT NULL DEFAULT FALSE,
    has_instagram BOOLEAN NOT NULL DEFAULT FALSE,
    has_linkedin BOOLEAN NOT NULL DEFAULT FALSE,
    has_member_count BOOLEAN NOT NULL DEFAULT FALSE,
    has_home_field BOOLEAN NOT NULL DEFAULT FALSE,
    has_home_hall BOOLEAN NOT NULL DEFAULT FALSE,
    training_facility_count INTEGER NOT NULL DEFAULT 0,
    primary_municipality_code CHAR(3) REFERENCES municipalities(code),
    primary_region_code CHAR(2) REFERENCES regions(code),
    primary_latitude DOUBLE PRECISION,
    primary_longitude DOUBLE PRECISION,
    profile_updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE organization_size (
    organization_id UUID PRIMARY KEY REFERENCES organizations(id) ON DELETE CASCADE,
    member_count INTEGER CHECK (member_count IS NULL OR member_count >= 0),
    junior_member_count INTEGER CHECK (junior_member_count IS NULL OR junior_member_count >= 0),
    adult_member_count INTEGER CHECK (adult_member_count IS NULL OR adult_member_count >= 0),
    member_count_year SMALLINT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE organization_names (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    name_type TEXT NOT NULL DEFAULT 'display',
    normalized_name TEXT,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (organization_id, name, name_type)
);

CREATE TABLE organization_sports (
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    sport_id INTEGER NOT NULL REFERENCES sports(id),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (organization_id, sport_id)
);

CREATE TABLE organization_locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    location_type TEXT NOT NULL DEFAULT 'primary',
    name TEXT,
    municipality_code CHAR(3) REFERENCES municipalities(code),
    region_code CHAR(2) REFERENCES regions(code),
    postal_code TEXT,
    address_street TEXT,
    address_extra TEXT,
    latitude DOUBLE PRECISION CHECK (latitude IS NULL OR (latitude BETWEEN -90 AND 90)),
    longitude DOUBLE PRECISION CHECK (longitude IS NULL OR (longitude BETWEEN -180 AND 180)),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE organization_training_facilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    facility_type TEXT NOT NULL DEFAULT 'training',
    location_id UUID REFERENCES organization_locations(id) ON DELETE SET NULL,
    description TEXT,
    UNIQUE (organization_id, name)
);

CREATE TABLE organization_activity (
    organization_id UUID PRIMARY KEY REFERENCES organizations(id) ON DELETE CASCADE,
    home_field_location_id UUID REFERENCES organization_locations(id) ON DELETE SET NULL,
    home_hall_location_id UUID REFERENCES organization_locations(id) ON DELETE SET NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE organization_emails (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    email_type TEXT NOT NULL DEFAULT 'general',
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMPTZ,
    UNIQUE (organization_id, email)
);

CREATE TABLE organization_phones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    phone TEXT NOT NULL,
    phone_type TEXT NOT NULL DEFAULT 'general',
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (organization_id, phone)
);

CREATE TABLE organization_websites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    website_type TEXT NOT NULL DEFAULT 'main',
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (organization_id, url)
);

CREATE TABLE organization_social_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    account_url TEXT NOT NULL DEFAULT '',
    account_handle TEXT,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (organization_id, platform, account_url)
);

CREATE TABLE organization_contact_persons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    role_title TEXT,
    email_id UUID REFERENCES organization_emails(id) ON DELETE SET NULL,
    phone_id UUID REFERENCES organization_phones(id) ON DELETE SET NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE organization_external_ids (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    id_scheme TEXT NOT NULL,
    source_id TEXT REFERENCES sources(source_id),
    external_id TEXT NOT NULL,
    UNIQUE (id_scheme, source_id, external_id)
);

CREATE TABLE organization_sources (
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    observation_id UUID,
    external_id TEXT,
    source_url TEXT,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (organization_id, source_id)
);

CREATE TABLE ingestion_runs (
    run_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'running',
    records_fetched INTEGER NOT NULL DEFAULT 0,
    records_matched INTEGER NOT NULL DEFAULT 0,
    records_new INTEGER NOT NULL DEFAULT 0,
    records_needs_review INTEGER NOT NULL DEFAULT 0,
    errors JSONB
);

CREATE TABLE observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    ingestion_run_id UUID REFERENCES ingestion_runs(run_id),
    source_record_key TEXT,
    source_url TEXT,
    matched_organization_id UUID REFERENCES organizations(id),
    match_status TEXT NOT NULL DEFAULT 'unmatched',
    match_confidence TEXT NOT NULL DEFAULT 'no_match',
    match_score REAL,
    match_reason TEXT,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    raw_payload JSONB
);

CREATE TABLE field_provenance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    entity_table TEXT NOT NULL,
    entity_id UUID NOT NULL,
    field_name TEXT NOT NULL,
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    observation_id UUID,
    merged_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indeksit 100k–1M org
CREATE INDEX idx_profile_multi_sport ON organization_profile (organization_id) WHERE is_multi_sport = TRUE;
CREATE INDEX idx_profile_has_email ON organization_profile (organization_id) WHERE has_email = TRUE;
CREATE INDEX idx_profile_has_website ON organization_profile (organization_id) WHERE has_website = TRUE;
CREATE INDEX idx_profile_has_phone ON organization_profile (organization_id) WHERE has_phone = TRUE;
CREATE INDEX idx_profile_has_contact ON organization_profile (organization_id) WHERE has_contact_person = TRUE;
CREATE INDEX idx_profile_has_facebook ON organization_profile (organization_id) WHERE has_facebook = TRUE;
CREATE INDEX idx_profile_has_instagram ON organization_profile (organization_id) WHERE has_instagram = TRUE;
CREATE INDEX idx_profile_has_linkedin ON organization_profile (organization_id) WHERE has_linkedin = TRUE;
CREATE INDEX idx_profile_has_member_count ON organization_profile (organization_id) WHERE has_member_count = TRUE;
CREATE INDEX idx_profile_has_home_field ON organization_profile (organization_id) WHERE has_home_field = TRUE;
CREATE INDEX idx_profile_has_home_hall ON organization_profile (organization_id) WHERE has_home_hall = TRUE;
CREATE INDEX idx_profile_geo ON organization_profile (primary_latitude, primary_longitude)
    WHERE primary_latitude IS NOT NULL AND primary_longitude IS NOT NULL;
CREATE INDEX idx_org_locations_lat_lon ON organization_locations (latitude, longitude)
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL;
CREATE INDEX idx_org_locations_type_org ON organization_locations (location_type, organization_id);
CREATE INDEX idx_org_training_facilities_org ON organization_training_facilities (organization_id);
CREATE INDEX idx_org_size_member_count ON organization_size (member_count) WHERE member_count IS NOT NULL;
CREATE INDEX idx_profile_municipality ON organization_profile (primary_municipality_code);
CREATE INDEX idx_profile_region ON organization_profile (primary_region_code);
CREATE INDEX idx_org_sports_sport_org ON organization_sports (sport_id, organization_id);
CREATE INDEX idx_org_locations_muni_org ON organization_locations (municipality_code, organization_id);
CREATE INDEX idx_org_locations_region_org ON organization_locations (region_code, organization_id);
CREATE INDEX idx_org_social_platform_org ON organization_social_accounts (platform, organization_id);
CREATE INDEX idx_org_names_normalized_trgm ON organization_names USING gin (normalized_name gin_trgm_ops);
CREATE UNIQUE INDEX idx_org_names_one_primary ON organization_names (organization_id) WHERE is_primary = TRUE;
CREATE INDEX idx_organizations_business_id ON organizations (business_id);
CREATE INDEX idx_organizations_updated_brin ON organizations USING brin (updated_at);

CREATE VIEW v_organization_summary AS
SELECT o.id, pn.name, p.is_multi_sport, p.has_email, p.has_website, p.has_phone,
       p.has_contact_person, p.has_facebook, p.has_instagram, p.has_linkedin,
       s.slug AS primary_sport_slug,
       COALESCE(p.primary_municipality_code, ol.municipality_code) AS municipality_code,
       COALESCE(p.primary_region_code, m.region_code) AS region_code
FROM organizations o
JOIN organization_profile p ON p.organization_id = o.id
LEFT JOIN organization_names pn ON pn.organization_id = o.id AND pn.is_primary = TRUE
LEFT JOIN organization_sports os ON os.organization_id = o.id AND os.is_primary = TRUE
LEFT JOIN sports s ON s.id = os.sport_id
LEFT JOIN organization_locations ol ON ol.organization_id = o.id AND ol.is_primary = TRUE
LEFT JOIN municipalities m ON m.code = COALESCE(p.primary_municipality_code, ol.municipality_code);

COMMIT;
