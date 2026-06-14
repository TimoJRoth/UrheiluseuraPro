"""Entity resolution -apuavaimet seurojen tunnistamiseen."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from urheiluseurapro.normalizers.email import normalize_email
from urheiluseurapro.normalizers.municipality import normalize_municipality
from urheiluseurapro.normalizers.phone import normalize_phone
from urheiluseurapro.normalizers.text import clean_text
from urheiluseurapro.normalizers.website import normalize_website

_MATCH_SUFFIXES = (
    " rekisteröity yhdistys",
    " ry",
    " rf",
    " sr",
    " r.y.",
    " r.f.",
    " r.s.",
)


def normalize_org_name_for_matching(name: str | None) -> str | None:
    """
    Normalisoi organisaation nimi matchausta varten.

    Poistaa yleiset oikeusmuotoliitteet (ry, r.y., rekisteröity yhdistys jne.),
    normalisoi kirjainkoon ja välilyönnit.
    """
    text = clean_text(name)
    if not text:
        return None

    lowered = text.lower()

    changed = True
    while changed:
        changed = False
        for suffix in _MATCH_SUFFIXES:
            if lowered.endswith(suffix):
                lowered = lowered[: -len(suffix)].strip()
                changed = True

    lowered = re.sub(r"[^\w\s]", "", lowered, flags=re.UNICODE)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered or None


def _website_domain(url: str | None) -> str | None:
    normalized = normalize_website(url)
    if not normalized:
        return None
    parsed = urlparse(normalized)
    host = parsed.netloc or parsed.path.split("/")[0]
    host = host.lower().strip()
    if host.startswith("www."):
        host = host[4:]
    return host or None


def _field(record: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in record and record[name] not in (None, ""):
            return record[name]
    return None


def club_match_keys(record: dict[str, Any]) -> list[str]:
    """
    Muodosta matchausavaimet seuratietueesta.

    Palauttaa tyhjän listan, jos recordista ei saada yhtään avainta.
    """
    keys: set[str] = set()

    email = normalize_email(_field(record, "email", "email_raw", "email_normalized"))
    if email:
        keys.add(f"email:{email}")

    domain = _website_domain(_field(record, "website", "website_raw", "website_normalized"))
    if domain:
        keys.add(f"website:{domain}")

    phone = normalize_phone(_field(record, "phone", "phone_raw", "phone_normalized"))
    if phone:
        keys.add(f"phone:{phone}")

    name = normalize_org_name_for_matching(_field(record, "name", "name_raw", "name_normalized"))
    municipality = normalize_municipality(_field(record, "municipality", "municipality_raw", "municipality_normalized"))
    if name and municipality:
        keys.add(f"name_municipality:{name}|{municipality.lower()}")

    return sorted(keys)
