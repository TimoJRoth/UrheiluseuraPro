# Arkkitehtuuri

UrheiluseuraPro on Python-pohjainen **urheiluseurojen tietokantatyökalu**. Se kerää hajautetusta julkisesta tiedosta, normalisoi sen, tallentaa tietokantaan ja tarjoaa viennin sekä myöhemmin rajapinnan.

Projekti **ei käytä** Tampermonkeyä, selainlaajennuksia tai selainpohjaista keruuta. Kaikki ingestio tapahtuu Pythonilla (HTTP, HTML-parsinta, tiedostoluku, API).

## Kokonaiskuva

```
┌──────────────────────────────────────────────────────────────┐
│  Ulkoiset lähteet                                            │
│  lajiliitot │ aluejärjestöt │ kunnat │ muut hakemistot       │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│  Ingestorit (collectors/)          ← toteutetaan vaihe 2+    │
│  HTML / API / Excel / PDF                                    │
└────────────────────────────┬─────────────────────────────────┘
                             │ list[Club] + metadata
                             ▼
┌──────────────────────────────────────────────────────────────┐
│  Normalisointi & validointi (models/)                        │
│  Pydantic Club, Source, IngestionRun                        │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│  Tietokanta (suunniteltu, vaihe 2)                           │
│  SQLite (dev) → PostgreSQL (prod)                            │
│  clubs │ sources │ club_sources │ ingestion_runs             │
└────────────────────────────┬─────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         Exporters        CLI           API (vaihe 5)
         CSV/JSON/Excel   collect       FastAPI
```

## Nykyinen tila vs. suunniteltu

| Komponentti | Tila | Kuvaus |
|-------------|------|--------|
| Lähdekartoitus | 🚧 Käynnissä | `sources.md`, neljä lähderyhmää |
| Datamallit | ✅ Suunniteltu | Relaatiomalli + merge/dedup – ks. [database-schema.md](database-schema.md) |
| Ingestorit | ✅ Runko | `BaseCollector`, `MockCollector`, `CollectorRegistry` |
| Tietokanta | ✅ Skeema valmis | `db/schema.sql` – repository + merge kirjoitus tuleva |
| Deduplikointi | ✅ Suunniteltu | matcher.py; SQL-toteutus tuleva |
| CLI | ✅ Runko valmis | `sources`, `collect` |
| Vienti | ✅ CSV/JSON | Excel myöhemmin |

## Kerrokset

### 1. Lähdekartoitus (dokumentaatio)

Ennen koodausta jokainen lähde dokumentoidaan [sources.md](../sources.md):

- lähderyhmä (lajiliitto, aluejärjestö, kunta, muu)
- kattavuus ja saatavilla olevat kentät
- tekninen muoto (HTML, API, Excel, PDF)
- prioriteetti (P1–P4)

Tämä kerros ei ole koodia – se ohjaa ingestoreiden toteutusjärjestystä.

### 2. Ingestorit (`collectors/`)

Geneerinen keruuarkkitehtuuri:

```
BaseCollector.collect() → list[CollectorResult]
    ↓
run_collector() → IngestionRun + ClubObservation[]
    ↓
ingest_observations() → Club master
```

| Komponentti | Tiedosto | Rooli |
|-------------|----------|-------|
| `BaseCollector` | `collectors/base.py` | Abstrakti rajapinta |
| `CollectorResult` | `models/collector.py` | Yhtenäinen tulos + provenance |
| `CollectorRegistry` | `collectors/registry.py` | Rekisteröinti ja haku |
| `run_collector` | `collectors/runner.py` | Ajon orkestraatio |
| `MockCollector` | `collectors/mock.py` | Kehitys/testi (3 seuraa muistista) |
| `HttpClient` | `collectors/http/client.py` | Retry, timeout, rate limit, User-Agent |
| `HttpCollector` | `collectors/http/base.py` | HTTP/JSON-ingestorien pohja |
| `JsonFeedCollector` | `collectors/examples/json_feed.py` | Esimerkki HTTP JSON -syötteestä |

```python
class BaseCollector(ABC):
    source_id: str
    display_name: str

    async def collect(self) -> list[CollectorResult]: ...
    def supports_url(self, url: str) -> bool: ...
```

Ingestorit rekisteröidään `CollectorRegistry`-luokkaan. Uusia lähteitä lisätään ilman CLI- tai pipeline-muutoksia.

**HTTP-kerros (uudelleenkäytettävä):**

```
HttpClient.get_json(url)
    → retry (429/5xx), timeout, rate limit, User-Agent
    → HttpFetchMetadata (url, fetched_at, status_code)
    ↓
HttpCollector.parse_club_records(payload)
    ↓
CollectorResult (source_url, fetched_at, ClubObservation)
```

Ingestorit rekisteröidään `CollectorRegistry`-luokkaan. Oletusrekisterissä on `MockCollector`; HTTP-ingestorit rekisteröidään erikseen kun lähde on valmis.

**Tulevat ingestorityypit:**

| Tyyppi | Tekniikka | Huomio |
|--------|-----------|--------|
| JSON/API | `HttpClient` + `HttpCollector` | Viralliset rajapinnat ensin |
| Tiedosto-ingestori | openpyxl / pdfplumber | Manuaalisesti ladattu data |

### 3. Datamallit (`models/`)

**Club** – normalisoitu seuratietue (Pydantic):

| Kenttä | Kuvaus |
|--------|--------|
| `name` | Seuran nimi (pakollinen) |
| `sport` | Laji |
| `municipality` | Kunta |
| `region` | Maakunta |
| `website`, `email`, `phone`, `address` | Yhteystiedot |
| `source_id` | Ingestorin tunniste |
| `source_url` | Alkuperäisen lähteen URL |
| `collected_at` | Keruuaika (UTC) |

**Source** (suunniteltu, vaihe 1–2) – lähteen metadata:

| Kenttä | Kuvaus |
|--------|--------|
| `source_id` | Uniikki tunniste |
| `name` | Näyttönimi |
| `category` | lajiliitto / aluejärjestö / kunta / muu |
| `priority` | P1–P4 |
| `format` | HTML / API / Excel / PDF |
| `url` | Pää-URL |

### 4. Tietokanta (suunniteltu, vaihe 2)

```
sources          – lähteiden metadata (synkronoitu sources.md:stä)
clubs            – deduplikoitu seuratieto
club_sources     – linkki seura ↔ lähde (provenienssi)
ingestion_runs   – ajohistoria (aika, lähde, rivimäärä, virheet)
```

Deduplikointi tapahtuu tallennusvaiheessa: useat lähteet voivat viitata samaan `club_id`:hen `club_sources`-taulun kautta.

### 5. Pipeline (`pipeline/`)

Orkestroi ingestoinnin:

1. Hae ingestori rekisteristä
2. Suorita `collect()` → `list[Club]`
3. Validoi Pydantic-mallilla
4. (Tulevaisuudessa) tallenna tietokantaan
5. Vie CSV/JSON `output/`-kansioon

### 6. CLI (`cli.py`)

| Komento | Kuvaus | Tila |
|---------|--------|------|
| `sources` | Listaa rekisteröidyt lähteet | ✅ |
| `collect <source>` | Kerää ja vie yhdestä lähteestä | ⏳ Odottaa ingestoreita |
| `db status` | Tietokannan tila | ⏳ Suunniteltu |
| `export` | Vie tietokannasta | ⏳ Suunniteltu |

### 7. Exporters (`exporters/`)

Funktiot `export_csv()` ja `export_json()` kirjoittavat tulokset `output/`-kansioon UTF-8 -enkoodauksella.

## Tietovirta (tavoitetila)

```
1. urheiluseurapro collect tampere-liikunta
2. CLI → Settings → CollectorRegistry
3. TampereCollector.collect() → HTTP + HTML-parsinta
4. list[Club] validoidaan
5. Tallennus: clubs + club_sources (SQLite)
6. export_csv() → output/clubs_tampere-liikunta_20250613.csv
7. CLI tulostaa: "Kerätty 142 seuraa, tallennettu 138 (4 duplikaattia)"
```

## Lähderyhmät arkkitehtuurissa (tuleva)

```
sources.md (inventaario)
    │
    └── BaseCollector-aliluokka + CollectorRegistry.register()
```

Nykyinen `collectors/`-rakenne tarjoaa geneerisen rajapinnan (`BaseCollector`, `MockCollector`). Oikeat lähteet lisätään myöhemmin dokumentoinnin (`sources.md`) jälkeen.

## Konfiguraatio

`Settings` (pydantic-settings) lukee `URHEILUSEURAPRO_*`-ympäristömuuttujat:

| Muuttuja | Oletus | Kuvaus |
|----------|--------|--------|
| `REQUEST_DELAY` | 1.0 | Sekuntien viive pyyntöjen välillä |
| `REQUEST_TIMEOUT` | 30.0 | HTTP-aikakatkaisu |
| `USER_AGENT` | UrheiluseuraPro/0.1 | User-Agent-otsikko |
| `LOG_LEVEL` | INFO | Lokitaso |
| `OUTPUT_DIR` | output | Vientikansio |
| `DATA_DIR` | data | Raaka- ja välimuistidata |

## Riippuvuudet

| Paketti | Käyttö | Vaihe |
|---------|--------|-------|
| httpx | Asynkroninen HTTP | 2 |
| pydantic | Datamallit | ✅ |
| pydantic-settings | Konfiguraatio | ✅ |
| python-dotenv | .env-tuki | ✅ |
| rich | Lokitus, CLI | ✅ |
| selectolax / bs4 | HTML-parsinta | 2 |
| openpyxl | Excel-luku | 3 |
| alembic / sqlite3 | Tietokanta | 2 |

## Laajennusohje (myöhemmille vaiheille)

| Tarve | Paikka |
|-------|--------|
| Uusi lähde | `collectors/<ryhmä>/<lähde>.py` + rekisteröinti + `sources.md` |
| Uusi vientiformaatti | `exporters/` |
| Tietokantaskeema | `db/schema.sql` tai Alembic-migraatiot |
| Välimuisti | `data/cache/` + ingestori |
| REST API | `api/` (FastAPI) |

## Rajoitteet ja periaatteet

- **Ei Tampermonkeyä** – kaikki ingestio Pythonilla
- **robots.txt** – tarkistetaan ennen keruuta
- **Kohtuullinen kuormitus** – konfiguroitava viive
- **Provenienssi** – tieto ei koskaan ilman `source_id`:tä
- **Headless-selain vain poikkeuksena** – dokumentoidaan erikseen, jos HTML-lähde vaatii JS-renderöinnin

**Sitovat merge- ja provenance-säännöt:** [ARKKITEHTUURI.md](ARKKITEHTUURI.md)
