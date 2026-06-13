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

**Suunnittelu ja lähdekartoitus.** Varsinaisia scrapereita ei ole vielä toteutettu. Seuraavaksi kartoitetaan lähteet, arvioidaan kattavuus ja priorisoidaan toteutusjärjestys. Katso [sources.md](sources.md) ja [roadmap.md](roadmap.md).

## Ominaisuudet (suunniteltu)

| Ominaisuus | Kuvaus |
|------------|--------|
| Lähdekartoitus | Järjestelmällinen inventaario lajiliitoista, aluejärjestöistä, kunnista ja muista hakemistoista |
| Modulaariset ingestorit | Jokainen lähde omana Python-komponenttinaan |
| Normalisoitu datamalli | Yhtenäinen `Club`-rakenne kaikille lähteille |
| Tietokanta | Paikallinen SQLite (kehitys), PostgreSQL (tuotanto, suunniteltu) |
| Deduplikointi | Sama seura useassa lähteessä → yksi tietue, useita lähteitä |
| Vienti | CSV, JSON ja myöhemmin Excel |
| CLI | Komentoriviltä suoritettava keruu, tarkistus ja vienti |

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
