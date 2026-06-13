"""HTTP-pohjaisten collectorien abstrakti perusluokka."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from urheiluseurapro.collectors.base import BaseCollector
from urheiluseurapro.collectors.http.client import HttpClient
from urheiluseurapro.collectors.http.errors import HttpResponseError
from urheiluseurapro.collectors.http.metadata import HttpFetchMetadata
from urheiluseurapro.config import Settings
from urheiluseurapro.models.collector import CollectorResult
from urheiluseurapro.models.source_config import SourceConfig
from urheiluseurapro.sources.registry import SourceConfigRegistry


class HttpCollector(BaseCollector):
    """
    Perusluokka HTTP/JSON/API-pohjaisille ingestoreille.

    Aliluokat toteuttavat `collect`-metodin käyttäen `fetch_json`-apua.
    Ei HTML-scrapausta – vain strukturoidut HTTP-vastaukset.
    """

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
        )
        self._http_client = http_client
        self._feed_url_override = feed_url
        self._last_fetch_metadata: HttpFetchMetadata | None = None

    @property
    def feed_url(self) -> str:
        if self._feed_url_override is not None:
            return self._feed_url_override
        if self._source_config.feed_url is not None:
            return self._source_config.feed_url
        raise ValueError(
            f"Lähteellä '{self.source_id}' ei ole feed_url-asetusta SourceConfigissa"
        )

    async def fetch_json(self, url: str | None = None) -> tuple[Any, HttpClient]:
        """
        Hae JSON annetusta URL:sta.

        Palauttaa (payload, client) jotta aliluokat voivat lukea metadataa.
        """
        target = url or self.feed_url
        client = self._http_client or HttpClient(self._source_config)
        if self._http_client is None:
            await client.__aenter__()
        payload, meta = await client.get_json(target)
        self._last_fetch_metadata = meta
        return payload, client

    async def _close_http_client(self, client: HttpClient) -> None:
        if self._http_client is None:
            await client.__aexit__(None, None, None)

    @staticmethod
    def parse_club_records(payload: Any) -> list[dict[str, Any]]:
        """
        Poimi seuratietueet JSON-vastauksesta.

        Tuetut muodot:
        - {"clubs": [...]}
        - [...]
        """
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            clubs = payload.get("clubs")
            if isinstance(clubs, list):
                return [item for item in clubs if isinstance(item, dict)]
        raise HttpResponseError("Odottamaton JSON-rakenne: clubs-listaa ei löytynyt")

    @abstractmethod
    async def collect(self) -> list[CollectorResult]:
        """Aliluokan toteutus."""
