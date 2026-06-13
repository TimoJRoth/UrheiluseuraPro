# Tietokantaskeema – Master Database

Lopullinen **täysin normalisoitu** relaatiotietokantaskeema Suomen urheiluseuroille. Suunniteltu SQLite-kehitykseen ja PostgreSQL-tuotantoon.

> **Lähde totuudelle:** `db/schema.sql` (v1.2.0)  
> **Validointi:** [schema-validation.md](schema-validation.md)  
> **PostgreSQL:** `db/schema.postgresql.sql`

## Suunnitteluperiaatteet

1. **Ei listoja tekstikentissä** – jokainen laji, sähköposti, puhelin, sivu ja somekanava omalla rivillään
2. **M:N erillisissä liitostauluissa** – esim. `organization_sports`
3. **Indeksit suodattimille** – laji, kunta, maakunta, some-alusta
4. **Staging + master** – havainnot erillisessä kerroksessa ennen mergeä
5. **Provenienssi** – jokainen tieto jäljitettävissä lähteeseensä
6. **organization_profile** – 1:1 hakukiihdytin (lasketut liput, EI listoja) 100k+ org -suorituskyvylle

## ER-kaavio (yhteenveto)

```
regions ─────┐
             ├── municipalities
             │
sports ──────┼── organization_sports ─── organizations ─── organization_names
sport_aliases│                            │                organization_emails
             │                            │                organization_phones
             │                            │                organization_websites
             │                            │                organization_social_accounts
             │                            │                organization_locations
             │                            │                organization_contact_persons
             │                            │                organization_external_ids
             │                            └── organization_sources ─── sources
             │
observations ── observation_* (peilitaulut) ── merge ── organizations
```

---

## Taulut

### Referenssit

| Taulu | Avain | Kuvaus |
|-------|-------|--------|
| `regions` | `code` | Maakunnat (19 kpl) |
| `municipalities` | `code` | Kunnat, FK → regions |
| `sports` | `id` | Lajit, slug-haku (`jaakiekko`) |
| `sport_aliases` | `id` | Lajin synonyymit (`jääkiekko` → jaakiekko) |
| `sources` | `source_id` | Tietolähteet (synkronoitu sources.md) |

### Master: organizations + 1:N / M:N

| Taulu | Suhde | Sisältö |
|-------|-------|---------|
| `organizations` | 1 | Seuran ydin (ei nimeä, ei listoja) |
| `organization_profile` | 1:1 | Hakulippujen kiihdytin (has_email, is_multi_sport, …) |
| `organization_names` | 1:N | display, official, short, alias |
| `organization_sports` | M:N | Useita lajeja per seura |
| `organization_size` | 1:1 | Jäsenmäärät: total, junior, adult |
| `organization_training_facilities` | 1:N | Harjoituspaikat (rajaton) |
| `organization_activity` | 1:1 | Kotikenttä / kotihalli → location-viitteet |
| `organization_locations` | 1:N | Osoitteet + **latitude / longitude** per paikka |
| `organization_emails` | 1:N | Useita sähköposteja |
| `organization_phones` | 1:N | Useita puhelinnumeroita |
| `organization_websites` | 1:N | Useita verkkosivuja |
| `organization_social_accounts` | 1:N | Facebook, Instagram, … |
| `organization_contact_persons` | 1:N | Yhteyshenkilöt (FK email/phone) |
| `organization_external_ids` | 1:N | Suomisport, YTJ, lajiliitto |
| `organization_sources` | M:N | Provenienssi: mitkä lähteet yhdistivät |

### Staging: observations + peilitaulut

| Taulu | Kuvaus |
|-------|--------|
| `observations` | Yksi havainto yhdestä lähteestä |
| `observation_names` | Havainnon nimet |
| `observation_sports` | Havainnon lajit (sport_raw + sport_id) |
| `observation_locations` | Havainnon osoitteet |
| `observation_emails` | … |
| `observation_phones` | … |
| `observation_websites` | … |
| `observation_social_accounts` | … |
| `observation_contact_persons` | … |
| `observation_external_ids` | … |

### Audit

| Taulu | Kuvaus |
|-------|--------|
| `ingestion_runs` | Keruuajojen metadata |
| `field_provenance` | Kenttäkohtainen merge-historia |

---

## Kyselyesimerkit

Kaikki kyselyt: `db/queries/examples.sql`

### Laji

```sql
-- Kaikki jääkiekkoseurat
SELECT o.id, pn.name
FROM organizations o
JOIN v_organization_primary_name pn ON pn.organization_id = o.id
JOIN organization_sports os ON os.organization_id = o.id
JOIN sports s ON s.id = os.sport_id
WHERE s.slug = 'jaakiekko';
```

Vaihda `slug`: salibandy, jalkapallo, golf, voimistelu.

### Maantiede

```sql
-- Pirkanmaan seurat (maakunta)
WHERE m.region_code = '11'

-- Tampereen seurat (kunta)
WHERE ol.municipality_code = '837'

-- Helsingin seurat
WHERE ol.municipality_code = '091'
```

### Yhteystiedot

| Suodatin | Liitostaulu | Ehto |
|----------|-------------|------|
| Sähköposti | `organization_emails` | JOIN riittää |
| Verkkosivu | `organization_websites` | JOIN riittää |
| Facebook | `organization_social_accounts` | `platform = 'facebook'` |
| Instagram | `organization_social_accounts` | `platform = 'instagram'` |
| Yhteyshenkilö | `organization_contact_persons` | JOIN riittää |
| Puhelin | `organization_phones` | JOIN riittää |

### Yhdistelmä

```sql
-- Tampereen jääkiekkoseurat joilla on sähköposti
SELECT DISTINCT o.id, pn.name, oe.email
FROM organizations o
JOIN organization_sports os ON os.organization_id = o.id
JOIN sports s ON s.id = os.sport_id AND s.slug = 'jaakiekko'
JOIN organization_locations ol ON ol.organization_id = o.id
    AND ol.municipality_code = '837'
JOIN organization_emails oe ON oe.organization_id = o.id;
```

---

## Indeksit (suorituskyky)

Miljoonien rivien skaalassa kriittiset indeksit:

| Indeksi | Kysely |
|---------|--------|
| `organization_sports(sport_id, organization_id)` | Kaikki X-lajin seurat |
| `organization_locations(municipality_code, organization_id)` | Kaikki X-kunnan seurat |
| `organization_locations(region_code, organization_id)` | Kaikki X-maakunnan seurat |
| `organization_social_accounts(platform, organization_id)` | Some-suodattimet |
| `organization_names(normalized_name)` | Nimi-haku |
| `organizations(business_id)` | Y-tunnus-deduplikointi |

PostgreSQL-tuotannossa: `PARTITION` observations-taulua `source_id`:llä jos >10M riviä.

---

## Näkymät

| Näkymä | Kuvaus |
|--------|--------|
| `v_organization_primary_name` | Yksi päänimi per seura |
| `v_organization_summary` | Seura + päälaji + pääkunta + maakunta |

---

## PostgreSQL-muutokset (tuotanto)

| SQLite | PostgreSQL |
|--------|------------|
| `TEXT` UUID | `UUID` |
| `TEXT` datetime | `TIMESTAMPTZ` |
| `INTEGER` boolean | `BOOLEAN` |
| `TEXT` JSON | `JSONB` |
| `AUTOINCREMENT` | `SERIAL` / `GENERATED` |

Muutoin skeema on identtinen. Migraatiot: Alembic (tuleva).

---

## Tietovirta mergeen

```
1. Ingestori → observations + observation_* (staging)
2. Normalisointi → sport_raw → sport_id, municipality_raw → code
3. Deduplikointi → matched_organization_id
4. Merge:
   - Uusi org → INSERT organizations + INSERT organization_*
   - Olemassa → INSERT/UPDATE organization_* (prioriteetti)
   - INSERT organization_sources, field_provenance
5. Master-valmis → SQL-kyselyt
```

---

## Suhde Pydantic-malleihin

| Kerros | Malli | Käyttö |
|--------|-------|--------|
| Tietokanta | `*Row` (`models/relational/`) | SQL INSERT/SELECT |
| Staging (sovellus) | `ClubObservation` | Ingestorien ulostulo (siirtyy peilitauluihin) |
| Master (sovellus) | `Club` (legacy aggregate) | Vienti/API – rakennetaan JOINeista |

**Huom:** `Club`-aggregate-malli korvataan asteittain relaatiokerroksella. Totuuden lähde on aina SQL-skeema.

---

## Seuraavat askeleet

- [ ] Alembic-migraatiot
- [ ] Repository-kerros (`db/repository.py`)
- [ ] Kuntarekisterin täydellinen seed (309 kuntaa)
- [ ] Merge-engine kirjoittaa relaatiotauluihin
- [ ] PostgreSQL-yhteensopivuustestit

## Liittyvät tiedostot

- [db/schema.sql](../db/schema.sql)
- [db/seed/reference.sql](../db/seed/reference.sql)
- [db/queries/examples.sql](../db/queries/examples.sql)
- [data-model.md](data-model.md) – sovelluskerros ja deduplikointi
