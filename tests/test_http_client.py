"""HTTP-keruun yksikkötestit (MockTransport, ei oikeaa verkkoa)."""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

import httpx
import pytest

from urheiluseurapro.collectors.http.client import HttpClient
from urheiluseurapro.collectors.http.errors import HttpStatusError, HttpTimeoutError
from urheiluseurapro.config import Settings
from urheiluseurapro.models.source_config import SourceConfig
from urheiluseurapro.sources.registry import default_source_registry

FIXTURE_PATH = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "example_clubs.json"
FIXTURE_JSON = FIXTURE_PATH.read_text(encoding="utf-8")
FEED_URL = "https://example.invalid/api/clubs"


def _fast_source_config(**overrides: float | int | str | bool) -> SourceConfig:
    base = default_source_registry(
        Settings(
            request_delay=0.0,
            request_timeout=5.0,
            request_retries=3,
            request_retry_backoff_seconds=0.0,
            user_agent="UrheiluseuraPro-Test/0.1",
        )
    ).require("example-json-feed")
    return base.model_copy(
        update={
            "request_delay": 0.0,
            "request_timeout": 5.0,
            "request_retries": 3,
            "retry_backoff_seconds": 0.0,
            "user_agent": "UrheiluseuraPro-Test/0.1",
            **overrides,
        }
    )


def test_http_client_sets_user_agent() -> None:
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["user_agent"] = request.headers.get("user-agent", "")
        return httpx.Response(200, text='{"clubs": []}')

    transport = httpx.MockTransport(handler)
    config = _fast_source_config(user_agent="Custom-Agent/1.0")

    async def run() -> None:
        async with HttpClient(config, transport=transport) as client:
            await client.get_json(FEED_URL)

    asyncio.run(run())
    assert seen["user_agent"] == "Custom-Agent/1.0"


def test_http_client_retries_on_server_error() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            return httpx.Response(503)
        return httpx.Response(200, text=FIXTURE_JSON)

    transport = httpx.MockTransport(handler)
    config = _fast_source_config(request_retries=3)

    async def run() -> tuple[object, int]:
        async with HttpClient(config, transport=transport) as client:
            payload, meta = await client.get_json(FEED_URL)
            return payload, meta.attempt

    payload, attempt = asyncio.run(run())
    assert attempts == 3
    assert attempt == 3
    assert isinstance(payload, dict)


def test_http_client_raises_on_http_error() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(404))
    config = _fast_source_config(request_retries=1)

    async def run() -> None:
        async with HttpClient(config, transport=transport) as client:
            await client.get_json(FEED_URL)

    with pytest.raises(HttpStatusError) as exc_info:
        asyncio.run(run())
    assert exc_info.value.status_code == 404


def test_http_client_timeout_with_retries() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ReadTimeout("timeout")

    transport = httpx.MockTransport(handler)
    config = _fast_source_config(request_retries=2, request_timeout=1.0)

    async def run() -> None:
        async with HttpClient(config, transport=transport) as client:
            await client.get_json(FEED_URL)

    with pytest.raises(HttpTimeoutError):
        asyncio.run(run())
    assert attempts == 2


def test_http_client_records_fetched_at_and_source_url() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, text=FIXTURE_JSON, request=request)
    )
    config = _fast_source_config()

    async def run() -> None:
        async with HttpClient(config, transport=transport) as client:
            _, meta = await client.get_json(FEED_URL)
            assert meta.url == FEED_URL
            assert meta.status_code == 200
            assert meta.fetched_at is not None

    asyncio.run(run())


def test_http_client_rate_limit_delays_second_request() -> None:
    timestamps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        timestamps.append(time.monotonic())
        return httpx.Response(200, text='{"clubs": []}')

    transport = httpx.MockTransport(handler)
    config = _fast_source_config(request_delay=0.05)

    async def run() -> None:
        async with HttpClient(config, transport=transport) as client:
            await client.get_json(FEED_URL)
            await client.get_json(FEED_URL)

    asyncio.run(run())
    assert len(timestamps) == 2
    assert timestamps[1] - timestamps[0] >= 0.04
