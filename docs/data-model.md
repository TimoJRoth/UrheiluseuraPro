# Tietomalli – Master Database

> **Lopullinen totuuden lähde:** relaatiotietokantaskeema → [database-schema.md](database-schema.md) ja [db/schema.sql](../db/schema.sql)

UrheiluseuraPro:n sovelluskerros: normalisointi, deduplikointi ja merge ennen/päivittäessä SQL-tietokantaa.

## Kerrokset

| Kerros | Toteutus | Rooli |
|--------|----------|-------|
| **SQL (totuus)** | `db/schema.sql` | Normalisoitu tallennus, nopeat kyselyt |
| **Rivimallit** | `models/relational/*Row` | Python ↔ SQL |
| **Staging** | `ClubObservation` + `observation_*` | Ingestorien ulostulo |
| **Merge** | `merge/`, `deduplication/` | Yhdistäminen masteriin |
| **Aggregate (väliaikainen)** | `Club` | Vienti/API – rakennetaan JOINeista |

---

## Relaatiomalli (yhteenveto)

**Ei listoja tekstikentissä.** Esimerkkejä:

| Tarve | Väärin | Oikein |
|-------|--------|--------|
| 3 lajia | `sports = "jääkiekko; salibandy"` | 3 riviä `organization_sports` |
| 2 sähköpostia | `email_secondary` | 2 riviä `organization_emails` |
| 2 toimipaikkaa | `address` + `address2` | 2 riviä `organization_locations` |
| Facebook + Instagram | `social = "fb, ig"` | 2 riviä `organization_social_accounts` |

Katso täydellinen skeema: [database-schema.md](database-schema.md)

---

## Club – master-tietue (golden record)

Tiedosto: `src/urheiluseurapro/models/club.py`

### Tunnisteet

| Kenttä | Tyyppi | Kuvaus |
|--------|--------|--------|
| `id` | UUID | Master-tietueen pääavain |
| `canonical_key` | str | Deterministinen avain deduplikointiin |

### identity – nimi ja identiteetti

| Kenttä | Kuvaus |
|--------|--------|
| `name` | Näyttönimi (paras saatavilla oleva) |
| `name_official` | PRH/rekisterin virallinen nimi |
| `name_short` | Lyhenne (esim. TuPy) |
| `name_normalized` | Normalisoitu nimi matchingiin |
| `aliases` | Vaihtoehtoiset nimet eri lähteistä |

### sports – lajit

| Kenttä | Kuvaus |
|--------|--------|
| `sports` | Kaikki lajit listana |
| `sport_codes` | Standardoidut lajikoodit (tuleva) |
| `primary_sport` | Päälaji |
| `is_multi_sport` | Monitoimiseura |

### legal – rekisteri

| Kenttä | Kuvaus |
|--------|--------|
| `business_id` | Y-tunnus |
| `prh_registration_number` | PRH-numero |
| `registration_date` | Rekisteröintipäivä |
| `legal_form` | ry / oy / muu |
| `club_type` | urheiluseura / liikuntakerho / … |

### location – sijainti

| Kenttä | Kuvaus |
|--------|--------|
| `municipality` | Kunta |
| `municipality_code` | Kuntanumero |
| `region` | Maakunta |
| `postal_code` | Postinumero |
| `address_street` | Katuosoite |
| `address_full` | Koko osoite |
| `latitude`, `longitude` | Koordinaatit (valinnainen) |

### contact – yhteystiedot

| Kenttä | Kuvaus |
|--------|--------|
| `website` | Verkkosivu |
| `email`, `email_secondary` | Sähköpostit |
| `phone`, `phone_secondary` | Puhelinnumerot |
| `facebook`, `instagram`, … | Sosiaalinen media |

### contact_person – yhteyshenkilö

| Kenttä | Kuvaus |
|--------|--------|
| `name`, `role` | Nimi ja rooli |
| `email`, `phone` | Yhteystiedot |

### external_ids – ulkoiset tunnisteet

| Kenttä | Kuvaus |
|--------|--------|
| `suomisport_id` | Suomisport-tunnus |
| `laji_fi_id` | Laji.fi-tunnus |
| `federation_ids` | `{source_id: external_id}` |

### activity – toiminta

| Kenttä | Kuvaus |
|--------|--------|
| `status` | aktiivinen / passiivinen / lakkautettu |
| `founded_year` | Perustamisvuosi |
| `member_count` | Jäsenmäärä |
| `has_active_grant` | Avustuksen saaja |
| `has_facility_booking` | Liikuntatilavaraus käytössä |

### quality – laatu

| Kenttä | Kuvaus |
|--------|--------|
| `completeness_score` | 0–1, kuinka monta kenttää täytetty |
| `confidence_score` | 0–1, luotettavuus |
| `source_count` | Montako lähdettä yhdistetty |
| `needs_review` | Manuaalinen tarkistus tarpeen |
| `merge_version` | Montako merge-kertaa |

### provenienssi

| Kenttä | Kuvaus |
|--------|--------|
| `source_links` | Linkit lähteisiin (`ClubSourceLink`) |
| `field_provenance` | Kenttäkohtainen alkuperä (`FieldProvenance`) |

---

## ClubObservation – lähdetason havainto

Tiedosto: `src/urheiluseurapro/models/observation.py`

Jokaisella havainnolla on **raaka** ja **normalisoitu** versio kentistä:

```
name_raw  →  normalize  →  name_normalized
email_raw →  normalize  →  email_normalized
...
```

Lisäksi deduplikointimetadata:

| Kenttä | Kuvaus |
|--------|--------|
| `match_status` | unmatched / matched / needs_review |
| `match_confidence` | exact / high / medium / low |
| `matched_master_club_id` | Linkitetty master-tietue |
| `match_score` | 0–1 |
| `raw` | Alkuperäinen raakadata (JSON) |

---

## Normalisointi

Tiedosto: `src/urheiluseurapro/normalization/fields.py`

| Funktio | Tekee |
|---------|-------|
| `normalize_club_name` | Poistaa " ry", välimerkit, lowercase |
| `normalize_municipality` | Yhtenäistää kunnan nimen |
| `normalize_business_id` | Y-tunnus muotoon NNNNNNN-N |
| `normalize_email` | Lowercase, trim |
| `normalize_phone` | +358-muoto |
| `normalize_website` | https, lowercase, ei trailing slash |
| `normalize_sport` | Lowercase (lajisanakirja tuleva) |

Normalisointi ajetaan **aina** ennen deduplikointia (`pipeline/ingest.py`).

---

## Deduplikointi

Tiedosto: `src/urheiluseurapro/deduplication/matcher.py`

### Matching-säännöt (prioriteettijärjestys)

| # | Sääntö | Luottamus | Score |
|---|--------|-----------|-------|
| 1 | Y-tunnus täsmää | EXACT | 1.0 |
| 2 | Suomisport-ID täsmää | EXACT | 1.0 |
| 3 | Nimi + kunta + laji | HIGH | 0.9 |
| 4 | Nimi + kunta | MEDIUM | 0.75 |
| 5 | Fuzzy nimi (tuleva) | LOW | 0.5–0.7 |
| – | Ei osumaa | NO_MATCH | 0.0 |

### Canonical key (uusi master-tietue)

```
yt:1234567-8                              ← Y-tunnus
ss:SUOMISPORT_ID                          ← Suomisport
name:tampereen+palloseura|tampere|jalkapallo  ← nimi+kunta+laji
```

Epävarmat tapaukset merkitään `needs_review = True` (tuleva logiikka).

---

## Lähteiden yhdistäminen (merge)

Tiedosto: `src/urheiluseurapro/merge/engine.py`

### Merge-prioriteetti (oletus)

| Lähde | Prioriteetti | Perustelu |
|-------|--------------|-----------|
| PRH/YTJ | 95 | Virallinen rekisteri |
| Suomisport | 90 | Laaja seurarekisteri |
| Laji.fi | 85 | Aggregaattori |
| Lajiliitot | 80 | Lajikohtainen auktoriteetti |
| Aluejärjestöt | 60 | Alueellinen |
| Kunnat | 55 | Paikallinen |
| Avustusrekisterit | 50 | Täydentää yhteyshenkilöitä |
| Varausjärjestelmät | 40 | Täydentää aktiivisuutta |

### Kenttävalinta

```
Jos uusi lähde.prioriteetti > nykyinen.prioriteetti:
    → päivitä kenttä
    → tallenna FieldProvenance
Muuten:
    → säilytä nykyinen arvo
```

### Konfliktit

Kun kaksi korkeaprioriteettista lähdettä antaa eri arvon:
- Molemmat tallennetaan provenienssiin
- `quality.needs_review = True`
- Master-kenttässä korkeampi prioriteetti voittaa

---

## Tietovirta (kokonaisuus)

```
1. Ingestori kerää raakadatan
        ↓
2. ClubObservation luodaan (raw-kentät)
        ↓
3. apply_normalization() → normalized-kentät
        ↓
4. match_observation_to_club() → osuma masteriin?
        ↓
   Kyllä → merge_observation_into_club()
   Ei    → observation_to_club() (uusi master)
        ↓
5. Club tallennetaan master-tietokantaan
        ↓
6. ClubSourceLink + FieldProvenance päivitetään
        ↓
7. completeness_score lasketaan
```

Orchestraatio: `pipeline/ingest.py` → `ingest_observations()`

---

## Tietokantaskeema (suunniteltu)

```
sources              ← Source-malli (synkronoitu sources.md)
clubs                ← Club master-tietueet
club_observations    ← ClubObservation staging
club_source_links    ← ClubSourceLink
field_provenance     ← FieldProvenance
ingestion_runs       ← IngestionRun
```

Staging-havainnot säilytetään – master-tietue voidaan aina jäljitetä alkuperään.

---

## Esimerkki: sama seura kolmessa lähteessä

| Lähde | Nimi | Kunta | Email |
|-------|------|-------|-------|
| PRH | Tampereen Pallo-Veikot ry | Tampere | – |
| Suomisport | Tampereen Pallo-Veikot | Tampere | info@tpv.fi |
| Tampere.fi | TPV | Tampere | tpv@example.fi |

**Master-tietue:**

```
name:        Tampereen Pallo-Veikot ry    ← PRH (prioriteetti 95)
name_short:  TPV                          ← Tampere.fi
municipality: Tampere
email:       info@tpv.fi                 ← Suomisport (90)
source_count: 3
```

---

## Seuraavat askeleet

- [ ] Tietokantaskeema SQLiteen (Alembic-migraatiot)
- [ ] Fuzzy name matching (Levenshtein / rapidfuzz)
- [ ] Lajisanakirja (synonyymit: "jalkapallo" = "football")
- [ ] Kuntanumerorekisteri (Kaikki kunnat 2024)
- [ ] `needs_review`-jono manuaaliselle tarkistukselle
- [ ] Source-mallin synkronointi sources.md:stä

## Liittyvät tiedostot

| Tiedosto | Sisältö |
|----------|---------|
| `models/club.py` | Club master-malli |
| `models/observation.py` | ClubObservation |
| `models/source.py` | Source metadata |
| `models/provenance.py` | Provenienssi |
| `models/enums.py` | Jaetut enumit |
| `normalization/fields.py` | Normalisointi |
| `deduplication/matcher.py` | Matching |
| `merge/engine.py` | Merge-logiikka |
| `pipeline/ingest.py` | Orchestraatio |
