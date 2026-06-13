"""Uudelleenkäytettävä HTTP-asiakas collector-keruuseen."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from urheiluseurapro.collectors.http.errors import (
    HttpClientError,
    HttpResponseError,
    HttpStatusError,
    HttpTimeoutError,
)
from urheiluseurapro.collectors.http.metadata import HttpFetchMetadata
from urheiluseurapro.models.source_config import SourceConfig

logger = logging.getLogger(__name__)

_RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


class HttpClient:
    """
    HTTP-asiakas ingestoreille.

    Ominaisuudet: timeout, User-Agent, rate limiting, retry, virheenkäsittely.
    Kaikki HTTP-asetukset tulevat SourceConfigista – ei kovakoodattuja arvoja.
    """

    def __init__(
        self,
        source_config: SourceConfig,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._config = source_config
        self._transport = transport
        self._client: httpx.AsyncClient | None = None
        self._owns_client = False
        self._last_request_monotonic: float | None = None

    @property
    def source_config(self) -> SourceConfig:
        return self._config

    async def __aenter__(self) -> HttpClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._config.request_timeout,
                headers={"User-Agent": self._config.user_agent},
                follow_redirects=True,
                transport=self._transport,
            )
            self._owns_client = True
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None
            self._owns_client = False

    async def get_text(self, url: str) -> tuple[str, HttpFetchMetadata]:
        """Hae URL JSON/text-muodossa retry-logiikalla."""
        client = self._require_client()
        max_attempts = max(1, self._config.request_retries)

        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            await self._apply_rate_limit()
            try:
                response = await client.get(url)
                self._last_request_monotonic = time.monotonic()

                if response.status_code in _RETRYABLE_STATUS_CODES and attempt < max_attempts:
                    logger.warning(
                        "HTTP %s %s (yritys %d/%d) – uudelleenyritys",
                        response.status_code,
                        url,
                        attempt,
                        max_attempts,
                    )
                    await self._backoff(attempt)
                    continue

                if response.status_code >= 400:
                    raise HttpStatusError(
                        f"HTTP {response.status_code}: {url}",
                        url=url,
                        status_code=response.status_code,
                    )

                meta = HttpFetchMetadata(
                    url=str(response.url),
                    fetched_at=datetime.now(timezone.utc),
                    status_code=response.status_code,
                    content_type=response.headers.get("content-type"),
                    attempt=attempt,
                )
                return response.text, meta

            except httpx.TimeoutException as exc:
                last_error = HttpTimeoutError(f"Aikakatkaisu: {url}", url=url)
                logger.warning("HTTP timeout %s (yritys %d/%d)", url, attempt, max_attempts)
                if attempt < max_attempts:
                    await self._backoff(attempt)
                    continue
                raise last_error from exc
            except httpx.HTTPError as exc:
                last_error = HttpClientError(f"HTTP-virhe: {url} – {exc}", url=url)
                if attempt < max_attempts:
                    await self._backoff(attempt)
                    continue
                raise last_error from exc

        if last_error:
            raise last_error
        raise HttpClientError(f"HTTP-haku epäonnistui: {url}", url=url)

    async def get_json(self, url: str) -> tuple[Any, HttpFetchMetadata]:
        """Hae URL JSON-muodossa."""
        text, meta = await self.get_text(url)
        try:
            return json.loads(text), meta
        except json.JSONDecodeError as exc:
            raise HttpResponseError(
                f"JSON-parsinta epäonnistui: {url}",
                url=url,
            ) from exc

    def _require_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("HttpClient ei ole alustettu – käytä async with -lohkoa")
        return self._client

    async def _apply_rate_limit(self) -> None:
        delay = self._config.request_delay
        if delay <= 0 or self._last_request_monotonic is None:
            return
        elapsed = time.monotonic() - self._last_request_monotonic
        wait = delay - elapsed
        if wait > 0:
            await asyncio.sleep(wait)

    async def _backoff(self, attempt: int) -> None:
        backoff = self._config.retry_backoff_seconds * attempt
        if backoff > 0:
            await asyncio.sleep(backoff)
