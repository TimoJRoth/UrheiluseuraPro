"""Canonical club -rakennus yhdestä tai useammasta lähdetietueesta."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from urheiluseurapro.normalizers.email import normalize_email
from urheiluseurapro.normalizers.municipality import normalize_municipality
from urheiluseurapro.normalizers.phone import normalize_phone
from urheiluseurapro.normalizers.sports import normalize_sports
from urheiluseurapro.normalizers.text import clean_text
from urheiluseurapro.normalizers.website import normalize_website

_PROVENANCE_META_KEYS = (
    "source",
    "source_id",
    "source_url",
    "source_record_key",
    "confidence",
    "observation_confidence",
    "fetched_at",
    "first_seen_at",
    "last_seen_at",
    "ingestion_run_id",
    "observation_id",
)

_NAME_FIELDS = ("name_official", "name", "name_raw", "name_normalized")
_EMAIL_FIELDS = ("email_normalized", "email", "email_raw")
_PHONE_FIELDS = ("phone_normalized", "phone", "phone_raw")
_WEBSITE_FIELDS = ("website_normalized", "website", "website_raw")
_SPORTS_FIELDS = ("sports_normalized", "sports", "sports_raw")
_MUNICIPALITY_FIELDS = ("municipality_normalized", "municipality", "municipality_raw")
_CONFIDENCE_FIELDS = ("confidence", "observation_confidence", "source_confidence")


@dataclass(frozen=True)
class CanonicalClub:
    """Yhden seuran canonical-esitys yhdestä tai useammasta lähdetietueesta."""

    canonical_name: str | None
    municipality: str | None
    emails: list[str]
    phones: list[str]
    websites: list[str]
    sports: list[str]
    source_records: list[dict[str, Any]]
    provenance: list[dict[str, Any]]
    confidence: float


class CanonicalClubBuilder:
    """
    Muodostaa canonical club -esityksen lähdetietueista.

    Ei deduplikoi koko aineistoa – odottaa että syöte on jo samaa seuraa
    kuvaavia tietueita (tai yksi tietue).
    """

    def build(self, record: dict[str, Any]) -> CanonicalClub:
        """Rakenna canonical-esitys yhdestä tietueesta."""
        return self.build_many([record])

    def build_many(self, records: list[dict[str, Any]]) -> CanonicalClub:
        """Rakenna canonical-esitys useasta samaa seuraa kuvaavasta tietueesta."""
        if not records:
            raise ValueError("At least one source record is required")

        source_records = [copy.deepcopy(record) for record in records]
        ordered = _records_by_confidence(source_records)

        emails, email_provenance = _collect_values(
            ordered, _EMAIL_FIELDS, normalize_email, "emails"
        )
        phones, phone_provenance = _collect_values(
            ordered, _PHONE_FIELDS, normalize_phone, "phones"
        )
        websites, website_provenance = _collect_websites(ordered)
        sports, sports_provenance = _collect_sports(ordered)

        canonical_name = _pick_canonical_name(ordered)
        name_provenance = _name_provenance(ordered, canonical_name)
        municipality = _pick_municipality(ordered)
        municipality_provenance = _municipality_provenance(ordered, municipality)

        provenance = (
            name_provenance
            + municipality_provenance
            + email_provenance
            + phone_provenance
            + website_provenance
            + sports_provenance
        )
        confidence = _aggregate_confidence(source_records)

        return CanonicalClub(
            canonical_name=canonical_name,
            municipality=municipality,
            emails=emails,
            phones=phones,
            websites=websites,
            sports=sports,
            source_records=source_records,
            provenance=provenance,
            confidence=confidence,
        )


def build_canonical_club(record: dict[str, Any] | list[dict[str, Any]]) -> CanonicalClub:
    """Rakenna canonical club yhdestä tietueesta tai listasta."""
    builder = CanonicalClubBuilder()
    if isinstance(record, list):
        return builder.build_many(record)
    return builder.build(record)


def _field(record: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in record and record[name] not in (None, ""):
            return record[name]
    return None


def _record_confidence(record: dict[str, Any]) -> float:
    for key in _CONFIDENCE_FIELDS:
        value = record.get(key)
        if isinstance(value, (int, float)):
            return float(max(0.0, min(1.0, value)))
    return 0.0


def _records_by_confidence(records: list[dict[str, Any]]) -> list[tuple[int, dict[str, Any]]]:
    indexed = list(enumerate(records))
    indexed.sort(key=lambda item: (-_record_confidence(item[1]), item[0]))
    return indexed


def _provenance_meta(record: dict[str, Any]) -> dict[str, Any]:
    meta: dict[str, Any] = {}
    for key in _PROVENANCE_META_KEYS:
        if key in record and record[key] not in (None, ""):
            meta[key] = record[key]
    if "source" in meta and "source_id" not in meta:
        meta["source_id"] = meta["source"]
    elif "source_id" in meta and "source" not in meta:
        meta["source"] = meta["source_id"]
    return meta


def _provenance_entry(
    *,
    field_name: str,
    value: Any,
    source_index: int,
    record: dict[str, Any],
    record_field: str | None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "field": field_name,
        "value": value,
        "source_index": source_index,
        "record_field": record_field,
    }
    entry.update(_provenance_meta(record))
    return entry


def _display_name(record: dict[str, Any]) -> str | None:
    for name_field in _NAME_FIELDS:
        value = _field(record, name_field)
        if value is not None:
            text = clean_text(str(value))
            if text:
                return text
    return None


def _pick_canonical_name(
    ordered: list[tuple[int, dict[str, Any]]],
) -> str | None:
    candidates: list[tuple[float, int, str]] = []
    for source_index, record in ordered:
        name = _display_name(record)
        if name:
            candidates.append((_record_confidence(record), -len(name), name))

    if not candidates:
        return None

    candidates.sort(reverse=True)
    return candidates[0][2]


def _name_provenance(
    ordered: list[tuple[int, dict[str, Any]]],
    canonical_name: str | None,
) -> list[dict[str, Any]]:
    if canonical_name is None:
        return []

    provenance: list[dict[str, Any]] = []
    for source_index, record in ordered:
        for name_field in _NAME_FIELDS:
            value = _field(record, name_field)
            if value is not None and clean_text(str(value)) == canonical_name:
                provenance.append(
                    _provenance_entry(
                        field_name="canonical_name",
                        value=canonical_name,
                        source_index=source_index,
                        record=record,
                        record_field=name_field,
                    )
                )
                break
    return provenance


def _pick_municipality(
    ordered: list[tuple[int, dict[str, Any]]],
) -> str | None:
    for _, record in ordered:
        for municipality_field in _MUNICIPALITY_FIELDS:
            raw = _field(record, municipality_field)
            if raw is None:
                continue
            normalized = normalize_municipality(raw)
            if normalized:
                return normalized
    return None


def _municipality_provenance(
    ordered: list[tuple[int, dict[str, Any]]],
    municipality: str | None,
) -> list[dict[str, Any]]:
    if municipality is None:
        return []

    provenance: list[dict[str, Any]] = []
    for source_index, record in ordered:
        for municipality_field in _MUNICIPALITY_FIELDS:
            raw = _field(record, municipality_field)
            if raw is None:
                continue
            normalized = normalize_municipality(raw)
            if normalized == municipality:
                provenance.append(
                    _provenance_entry(
                        field_name="municipality",
                        value=municipality,
                        source_index=source_index,
                        record=record,
                        record_field=municipality_field,
                    )
                )
                break
    return provenance


def _collect_values(
    ordered: list[tuple[int, dict[str, Any]]],
    field_names: tuple[str, ...],
    normalizer: Any,
    canonical_field: str,
) -> tuple[list[str], list[dict[str, Any]]]:
    values: list[str] = []
    provenance: list[dict[str, Any]] = []
    seen: set[str] = set()

    for source_index, record in ordered:
        for record_field in field_names:
            raw = _field(record, record_field)
            if raw is None:
                continue
            normalized = normalizer(raw)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            values.append(normalized)
            provenance.append(
                _provenance_entry(
                    field_name=canonical_field,
                    value=normalized,
                    source_index=source_index,
                    record=record,
                    record_field=record_field,
                )
            )
            break

    return values, provenance


def _website_domain(url: str) -> str | None:
    normalized = normalize_website(url)
    if not normalized:
        return None
    parsed = urlparse(normalized)
    host = parsed.netloc or parsed.path.split("/")[0]
    host = host.lower().strip()
    if host.startswith("www."):
        host = host[4:]
    return host or None


def _collect_websites(
    ordered: list[tuple[int, dict[str, Any]]],
) -> tuple[list[str], list[dict[str, Any]]]:
    values: list[str] = []
    provenance: list[dict[str, Any]] = []
    seen_domains: set[str] = set()

    for source_index, record in ordered:
        for record_field in _WEBSITE_FIELDS:
            raw = _field(record, record_field)
            if raw is None:
                continue
            normalized = normalize_website(raw)
            domain = _website_domain(raw)
            if not normalized or not domain or domain in seen_domains:
                continue
            seen_domains.add(domain)
            values.append(normalized)
            provenance.append(
                _provenance_entry(
                    field_name="websites",
                    value=normalized,
                    source_index=source_index,
                    record=record,
                    record_field=record_field,
                )
            )
            break

    return values, provenance


def _collect_sports(
    ordered: list[tuple[int, dict[str, Any]]],
) -> tuple[list[str], list[dict[str, Any]]]:
    sports: list[str] = []
    provenance: list[dict[str, Any]] = []
    seen: set[str] = set()

    for source_index, record in ordered:
        for record_field in _SPORTS_FIELDS:
            raw = _field(record, record_field)
            if raw is None:
                continue
            for sport in normalize_sports(raw):
                if sport in seen:
                    continue
                seen.add(sport)
                sports.append(sport)
                provenance.append(
                    _provenance_entry(
                        field_name="sports",
                        value=sport,
                        source_index=source_index,
                        record=record,
                        record_field=record_field,
                    )
                )
            if raw is not None:
                break

    return sports, provenance


def _aggregate_confidence(records: list[dict[str, Any]]) -> float:
    confidences = [_record_confidence(record) for record in records]
    if any(confidence > 0.0 for confidence in confidences):
        return max(confidences)
    return 1.0 if len(records) == 1 else 0.0
