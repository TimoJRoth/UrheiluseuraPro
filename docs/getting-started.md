# Aloitusopas

Nopea opas UrheiluseuraPro:n kehitysympäristöön.

> **Nykyinen vaihe:** lähdekartoitus ([sources.md](../sources.md)). Asennus ja ensimmäiset ingestorit tulevat käyttöön vaiheessa 2 – ohjeet alla ovat valmiina etukäteen.

## 1. Kloonaa tai avaa projekti

```bash
cd c:\Tilakeskus_AI\UrheiluseuraPro
```

## 2. Luo virtuaaliympäristö

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 3. Asenna riippuvuudet

```bash
pip install -e ".[dev]"
```

## 4. Konfiguroi ympäristö

```bash
copy .env.example .env
```

Muokkaa `.env` tarvittaessa (esim. `URHEILUSEURAPRO_LOG_LEVEL=DEBUG`).

## 5. Kokeile CLI:tä

```bash
urheiluseurapro --version
urheiluseurapro sources
```

Ensimmäisessä versiossa kerääjiä ei ole vielä rekisteröity – `sources` kertoo tämän.

## 6. Ensimmäinen kerääjä (kehittäjille)

1. Luo tiedosto `src/urheiluseurapro/collectors/tampere.py`
2. Peri `BaseCollector` ja toteuta `collect()` sekä `supports_url()`
3. Rekisteröi kerääjä `default_registry()`-funktiossa
4. Aja: `urheiluseurapro collect tampere-liikunta --format both`
5. Tarkista tulos `output/`-kansiosta

## 7. Hyödylliset komennot

```bash
# Linttaus
ruff check src

# Muotoilu
ruff format src

# Tyyppitarkistus
mypy src
```

## Kansiot

| Kansio | Tarkoitus |
|--------|-----------|
| `src/` | Sovelluskoodi |
| `docs/` | Tekninen dokumentaatio |
| `data/raw/` | Manuaalisesti ladattu raakadata |
| `data/cache/` | Automaattinen välimuisti |
| `output/` | Generoidut CSV/JSON-tiedostot |

## Seuraavat askeleet

- Lue [roadmap.md](../roadmap.md) prioriteeteista
- Lue [sources.md](../sources.md) suunnitelluista lähteistä
- Lue [architecture.md](architecture.md) rakenteesta
