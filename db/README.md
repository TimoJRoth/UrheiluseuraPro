# Tietokanta

Suomen kattavin urheiluseurojen **master-tietokanta** – ei scraper-projekti.

| Tiedosto | Käyttö |
|----------|--------|
| [schema.sql](schema.sql) | SQLite kehitys (v1.1.0) |
| [schema.postgresql.sql](schema.postgresql.sql) | PostgreSQL tuotanto |
| [seed/reference.sql](seed/reference.sql) | Lajit, maakunnat, kaupungit |
| [queries/examples.sql](queries/examples.sql) | Esimerkkikyselyt |
| `src/urheiluseurapro/db/repository.py` | SQLite-repository |
| `src/urheiluseurapro/merge/engine.py` | Merge-engine (havainnot → master) |

## Merge ja provenance

Merge-engine (`merge/engine.py`) toimii sovelluskerroksessa ennen SQL-kirjoitusta:

- **Havainnot** → `observations` + `observation_*` -taulut (staging)
- **Master** → `organizations` + liitostaulut
- **Provenienssi** → `field_provenance` (linkittää master-kentän havaintoon)

Periaate: havaintoja ei poisteta merge-vaiheessa; master-arvo päivittyy uudelleenlaskennalla.

### Yhteyshenkilöt

| SQL | Sovelluskerros |
|-----|----------------|
| `observation_contact_persons` | `ContactPersonObservation` |
| `organization_contact_persons` | `MasterContactPerson` (roolikohtainen master) |

Merge: `merge/contact_persons.py` – append-only, roolikohtainen master-valinta.

## Käyttö (Python)

```python
from urheiluseurapro.db import SQLiteRepository

with SQLiteRepository.open_file() as db:
    db.init_schema(with_seed=True)
    org_id = db.add_organization("Ilves ry")
    sport_id = db.add_sport("jaakiekko", "Jääkiekko")
    db.link_organization_sport(org_id, sport_id, is_primary=True)
```

## Validointi

[docs/schema-validation.md](../docs/schema-validation.md) – vaatimusten täyttäminen ennen hyväksyntää.

## Dokumentaatio

[docs/database-schema.md](../docs/database-schema.md)
