"""Esimerkkiseurat JSON-syötteestä (HTTP/JSON, ei HTML-scrapausta)."""

from __future__ import annotations

from typing import Any

from urheiluseurapro.collectors.http.base import HttpCollector
from urheiluseurapro.collectors.http.client import HttpClient
from urheiluseurapro.collectors.http.metadata import HttpFetchMetadata
from urheiluseurapro.config import Settings
from urheiluseurapro.models.collector import CollectorResult
from urheiluseurapro.models.contact_person import ObservationContactPerson
from urheiluseurapro.models.source_config import SourceConfig
from urheiluseurapro.normalizers import normalize_club_record
from urheiluseurapro.sources.registry import SourceConfigRegistry


class JsonFeedCollector(HttpCollector):
    """
    Ensimmäinen HTTP-pohjainen ingestori – malli tuleville lähteille.

    Hakee strukturoidun JSON-syöteen (API tai staattinen tiedosto HTTP:n yli).
    Ei HTML-parseria, ei selainautomaatiota.

    Rekisteröi collector erikseen: registry.register(JsonFeedCollector(...))
    Lähdeasetukset tulevat SourceConfigista (source_id: example-json-feed).
    """

    SOURCE_CONFIG_KEY = "example-json-feed"

    def __init__(
        self,
        *,
        source_config: SourceConfig | None = None,
        source_registry: SourceConfigRegistry | None = None,
        settings: Settings | None = None,
        http_client: HttpClient | None = None,
        feed_url: str | None = None,
    ) -> None:
        super().__init__(
            source_config=source_config,
            source_registry=source_registry,
            settings=settings,
            http_client=http_client,
            feed_url=feed_url,
        )

    async def collect(self) -> list[CollectorResult]:
        payload, client = await self.fetch_json()
        try:
            records = self.parse_club_records(payload)
            meta = self._last_fetch_metadata
            if meta is None:
                raise RuntimeError("HTTP-metadata puuttuu")
            return [self._record_to_result(record, meta) for record in records]
        finally:
            await self._close_http_client(client)

    def _record_to_result(
        self,
        record: dict[str, Any],
        meta: HttpFetchMetadata,
    ) -> CollectorResult:
        normalized = normalize_club_record(record)
        contact_persons = [
            ObservationContactPerson(
                full_name=person["full_name"],
                role=person.get("role"),
                emails=person.get("emails", []),
                phones=person.get("phones", []),
            )
            for person in normalized.get("contact_persons", [])
        ]

        source_url = record.get("source_url") or meta.url

        return self.build_result(
            name_raw=normalized["name"],
            municipality_raw=normalized.get("municipality"),
            sports_raw=normalized.get("sports", []),
            source_record_key=record.get("source_record_key"),
            source_url=source_url,
            website_raw=normalized.get("website"),
            email_raw=normalized.get("email"),
            phone_raw=normalized.get("phone"),
            address_raw=normalized.get("address"),
            contact_persons=contact_persons,
            confidence=record.get("confidence", self.default_confidence),
            fetched_at=meta.fetched_at,
            raw={
                "collector": self.source_id,
                "http": {
                    "url": meta.url,
                    "status_code": meta.status_code,
                    "content_type": meta.content_type,
                    "attempt": meta.attempt,
                },
                "record": normalized,
            },
        )

    def supports_url(self, url: str) -> bool:
        lowered = url.lower()
        base = (self.base_url or "").lower()
        return base in lowered or "example.invalid/api" in lowered
