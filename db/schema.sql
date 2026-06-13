-- UrheiluseuraPro – Master Database schema (SQLite kehitys)
-- Versio: 1.2.0
--
-- TAVOITE: Suomen kattavin urheiluseurojen master-tietokanta (EI scraper-projekti)
-- Periaatteet:
--   - Täysin normalisoitu: jokainen fakta omalla rivillään
--   - Ei JSON-listoja, ei pilkuilla erotettuja kenttiä, ei listadenormalisointia
--   - organization_profile = 1:1 hakukiihdytin (laskettuja lippuja, EI listoja)
--   - PostgreSQL-tuotanto: db/schema.postgresql.sql

PRAGMA foreign_keys = ON;

-- =============================================================================
-- REFERENSSIT
-- =============================================================================

CREATE TABLE regions (
    code        TEXT PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE
);

CREATE TABLE municipalities (
    code        TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    region_code TEXT NOT NULL REFERENCES regions(code)
);

CREATE TABLE sports (
    id          INTEGER PRIMARY KEY,
    slug        TEXT NOT NULL UNIQUE,
    name_fi     TEXT NOT NULL,
    name_en     TEXT,
    parent_id   INTEGER REFERENCES sports(id)
);

CREATE TABLE sport_aliases (
    id          INTEGER PRIMARY KEY,
    sport_id    INTEGER NOT NULL REFERENCES sports(id) ON DELETE CASCADE,
    alias       TEXT NOT NULL,
    alias_normalized TEXT NOT NULL DEFAULT '',
    UNIQUE (sport_id, alias)
);

CREATE INDEX idx_sport_aliases_alias ON sport_aliases (alias_normalized);

CREATE TABLE sources (
    source_id       TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    category        TEXT NOT NULL,
    url             TEXT,
    merge_priority  INTEGER NOT NULL DEFAULT 50 CHECK (merge_priority BETWEEN 0 AND 100),
    priority        TEXT NOT NULL DEFAULT 'P3' CHECK (priority IN ('P1','P2','P3','P4')),
    active          INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- =============================================================================
-- MASTER: ORGANIZAATIOT
-- =============================================================================

CREATE TABLE organizations (
    id                  TEXT PRIMARY KEY,
    canonical_key       TEXT UNIQUE,
    business_id         TEXT UNIQUE,
    legal_form          TEXT NOT NULL DEFAULT 'tuntematon'
                        CHECK (legal_form IN ('ry','sr','oy','muu','tuntematon')),
    club_type           TEXT NOT NULL DEFAULT 'tuntematon'
                        CHECK (club_type IN (
                            'urheiluseura','monitoimiseura','liikuntaseura',
                            'nuorisoseura','liikuntakerho','yhdistys','muu','tuntematon'
                        )),
    status              TEXT NOT NULL DEFAULT 'tuntematon'
                        CHECK (status IN ('aktiivinen','passiivinen','lakkautettu','tuntematon')),
    founded_year        INTEGER CHECK (founded_year IS NULL OR (founded_year BETWEEN 1800 AND 2100)),
    needs_review        INTEGER NOT NULL DEFAULT 0 CHECK (needs_review IN (0, 1)),
    completeness_score  REAL NOT NULL DEFAULT 0.0 CHECK (completeness_score BETWEEN 0.0 AND 1.0),
    confidence_score    REAL NOT NULL DEFAULT 0.0 CHECK (confidence_score BETWEEN 0.0 AND 1.0),
    merge_version       INTEGER NOT NULL DEFAULT 1 CHECK (merge_version >= 1),
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    last_merged_at      TEXT,
    last_seen_at        TEXT
);

-- Hakuprofiili: 1:1 kiihdytin (lasketut laskurit/liput – EI listoja)
CREATE TABLE organization_profile (
    organization_id         TEXT PRIMARY KEY REFERENCES organizations(id) ON DELETE CASCADE,
    sport_count             INTEGER NOT NULL DEFAULT 0 CHECK (sport_count >= 0),
    is_multi_sport          INTEGER NOT NULL DEFAULT 0 CHECK (is_multi_sport IN (0, 1)),
    location_count          INTEGER NOT NULL DEFAULT 0 CHECK (location_count >= 0),
    email_count             INTEGER NOT NULL DEFAULT 0 CHECK (email_count >= 0),
    phone_count             INTEGER NOT NULL DEFAULT 0 CHECK (phone_count >= 0),
    website_count           INTEGER NOT NULL DEFAULT 0 CHECK (website_count >= 0),
    contact_person_count    INTEGER NOT NULL DEFAULT 0 CHECK (contact_person_count >= 0),
    social_account_count    INTEGER NOT NULL DEFAULT 0 CHECK (social_account_count >= 0),
    source_count            INTEGER NOT NULL DEFAULT 0 CHECK (source_count >= 0),
    has_email               INTEGER NOT NULL DEFAULT 0 CHECK (has_email IN (0, 1)),
    has_website             INTEGER NOT NULL DEFAULT 0 CHECK (has_website IN (0, 1)),
    has_phone               INTEGER NOT NULL DEFAULT 0 CHECK (has_phone IN (0, 1)),
    has_contact_person      INTEGER NOT NULL DEFAULT 0 CHECK (has_contact_person IN (0, 1)),
    has_facebook            INTEGER NOT NULL DEFAULT 0 CHECK (has_facebook IN (0, 1)),
    has_instagram           INTEGER NOT NULL DEFAULT 0 CHECK (has_instagram IN (0, 1)),
    has_linkedin            INTEGER NOT NULL DEFAULT 0 CHECK (has_linkedin IN (0, 1)),
    has_member_count        INTEGER NOT NULL DEFAULT 0 CHECK (has_member_count IN (0, 1)),
    has_home_field          INTEGER NOT NULL DEFAULT 0 CHECK (has_home_field IN (0, 1)),
    has_home_hall           INTEGER NOT NULL DEFAULT 0 CHECK (has_home_hall IN (0, 1)),
    training_facility_count INTEGER NOT NULL DEFAULT 0 CHECK (training_facility_count >= 0),
    primary_municipality_code TEXT REFERENCES municipalities(code),
    primary_region_code     TEXT REFERENCES regions(code),
    primary_latitude        REAL,
    primary_longitude       REAL,
    profile_updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Jäsenmäärät (1:1 – erillinen ryhmä organization_size)
CREATE TABLE organization_size (
    organization_id         TEXT PRIMARY KEY REFERENCES organizations(id) ON DELETE CASCADE,
    member_count            INTEGER CHECK (member_count IS NULL OR member_count >= 0),
    junior_member_count     INTEGER CHECK (junior_member_count IS NULL OR junior_member_count >= 0),
    adult_member_count      INTEGER CHECK (adult_member_count IS NULL OR adult_member_count >= 0),
    member_count_year       INTEGER CHECK (member_count_year IS NULL OR (member_count_year BETWEEN 1900 AND 2100)),
    updated_at              TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE organization_names (
    id                  TEXT PRIMARY KEY,
    organization_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name                TEXT NOT NULL,
    name_type           TEXT NOT NULL DEFAULT 'display'
                        CHECK (name_type IN ('display','official','short','alias')),
    normalized_name     TEXT,
    is_primary          INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    UNIQUE (organization_id, name, name_type)
);

CREATE TABLE organization_sports (
    organization_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    sport_id            INTEGER NOT NULL REFERENCES sports(id),
    is_primary          INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    PRIMARY KEY (organization_id, sport_id)
);

CREATE TABLE organization_locations (
    id                  TEXT PRIMARY KEY,
    organization_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    location_type       TEXT NOT NULL DEFAULT 'primary'
                        CHECK (location_type IN (
                            'primary','venue','postal','training',
                            'home_field','home_hall','other'
                        )),
    name                TEXT,
    municipality_code   TEXT REFERENCES municipalities(code),
    region_code         TEXT REFERENCES regions(code),
    postal_code         TEXT,
    address_street      TEXT,
    address_extra       TEXT,
    latitude            REAL CHECK (latitude IS NULL OR (latitude BETWEEN -90.0 AND 90.0)),
    longitude           REAL CHECK (longitude IS NULL OR (longitude BETWEEN -180.0 AND 180.0)),
    is_primary          INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1))
);

-- Harjoituspaikat / liikuntatilat (1:N – rajaton määrä)
CREATE TABLE organization_training_facilities (
    id                  TEXT PRIMARY KEY,
    organization_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name                TEXT NOT NULL,
    facility_type       TEXT NOT NULL DEFAULT 'training'
                        CHECK (facility_type IN ('training','gym','ice_rink','field','hall','other')),
    location_id         TEXT REFERENCES organization_locations(id) ON DELETE SET NULL,
    description         TEXT,
    UNIQUE (organization_id, name)
);

-- Kotikenttä / kotihalli (1:1 viitteet location-riveihin)
CREATE TABLE organization_activity (
    organization_id         TEXT PRIMARY KEY REFERENCES organizations(id) ON DELETE CASCADE,
    home_field_location_id  TEXT REFERENCES organization_locations(id) ON DELETE SET NULL,
    home_hall_location_id   TEXT REFERENCES organization_locations(id) ON DELETE SET NULL,
    updated_at              TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE organization_emails (
    id                  TEXT PRIMARY KEY,
    organization_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email               TEXT NOT NULL,
    email_type          TEXT NOT NULL DEFAULT 'general'
                        CHECK (email_type IN ('general','contact','info','billing','other')),
    is_primary          INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    verified_at         TEXT,
    UNIQUE (organization_id, email)
);

CREATE TABLE organization_phones (
    id                  TEXT PRIMARY KEY,
    organization_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    phone               TEXT NOT NULL,
    phone_type          TEXT NOT NULL DEFAULT 'general'
                        CHECK (phone_type IN ('general','mobile','office','fax','other')),
    is_primary          INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    UNIQUE (organization_id, phone)
);

CREATE TABLE organization_websites (
    id                  TEXT PRIMARY KEY,
    organization_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    url                 TEXT NOT NULL,
    website_type        TEXT NOT NULL DEFAULT 'main'
                        CHECK (website_type IN ('main','register','booking','wiki','other')),
    is_primary          INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    UNIQUE (organization_id, url)
);

CREATE TABLE organization_social_accounts (
    id                  TEXT PRIMARY KEY,
    organization_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    platform            TEXT NOT NULL
                        CHECK (platform IN (
                            'facebook','instagram','twitter','linkedin',
                            'youtube','tiktok','other'
                        )),
    account_url         TEXT NOT NULL DEFAULT '',
    account_handle      TEXT,
    is_primary          INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    UNIQUE (organization_id, platform, account_url)
);

CREATE TABLE organization_contact_persons (
    id                  TEXT PRIMARY KEY,
    organization_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    full_name           TEXT NOT NULL,
    role_title          TEXT,
    email_id            TEXT REFERENCES organization_emails(id) ON DELETE SET NULL,
    phone_id            TEXT REFERENCES organization_phones(id) ON DELETE SET NULL,
    is_primary          INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1))
);

CREATE TABLE organization_external_ids (
    id                  TEXT PRIMARY KEY,
    organization_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    id_scheme           TEXT NOT NULL,
    source_id           TEXT REFERENCES sources(source_id),
    external_id         TEXT NOT NULL,
    UNIQUE (id_scheme, source_id, external_id)
);

CREATE TABLE organization_sources (
    organization_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    source_id           TEXT NOT NULL REFERENCES sources(source_id),
    observation_id      TEXT,
    external_id         TEXT,
    source_url          TEXT,
    is_primary          INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    first_seen_at       TEXT NOT NULL DEFAULT (datetime('now')),
    last_seen_at        TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (organization_id, source_id)
);

-- =============================================================================
-- STAGING
-- =============================================================================

CREATE TABLE ingestion_runs (
    run_id              TEXT PRIMARY KEY,
    source_id           TEXT NOT NULL REFERENCES sources(source_id),
    started_at          TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at         TEXT,
    status              TEXT NOT NULL DEFAULT 'running'
                        CHECK (status IN ('running','success','failed','partial')),
    records_fetched     INTEGER NOT NULL DEFAULT 0,
    records_matched     INTEGER NOT NULL DEFAULT 0,
    records_new         INTEGER NOT NULL DEFAULT 0,
    records_needs_review INTEGER NOT NULL DEFAULT 0,
    errors              TEXT
);

CREATE TABLE observations (
    id                      TEXT PRIMARY KEY,
    source_id               TEXT NOT NULL REFERENCES sources(source_id),
    ingestion_run_id        TEXT REFERENCES ingestion_runs(run_id),
    source_record_key       TEXT,
    source_url              TEXT,
    matched_organization_id TEXT REFERENCES organizations(id),
    match_status            TEXT NOT NULL DEFAULT 'unmatched',
    match_confidence        TEXT NOT NULL DEFAULT 'no_match',
    match_score             REAL,
    match_reason            TEXT,
    collected_at            TEXT NOT NULL DEFAULT (datetime('now')),
    raw_payload             TEXT
);

CREATE TABLE observation_names (
    id                  TEXT PRIMARY KEY,
    observation_id      TEXT NOT NULL REFERENCES observations(id) ON DELETE CASCADE,
    name                TEXT NOT NULL,
    name_type           TEXT NOT NULL DEFAULT 'display',
    normalized_name     TEXT
);

CREATE TABLE observation_sports (
    observation_id      TEXT NOT NULL REFERENCES observations(id) ON DELETE CASCADE,
    sport_id            INTEGER REFERENCES sports(id),
    sport_raw           TEXT NOT NULL DEFAULT '',
    is_primary          INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    PRIMARY KEY (observation_id, sport_id, sport_raw)
);

CREATE TABLE observation_locations (
    id                  TEXT PRIMARY KEY,
    observation_id      TEXT NOT NULL REFERENCES observations(id) ON DELETE CASCADE,
    location_type       TEXT NOT NULL DEFAULT 'primary',
    name                TEXT,
    municipality_code   TEXT,
    municipality_raw    TEXT,
    region_code         TEXT,
    postal_code         TEXT,
    address_street      TEXT,
    address_extra       TEXT,
    latitude            REAL,
    longitude           REAL
);

CREATE TABLE observation_size (
    observation_id          TEXT PRIMARY KEY REFERENCES observations(id) ON DELETE CASCADE,
    member_count            INTEGER,
    junior_member_count     INTEGER,
    adult_member_count      INTEGER,
    member_count_year       INTEGER
);

CREATE TABLE observation_training_facilities (
    id                  TEXT PRIMARY KEY,
    observation_id      TEXT NOT NULL REFERENCES observations(id) ON DELETE CASCADE,
    name                TEXT NOT NULL,
    facility_type       TEXT NOT NULL DEFAULT 'training',
    description         TEXT
);

CREATE TABLE observation_activity (
    observation_id              TEXT PRIMARY KEY REFERENCES observations(id) ON DELETE CASCADE,
    home_field_name             TEXT,
    home_hall_name              TEXT
);

CREATE TABLE observation_emails (
    id                  TEXT PRIMARY KEY,
    observation_id      TEXT NOT NULL REFERENCES observations(id) ON DELETE CASCADE,
    email               TEXT NOT NULL,
    email_type          TEXT NOT NULL DEFAULT 'general'
);

CREATE TABLE observation_phones (
    id                  TEXT PRIMARY KEY,
    observation_id      TEXT NOT NULL REFERENCES observations(id) ON DELETE CASCADE,
    phone               TEXT NOT NULL,
    phone_type          TEXT NOT NULL DEFAULT 'general'
);

CREATE TABLE observation_websites (
    id                  TEXT PRIMARY KEY,
    observation_id      TEXT NOT NULL REFERENCES observations(id) ON DELETE CASCADE,
    url                 TEXT NOT NULL,
    website_type        TEXT NOT NULL DEFAULT 'main'
);

CREATE TABLE observation_social_accounts (
    id                  TEXT PRIMARY KEY,
    observation_id      TEXT NOT NULL REFERENCES observations(id) ON DELETE CASCADE,
    platform            TEXT NOT NULL,
    account_url         TEXT NOT NULL DEFAULT '',
    account_handle      TEXT
);

CREATE TABLE observation_contact_persons (
    id                  TEXT PRIMARY KEY,
    observation_id      TEXT NOT NULL REFERENCES observations(id) ON DELETE CASCADE,
    full_name           TEXT NOT NULL,
    role_title          TEXT,
    email               TEXT,
    phone               TEXT
);

CREATE TABLE observation_external_ids (
    id                  TEXT PRIMARY KEY,
    observation_id      TEXT NOT NULL REFERENCES observations(id) ON DELETE CASCADE,
    id_scheme           TEXT NOT NULL,
    external_id         TEXT NOT NULL
);

CREATE TABLE field_provenance (
    id                  TEXT PRIMARY KEY,
    organization_id     TEXT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    entity_table        TEXT NOT NULL,
    entity_id           TEXT NOT NULL,
    field_name          TEXT NOT NULL,
    source_id           TEXT NOT NULL REFERENCES sources(source_id),
    observation_id      TEXT REFERENCES observations(id),
    merged_at           TEXT NOT NULL DEFAULT (datetime('now'))
);

-- =============================================================================
-- INDEKSIT – 100 000+ organisaatiota
-- =============================================================================

CREATE INDEX idx_organizations_status          ON organizations (status);
CREATE INDEX idx_organizations_needs_review      ON organizations (needs_review) WHERE needs_review = 1;
CREATE INDEX idx_organizations_updated           ON organizations (updated_at);

CREATE INDEX idx_profile_multi_sport             ON organization_profile (is_multi_sport) WHERE is_multi_sport = 1;
CREATE INDEX idx_profile_has_email               ON organization_profile (has_email) WHERE has_email = 1;
CREATE INDEX idx_profile_has_website             ON organization_profile (has_website) WHERE has_website = 1;
CREATE INDEX idx_profile_has_phone               ON organization_profile (has_phone) WHERE has_phone = 1;
CREATE INDEX idx_profile_has_contact             ON organization_profile (has_contact_person) WHERE has_contact_person = 1;
CREATE INDEX idx_profile_has_facebook            ON organization_profile (has_facebook) WHERE has_facebook = 1;
CREATE INDEX idx_profile_has_instagram           ON organization_profile (has_instagram) WHERE has_instagram = 1;
CREATE INDEX idx_profile_has_linkedin            ON organization_profile (has_linkedin) WHERE has_linkedin = 1;
CREATE INDEX idx_profile_has_member_count        ON organization_profile (has_member_count) WHERE has_member_count = 1;
CREATE INDEX idx_profile_has_home_field          ON organization_profile (has_home_field) WHERE has_home_field = 1;
CREATE INDEX idx_profile_has_home_hall           ON organization_profile (has_home_hall) WHERE has_home_hall = 1;
CREATE INDEX idx_profile_municipality            ON organization_profile (primary_municipality_code);
CREATE INDEX idx_profile_region                  ON organization_profile (primary_region_code);
CREATE INDEX idx_profile_geo                     ON organization_profile (primary_latitude, primary_longitude);

CREATE INDEX idx_org_size_member_count           ON organization_size (member_count) WHERE member_count IS NOT NULL;
CREATE INDEX idx_org_training_facilities_org     ON organization_training_facilities (organization_id);
CREATE INDEX idx_org_activity_home_field         ON organization_activity (home_field_location_id);
CREATE INDEX idx_org_activity_home_hall          ON organization_activity (home_hall_location_id);

CREATE INDEX idx_org_sports_sport_id             ON organization_sports (sport_id);
CREATE INDEX idx_org_sports_org                  ON organization_sports (organization_id);
CREATE INDEX idx_org_sports_sport_org            ON organization_sports (sport_id, organization_id);

CREATE INDEX idx_org_locations_org               ON organization_locations (organization_id);
CREATE INDEX idx_org_locations_municipality      ON organization_locations (municipality_code);
CREATE INDEX idx_org_locations_region            ON organization_locations (region_code);
CREATE INDEX idx_org_locations_muni_org          ON organization_locations (municipality_code, organization_id);
CREATE INDEX idx_org_locations_region_org        ON organization_locations (region_code, organization_id);
CREATE INDEX idx_org_locations_type              ON organization_locations (location_type);
CREATE INDEX idx_org_locations_type_org          ON organization_locations (location_type, organization_id);
CREATE INDEX idx_org_locations_lat_lon           ON organization_locations (latitude, longitude)
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL;

CREATE INDEX idx_org_emails_org                  ON organization_emails (organization_id);
CREATE INDEX idx_org_phones_org                  ON organization_phones (organization_id);
CREATE INDEX idx_org_websites_org                ON organization_websites (organization_id);
CREATE INDEX idx_org_contacts_org                ON organization_contact_persons (organization_id);
CREATE INDEX idx_org_social_org                  ON organization_social_accounts (organization_id);
CREATE INDEX idx_org_social_platform             ON organization_social_accounts (platform);
CREATE INDEX idx_org_social_platform_org         ON organization_social_accounts (platform, organization_id);

CREATE INDEX idx_org_names_org                   ON organization_names (organization_id);
CREATE INDEX idx_org_names_normalized            ON organization_names (normalized_name);
CREATE UNIQUE INDEX idx_org_names_one_primary    ON organization_names (organization_id) WHERE is_primary = 1;

CREATE INDEX idx_organizations_business_id       ON organizations (business_id);
CREATE INDEX idx_organizations_canonical           ON organizations (canonical_key);
CREATE INDEX idx_org_external_ids_org            ON organization_external_ids (organization_id);
CREATE INDEX idx_org_external_ids_scheme         ON organization_external_ids (id_scheme, external_id);
CREATE INDEX idx_org_sources_org                 ON organization_sources (organization_id);
CREATE INDEX idx_org_sources_source              ON organization_sources (source_id);

CREATE INDEX idx_observations_source             ON observations (source_id);
CREATE INDEX idx_observations_matched            ON observations (matched_organization_id);
CREATE INDEX idx_observations_status             ON observations (match_status);
CREATE INDEX idx_municipalities_region           ON municipalities (region_code);
CREATE INDEX idx_sports_slug                     ON sports (slug);

-- =============================================================================
-- NÄKYMÄT
-- =============================================================================

CREATE VIEW v_organization_primary_name AS
SELECT organization_id, name, normalized_name
FROM organization_names WHERE is_primary = 1;

CREATE VIEW v_organization_summary AS
SELECT
    o.id, pn.name,
    p.sport_count, p.is_multi_sport,
    p.has_email, p.has_website, p.has_phone, p.has_contact_person,
    p.has_facebook, p.has_instagram, p.has_linkedin,
    p.has_member_count, p.has_home_field, p.has_home_hall,
    p.training_facility_count,
    sz.member_count, sz.junior_member_count, sz.adult_member_count, sz.member_count_year,
    s.slug AS primary_sport_slug, s.name_fi AS primary_sport_name,
    COALESCE(p.primary_municipality_code, ol.municipality_code) AS municipality_code,
    m.name AS municipality_name,
    COALESCE(p.primary_region_code, r.code) AS region_code,
    r.name AS region_name,
    COALESCE(p.primary_latitude, ol.latitude) AS latitude,
    COALESCE(p.primary_longitude, ol.longitude) AS longitude,
    o.status, o.business_id, o.completeness_score, o.needs_review, p.source_count
FROM organizations o
JOIN organization_profile p ON p.organization_id = o.id
LEFT JOIN organization_size sz ON sz.organization_id = o.id
LEFT JOIN v_organization_primary_name pn ON pn.organization_id = o.id
LEFT JOIN organization_sports os ON os.organization_id = o.id AND os.is_primary = 1
LEFT JOIN sports s ON s.id = os.sport_id
LEFT JOIN organization_locations ol ON ol.organization_id = o.id AND ol.is_primary = 1
LEFT JOIN municipalities m ON m.code = COALESCE(p.primary_municipality_code, ol.municipality_code)
LEFT JOIN regions r ON r.code = COALESCE(p.primary_region_code, ol.region_code, m.region_code);
