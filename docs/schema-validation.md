# Skeeman validointi – vaatimusten täyttäminen

Tämä dokumentti varmistaa, että tietomalli tukee **Suomen kattavinta urheiluseurojen master-tietokantaa** – ei scraper-projektia.

> Skeema v1.2.0 | SQLite: `db/schema.sql` | PostgreSQL: `db/schema.postgresql.sql`

## Projektin lopullinen tavoite

| Vaatimus | Toteutus | Status |
|----------|----------|--------|
| Master-tietokanta (ei scraper) | `organizations` + child-taulut, staging erillään | ✅ |
| Useita lähteitä yhteen seuraan | `organization_sources` (M:N, rajaton) | ✅ |
| Täysin normalisoitu | Jokainen fakta omalla rivillään | ✅ |
| Ei JSON-listoja | `raw_payload` vain stagingissä (yksittäinen havainto) | ✅ |
| Ei pilkkulistoja | Kielletty skeemassa | ✅ |
| 100k+ org nopeat haut | `organization_profile` + partial indexit | ✅ |
| PostgreSQL tuotanto | `schema.postgresql.sql` | ✅ |

---

## Vaaditut haut → skeema → indeksi

| # | Haku | Taulu / näkymä | Indeksi | Esimerkki |
|---|------|----------------|---------|-----------|
| 1 | Kaikki seurat | `organizations` + `organization_profile` | PK | `examples.sql` #1 |
| 2 | Tietyn lajin seurat | `organization_sports` → `sports.slug` | `idx_org_sports_sport_org` | #2 |
| 3 | Tietyn kaupungin seurat | `organization_profile.primary_municipality_code` TAI `organization_locations` | `idx_profile_municipality`, `idx_org_locations_muni_org` | #3, B |
| 4 | Tietyn maakunnan seurat | `organization_profile.primary_region_code` TAI `organization_locations` + `municipalities` | `idx_profile_region`, `idx_org_locations_region_org` | #4, B |
| 5 | Monilajiseurat | `organization_profile.is_multi_sport` TAI `GROUP BY organization_sports` | `idx_profile_multi_sport` (partial) | #5 |
| 6 | Sähköposti | `organization_profile.has_email` | `idx_profile_has_email` (partial) | #6 |
| 7 | Verkkosivut | `organization_profile.has_website` | `idx_profile_has_website` (partial) | #7 |
| 8 | Facebook | `organization_profile.has_facebook` | `idx_profile_has_facebook` (partial) | #8 |
| 9 | Instagram | `organization_profile.has_instagram` | `idx_profile_has_instagram` (partial) | #9 |
| 10 | LinkedIn | `organization_profile.has_linkedin` | `idx_profile_has_linkedin` (partial) | #10 |
| 11 | Yhteyshenkilö | `organization_profile.has_contact_person` | `idx_profile_has_contact` (partial) | #11 |
| 12 | Puhelinnumero | `organization_profile.has_phone` | `idx_profile_has_phone` (partial) | #12 |

Kaikki esimerkit: [db/queries/examples.sql](../db/queries/examples.sql)

---

## Rajaton määrä per seura → omat taulut

| Data | Taulu | Rajoitus |
|------|-------|----------|
| Lajit | `organization_sports` | M:N, ei ylärajaa |
| Toimipaikat | `organization_locations` | 1:N |
| Sähköpostit | `organization_emails` | 1:N |
| Puhelinnumerot | `organization_phones` | 1:N |
| Verkkosivut | `organization_websites` | 1:N |
| Somekanavat | `organization_social_accounts` | 1:N (useita per alusta eri URL:lla) |
| Yhteyshenkilöt | `organization_contact_persons` | 1:N |
| Tietolähteet | `organization_sources` | M:N |
| Nimet/aliakset | `organization_names` | 1:N |
| Jäsenmäärät | `organization_size` | 1:1 |
| Harjoituspaikat | `organization_training_facilities` | 1:N |
| Kotikenttä / kotihalli | `organization_activity` → `organization_locations` | 1:1 viitteet |
| Koordinaatit | `organization_locations.latitude/longitude` | per toimipaikka |

**Ei sallittu:** `sports TEXT`, `emails TEXT`, `social JSON`, `sources TEXT`

---

## organization_profile – miksi?

`organization_profile` on **1:1 hakukiihdytin**, ei listadenormalisointi:

- Sisältää vain **laskureita ja boolean-lippuja** (has_email, sport_count)
- Päivitetään **merge-vaiheessa** kun child-taulut muuttuvat
- Mahdollistaa **partial index** -suodattimet: `WHERE has_email = 1`
- Arvio 100k org: profiilihaku ~5–20 ms vs. EXISTS-skannaus ~50–200 ms

Totuuden lähde pysyy aina child-tauluissa. Profiili on derivoitu näkymä tallennettuna.

---

## Suorituskykyarvio (100 000 organisaatiota)

| Kysely | Arvio | Mekanismi |
|--------|-------|-----------|
| Kaikki seurat | Index scan PK | `organizations` |
| Laji (jääkiekko ~400) | ~1 ms | `idx_org_sports_sport_org` |
| Kunta (Tampere ~1500) | ~2 ms | `idx_profile_municipality` |
| Maakunta (Pirkanmaa ~3000) | ~3 ms | `idx_profile_region` |
| has_email (~60k) | ~5 ms | Partial index |
| Monilajiseurat (~15k) | ~2 ms | Partial index |
| Yhdistelmä laji+kunta+email | ~1 ms | Bitmap AND indekseistä |

PostgreSQL: `EXPLAIN ANALYZE` ennen tuotantoa. `organization_profile` voidaan materialisoida tarvittaessa.

---

## PostgreSQL-tuotanto

| Ominaisuus | Toteutus |
|------------|----------|
| UUID-avaimet | `uuid_generate_v4()` |
| Aikaleimat | `TIMESTAMPTZ` |
| Boolean | native `BOOLEAN` |
| Staging JSON | `JSONB` |
| Nimi-haku | `pg_trgm` GIN-indeksi |
| Aikaindeksit | BRIN `updated_at` |
| Skaala >1M havaintoa | `observations` partition BY source_id |

Tiedosto: [db/schema.postgresql.sql](../db/schema.postgresql.sql)

---

## Hyväksyntächecklist

- [x] Kaikki 12 vaadittua hakutyyppiä tuettu
- [x] Rajaton 1:N/M:N kaikille toistuville kentille
- [x] Ei listoja tekstikentissä master-tauluissa
- [x] Indeksointi 100k+ org
- [x] PostgreSQL-skeema valmiina
- [x] SQLite kehitysskeema synkassa
- [x] Staging erillään masterista
- [x] Provenienssi (`organization_sources`, `field_provenance`)
- [ ] Repository-kerros (seuraava vaihe)
- [ ] Merge päivittää `organization_profile` (seuraava vaihe)

**Skeema on valmis hyväksyttäväksi ennen ensimmäistä ingestoria.**
