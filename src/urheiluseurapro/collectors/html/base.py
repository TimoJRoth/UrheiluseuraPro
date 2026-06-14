"""HTML-pohjaisten collectorien abstrakti perusluokka."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from bs4 import BeautifulSoup

from urheiluseurapro.collectors.http.base import HttpCollector
from urheiluseurapro.collectors.http.client import HttpClient
from urheiluseurapro.collectors.http.metadata import HttpFetchMetadata
from urheiluseurapro.collectors.html.errors import HtmlParseError
from urheiluseurapro.collectors.html.parser import parse_html
from urheiluseurapro.collectors.html.robots import RobotsChecker
from urheiluseurapro.config import Settings
from urheiluseurapro.models.collector import CollectorResult
from urheiluseurapro.models.contact_person import ObservationContactPerson
from urheiluseurapro.models.source_config import SourceConfig
from urheiluseurapro.normalizers import normalize_club_record
from urheiluseurapro.sources.registry import SourceConfigRegistry


class HtmlCollector(HttpCollector):
    """
    Perusluokka HTML-sivujen ingestoreille.

    Tarjoaa HTTP-haun (SourceConfig-asetukset), robots.txt-tarkistuksen,
    BeautifulSoup-parsinnan ja yhtenäisen provenience-rakenteen.

    Aliluokat toteuttavat `parse_records`-metodin, joka poimii seuratietueet
    HTML-dokumentista. Ei selainautomaatiota – vain HTTP + HTML-parsinta.
    """

    def __init__(
        self,
        *,
        source_config: SourceConfig | None = None,
        source_registry: SourceConfigRegistry | None = None,
        settings: Settings | None = None,
        http_client: HttpClient | None = None,
        feed_url: str | None = None,
        respect_robots_txt: bool = True,
        robots_checker: RobotsChecker | None = None,
    ) -> None:
        super().__init__(
            source_config=source_config,
            source_registry=source_registry,
            settings=settings,
            http_client=http_client,
            feed_url=feed_url,
        )
        self._respect_robots_txt = respect_robots_txt
        self._robots_checker = robots_checker

    async def fetch_html(
        self,
        url: str | None = None,
    ) -> tuple[BeautifulSoup, HttpFetchMetadata, HttpClient]:
        """
        Hae HTML-sivu, tarkista robots.txt ja jäsennä BeautifulSoup-olioksi.

        Palauttaa (soup, metadata, client) jotta aliluokat voivat lukea proveniencea.
        """
        target = url or self.feed_url
        client = self._http_client or HttpClient(self._source_config)
        owns_client = self._http_client is None
        if owns_client:
            await client.__aenter__()

        try:
            if self._respect_robots_txt:
                checker = self._robots_checker or RobotsChecker(client)
                await checker.assert_allowed(target)

            text, meta = await client.get_text(target)
            soup = self.parse_html(text, url=target)
            self._last_fetch_metadata = meta
            return soup, meta, client
        except Exception:
            if owns_client:
                await client.__aexit__(None, None, None)
            raise

    @staticmethod
    def parse_html(html: str, *, url: str | None = None) -> BeautifulSoup:
        """Jäsennä HTML BeautifulSoup-olioksi."""
        return parse_html(html, url=url)

    @staticmethod
    def build_http_provenance(meta: HttpFetchMetadata) -> dict[str, Any]:
        """Yhtenäinen HTTP-provenance raw-kenttään."""
        return {
            "url": meta.url,
            "status_code": meta.status_code,
            "content_type": meta.content_type,
            "attempt": meta.attempt,
        }

    @abstractmethod
    def parse_records(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        """Aliluokka poimii seuratietueet HTML-dokumentista."""

    async def collect(self) -> list[CollectorResult]:
        soup, meta, client = await self.fetch_html()
        try:
            records = self.parse_records(soup)
            if not records:
                raise HtmlParseError(
                    f"HTML-sivulta ei löytynyt seuratietueita: {meta.url}",
                    url=meta.url,
                )
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
                "http": self.build_http_provenance(meta),
                "record": normalized,
            },
        )
