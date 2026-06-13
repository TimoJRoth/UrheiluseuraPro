# Tietokanta

Suomen kattavin urheiluseurojen **master-tietokanta** – ei scraper-projekti.

| Tiedosto | Käyttö |
|----------|--------|
| [schema.sql](schema.sql) | SQLite kehitys (v1.1.0) |
| [schema.postgresql.sql](schema.postgresql.sql) | PostgreSQL tuotanto |
| [seed/reference.sql](seed/reference.sql) | Lajit, maakunnat, kaupungit |
| [queries/examples.sql](queries/examples.sql) | Esimerkkikyselyt |
| `src/urheiluseurapro/db/repository.py` | SQLite-repository |

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
