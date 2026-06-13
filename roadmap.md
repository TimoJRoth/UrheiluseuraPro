# Kehityssuunnitelma

UrheiluseuraPro:n vaiheittainen tie kohti tuotantokäyttöistä urheiluseurojen tietokantaa. Projektin perusta on **Python** – ei Tampermonkeyä eikä selainlaajennuksia.

## Vaihe 0 – Projektin perusta ✅

- [x] Projektirakenne (`src/`, `docs/`, `data/`, `output/`)
- [x] Python-paketointi (`pyproject.toml`)
- [x] CLI-runko (`sources`, `collect`)
- [x] Normalisoitu `Club`-datamalli
- [x] Kerääjärekisteri ja abstrakti `BaseCollector`
- [x] CSV/JSON-vienti
- [x] Konfigurointi ja lokitus

## Vaihe 1 – Lähdekartoitus 🚧 (nykyinen)

Tavoite: tietää **mistä** data tulee, ennen kuin scrapereita rakennetaan.

- [x] Lähderyhmien määrittely (9 kategoriaa, ks. [sources.md](sources.md))
- [x] Lähdeinventaario: ~170 lähdettä koko Suomesta
- [x] Optimaalinen keruujärjestys (vaiheet A–E)
- [x] Päällekkäisyysanalyysi
- [ ] robots.txt- ja käyttöehtotarkistus P1-lähteille
- [ ] Kenttäkartta lähteittäin → `Club`-malliin
- [ ] Suomisport- ja YTJ/PRH-API selvitys
- [ ] `Source`-metadatamalli koodissa
- [x] SQLite/PostgreSQL-skeema v1.1.0 (`db/schema.sql`, `db/schema.postgresql.sql`)
- [x] Skeeman validointi: [docs/schema-validation.md](docs/schema-validation.md)
- [x] Relaatiomallit (`models/relational/`)
- [x] Dokumentaatio: [docs/database-schema.md](docs/database-schema.md)
- [x] Repository-kerros SQLite:lle (`src/urheiluseurapro/db/repository.py`)

**Ei tässä vaiheessa:** scraperit, asennuskomennot, verkkopyyntöjä tuotantodatalla.

## Vaihe 2 – Tietokanta ja ingestio

- [ ] SQLite-skeema: `clubs`, `sources`, `club_sources`, `ingestion_runs`
- [ ] Migraatiot (Alembic tai yksinkertainen versiointi)
- [ ] Ensimmäinen ingestori: yksi P1-lähde (pilotti)
- [ ] HTML-parsinta (selectolax tai BeautifulSoup4)
- [ ] HTTP-asiakkaan integrointi ingestoreihin
- [ ] Raakadatan tallennus `data/raw/`-kansioon
- [ ] Ingestion-loki ja virheenkäsittely

## Vaihe 3 – Laajennus ja laatu

- [ ] P1-lähteiden ingestorit valmiiksi
- [ ] P2-lähteet (kuntalistaukset, laajempi maantieteellinen kattavuus)
- [ ] Deduplikointi: nimi + kunta + laji -heuristiikka
- [ ] Validointi (sähköposti, URL, puhelin)
- [ ] Välimuisti `data/cache/`
- [ ] Yksikkö- ja integraatiotestit ingestoreille

## Vaihe 4 – Tietokannan rikastaminen

- [ ] Usean lähteen yhdistäminen (golden record)
- [ ] Puuttuvien kenttien täydennys toissijaisista lähteistä
- [ ] Konfliktien käsittely (eri sähköposti eri lähteissä)
- [ ] Maakunta- ja postinumeropäättely
- [ ] Excel-vienti (openpyxl)
- [ ] `--dry-run` ja `--limit` CLI-parametrit

## Vaihe 5 – Käytettävyys ja integraatiot

- [ ] Rich-pohjainen CLI (edistymispalkki, taulukot)
- [ ] REST API (FastAPI) tietokantaan
- [ ] Ajastettu päivitys (cron / Task Scheduler)
- [ ] Valinnaiset integraatiot (Google Sheets, Airtable)
- [ ] Docker-kontti

## Vaihe 6 – Tuotanto

- [ ] PostgreSQL-tuki
- [ ] CI/CD (GitHub Actions)
- [ ] Semanttinen versionhallinta
- [ ] Kattava dokumentaatio ja FAQ
- [ ] Julkaisu PyPI:hin (valinnainen)

## Prioriteettijärjestys lähteille

| Prioriteetti | Merkitys | Toteutusjärjestys |
|--------------|----------|-------------------|
| **P1** | Korkea kattavuus, hyvä data, teknisesti suoraviivainen | Ensimmäiset ingestorit |
| **P2** | Hyödyllinen täydennys, kohtuullinen työmäärä | Vaihe 3 |
| **P3** | Rajallinen kattavuus tai tekninen haaste | Vaihe 3–4 |
| **P4** | Epävarma hyöty, API-rajoitukset tai manuaalityö | Arvioidaan myöhemmin |

Katso yksityiskohtainen lähdeinventaario: [sources.md](sources.md).

## Periaatteet

1. **Kartoitus ennen koodia** – ei scraperia ilman dokumentoitua lähdettä
2. **Yksi lähde, yksi ingestori** – testattava ja ylläpidettävä
3. **Tietokanta on totuuden lähde** – vienti on näkymä, ei varastointi
4. **Jäljitettävyys** – jokainen tietue linkittyy alkuperälähteeseensä
5. **Kohtuullinen kuormitus** – viiveet, robots.txt, käyttöehdot
6. **Puhdas Python** – ei Tampermonkeyä, ei selainriippuvuutta ellei pakko

## Avoimet kysymykset

- Riittääkö Suomisport + lajiliitot + kuntalistaukset hyvään kattavuuteen?
- Tarvitaanko Playwright JavaScript-painotteisille kuntasivuille?
- Miten deduplikoidaan seurat, joiden nimi vaihtelee lähteissä (lyhenne vs. virallinen nimi)?
- Tarvitaanko historiallinen seuranta (muutokset ajan yli)?
- Mitkä 5 kuntaa priorisoidaan ensimmäiseksi P2-toteutuksessa?
