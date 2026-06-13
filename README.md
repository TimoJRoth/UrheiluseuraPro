# UrheiluseuraPro

Python-pohjainen tietokantatyökalu suomalaisten urheiluseurojen tiedon keräämiseen, yhdistämiseen, rikastamiseen ja ylläpitoon.

Projekti kokoaa hajautetusta julkisesta tiedosta yhtenäisen seuratietokannan. Toteutus on puhdasta Pythonia – ei selainlaajennuksia, ei Tampermonkeyä, ei selainpohjaista keruuta.

## Tavoite

Rakentaa luotettava, toistettava ja laajennettava **urheiluseurojen tietokanta**, jossa jokaisella seuralla on:

- normalisoitu identiteetti (nimi, laji, kunta)
- jäljitettävä alkuperä (mistä lähde tieto on peräisin)
- yhteystiedot ja linkit, kun lähteestä saatavilla
- deduplikointi useista lähteistä

## Nykyinen vaihe

**Tietomalli, tietokanta ja merge-engine.** SQLite-skeema, repository-kerros ja tuotantotason merge (append-only provenance) ovat valmiit. Scrapereita ei ole vielä toteutettu. Katso [sources.md](sources.md) ja [roadmap.md](roadmap.md).

## Ominaisuudet

| Ominaisuus | Tila | Kuvaus |
|------------|------|--------|
| Lähdekartoitus | ✅ | ~170 lähdettä, 9 kategoriaa ([sources.md](sources.md)) |
| Normalisoitu datamalli | ✅ | `Club`, `ClubObservation`, relaatiomallit |
| SQLite-skeema | ✅ | `db/schema.sql` v1.2.0 |
| Repository-kerros | ✅ | `SQLiteRepository` – CRUD ja haut |
| Merge-engine | ✅ | Append-only havainnot, master-valinta prioriteetilla |
| Modulaariset ingestorit | 🚧 | Abstrakti `BaseCollector`, toteutus myöhemmin |
| Deduplikointi | ✅ | Nimi + kunta + laji / Y-tunnus |
| Vienti | ✅ | CSV, JSON |
| CLI | ✅ | `sources`, `collect` (runko) |

## Teknologiavalinnat

- **Kieli:** Python 3.11+
- **Datamallit:** Pydantic
- **HTTP:** httpx (asynkroninen)
- **Tietokanta:** SQLite → PostgreSQL (vaiheittain)
- **CLI:** argparse
- **Ei käytössä:** Tampermonkey, selainlaajennukset, headless-selain (vain jos HTML-lähde pakottaa)

## Projektirakenne

```
UrheiluseuraPro/
├── README.md                 # Projektin yleiskuvaus
├── roadmap.md                # Kehityssuunnitelma
├── sources.md                # Lähdekartoitus (pääasiallinen inventaario)
├── pyproject.toml            # Paketointi ja riippuvuudet
├── .env.example              # Ympäristömuuttujat
├── src/
│   └── urheiluseurapro/      # Sovelluskoodi
│       ├── cli.py            # Komentorivikäyttöliittymä
│       ├── config.py         # Asetukset
│       ├── models/           # Datamallit (Club, Source, …)
│       ├── merge/            # Merge-engine ja lähdeprioriteetit
│       ├── db/               # SQLite-repository
│       ├── collectors/       # Ingestorit (toteutetaan myöhemmin)
│       ├── exporters/        # CSV/JSON-vienti
│       └── pipeline/         # Keruu- ja tallennusputki
├── docs/
│   ├── architecture.md       # Arkkitehtuuri ja tietovirta
│   └── getting-started.md    # Kehittäjän aloitusopas
├── data/
│   ├── raw/                  # Manuaalisesti ladattu raakadata
│   └── cache/                # Välimuisti
└── output/                   # Viety data (CSV, JSON)
```

## Lähderyhmät

Tietolähteet on jaoteltu neljään kategoriaan ([sources.md](sources.md)):

1. **Lajiliitot** – valtakunnalliset lajikohtaiset liitot ja niiden seurarekisterit
2. **Liikunnan aluejärjestöt** – liikuntapiirit ja muut alueelliset järjestöt
3. **Kaupungit ja kunnat** – kuntien viralliset seura- ja liikuntalistaukset
4. **Muut seurahakemistot** – Suomisport, avoin data, aggregaattorit

## Asennus ja käyttö

Asennusohjeet tulevat käyttöön, kun ensimmäinen ingestori on valmis. Kehittäjille: [docs/getting-started.md](docs/getting-started.md).

## Kehitysperiaatteet

1. **Lähde ensin** – kartoitus ennen koodausta
2. **Yksi lähde, yksi ingestori** – selkeä vastuu ja testattavuus
3. **Jäljitettävyys** – jokaisella tietueella `source_id` ja keruuaika
4. **Kohtuullinen kuormitus** – viiveet, User-Agent, robots.txt
5. **Ei selainriippuvuutta** – HTML/API/Excel ensisijaisesti
6. **Havainnot säilyvät** – merge ei koskaan poista lähdedataa; master lasketaan erikseen

## Merge-engine

Jokainen lähdehavainto tallennetaan erikseen (`FieldObservation`). Master-arvot lasketaan havainnoista:

1. Seuran oma verkkosivu (100)
2. Suomisport (90)
3. Olympiakomitea (85)
4. Lajiliitto (80)
5. Kunnan sivut (70)
6. PRH/YTJ (65)
7. Muu lähde (40)

Konfliktit (esim. eri sähköposti): kaikki havainnot säilyvät, aktiivinen master valitaan prioriteetin, tuoreuden ja yksimielisyyden perusteella. `confidence_score` ja `supporting_sources` tallennetaan `MasterFieldValue`-rakenteeseen.

```python
from urheiluseurapro.merge import merge_observation_into_club, observation_to_club

club = observation_to_club(observation, sources=sources)
club = merge_observation_into_club(club, another_observation, source, sources=sources)
```

Testit: `pytest tests/test_merge_engine.py`

## Dokumentaatio

- [Kehityssuunnitelma](roadmap.md)
- [Lähdekartoitus](sources.md)
- [Tietokantaskeema (SQL)](docs/database-schema.md)
- [Skeeman validointi](docs/schema-validation.md)
- [Tietomalli (sovelluskerros)](docs/data-model.md)
- [Arkkitehtuuri](docs/architecture.md)
- [Aloitusopas](docs/getting-started.md)

## Lisenssi

MIT
