"""HtmlCollector- ja robots.txt-testit (MockTransport, ei oikeaa verkkoa)."""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

import httpx
import pytest

from urheiluseurapro.collectors.examples.html_page import ExampleHtmlCollector
from urheiluseurapro.collectors.html.errors import HtmlParseError, RobotsDisallowedError
from urheiluseurapro.collectors.html.parser import parse_html
from urheiluseurapro.collectors.html.robots import RobotsChecker
from urheiluseurapro.collectors.http.client import HttpClient
from urheiluseurapro.collectors.http.errors import HttpTimeoutError
from urheiluseurapro.collectors.registry import CollectorRegistry, default_registry
from urheiluseurapro.collectors.runner import run_collector
from urheiluseurapro.config import Settings
from urheiluseurapro.models.source_config import SourceConfig
from urheiluseurapro.pipeline.ingest import ingest_observations

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "data" / "fixtures"
HTML_FIXTURE = (FIXTURE_DIR / "example_clubs.html").read_text(encoding="utf-8")
ROBOTS_ALLOW = (FIXTURE_DIR / "robots_allow.txt").read_text(encoding="utf-8")
ROBOTS_DISALLOW = (FIXTURE_DIR / "robots_disallow.txt").read_text(encoding="utf-8")
PAGE_URL = "https://example.invalid/clubs"
ROBOTS_URL = "https://example.invalid/robots.txt"


def _fast_settings() -> Settings:
    return Settings(
        request_delay=0.0,
        request_retries=3,
        request_retry_backoff_seconds=0.0,
        user_agent="UrheiluseuraPro-Test-Html/0.1",
    )


def _html_source_config(**overrides: float | int | str | bool) -> SourceConfig:
    defaults: dict[str, float | int | str | bool] = {
        "source_id": "example-html-page",
        "display_name": "Esimerkki HTML-sivu",
        "enabled": True,
        "request_timeout": 5.0,
        "request_delay": 0.0,
        "request_retries": 3,
        "retry_backoff_seconds": 0.0,
        "user_agent": "UrheiluseuraPro-Test-Html/0.1",
        "confidence_default": 0.81,
        "base_url": "https://example.invalid",
        "feed_url": PAGE_URL,
    }
    return SourceConfig.from_merged(defaults, overrides)


def _mock_transport(
    *,
    html: str = HTML_FIXTURE,
    robots: str = ROBOTS_ALLOW,
    robots_status: int = 200,
    page_status: int = 200,
    page_handler: object | None = None,
) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/robots.txt":
            return httpx.Response(robots_status, text=robots, request=request)
        if path.startswith("/clubs"):
            if page_handler is not None:
                return page_handler(request)  # type: ignore[operator,no-any-return]
            return httpx.Response(
                page_status,
                text=html,
                headers={"content-type": "text/html; charset=utf-8"},
                request=request,
            )
        return httpx.Response(404, text="not found", request=request)

    return httpx.MockTransport(handler)


async def _collector_with_transport(
    transport: httpx.MockTransport,
    *,
    respect_robots_txt: bool = True,
    source_config: SourceConfig | None = None,
) -> ExampleHtmlCollector:
    config = source_config or _html_source_config()
    client = HttpClient(config, transport=transport)
    await client.__aenter__()
    return ExampleHtmlCollector(
        source_config=config,
        settings=_fast_settings(),
        http_client=client,
        respect_robots_txt=respect_robots_txt,
    )


def test_parse_html_fixture() -> None:
    soup = parse_html(HTML_FIXTURE, url=PAGE_URL)
    names = [el.get_text(strip=True) for el in soup.select("article.club .name")]
    assert "Esimerkki Urheiluseura Delta" in names
    assert len(names) == 3


def test_parse_html_empty_raises() -> None:
    with pytest.raises(HtmlParseError, match="Tyhjä"):
        parse_html("   ", url=PAGE_URL)


def test_example_html_collector_returns_three_clubs() -> None:
    transport = _mock_transport()

    async def run() -> list[str]:
        collector = await _collector_with_transport(transport)
        results = await collector.collect()
        return [r.observation.name_raw for r in results]

    names = asyncio.run(run())
    assert len(names) == 3
    assert "Esimerkki Urheiluseura Delta" in names


def test_html_collector_provenance() -> None:
    transport = _mock_transport()

    async def run() -> None:
        collector = await _collector_with_transport(transport)
        result = (await collector.collect())[0]

        assert result.source == "example-html-page"
        assert result.source_url is not None
        assert result.fetched_at is not None
        assert result.observation.source_url is not None
        assert result.observation.raw is not None
        assert result.observation.raw["http"]["url"] == PAGE_URL
        assert result.observation.raw["http"]["status_code"] == 200

    asyncio.run(run())


def test_html_collector_merge_compatible() -> None:
    transport = _mock_transport()

    async def run() -> None:
        collector = await _collector_with_transport(transport)
        return await run_collector(collector)

    summary = asyncio.run(run())
    clubs, processed = ingest_observations(summary.observations, [], sources={})
    assert len(clubs) == 3
    assert len(processed) == 3


def test_html_not_in_default_registry() -> None:
    registry = default_registry()
    sources = dict(registry.list_sources())
    assert "example-html-page" not in sources
    assert "mock" in sources


def test_html_can_be_registered_manually() -> None:
    transport = _mock_transport()

    async def setup() -> ExampleHtmlCollector:
        return await _collector_with_transport(transport)

    registry = CollectorRegistry()
    registry.register(asyncio.run(setup()))
    assert registry.get("example-html-page").source_id == "example-html-page"


def test_robots_allowed_permits_fetch() -> None:
    transport = _mock_transport(robots=ROBOTS_ALLOW)

    async def run() -> int:
        collector = await _collector_with_transport(transport)
        return len(await collector.collect())

    assert asyncio.run(run()) == 3


def test_robots_disallowed_blocks_fetch() -> None:
    transport = _mock_transport(robots=ROBOTS_DISALLOW)

    async def run() -> None:
        collector = await _collector_with_transport(transport)
        await collector.collect()

    with pytest.raises(RobotsDisallowedError) as exc_info:
        asyncio.run(run())
    assert exc_info.value.url == PAGE_URL
    assert exc_info.value.robots_url == ROBOTS_URL


def test_robots_missing_allows_fetch() -> None:
    transport = _mock_transport(robots_status=404)

    async def run() -> int:
        collector = await _collector_with_transport(transport)
        return len(await collector.collect())

    assert asyncio.run(run()) == 3


def test_robots_checker_is_allowed() -> None:
    transport = _mock_transport(robots=ROBOTS_DISALLOW)
    config = _html_source_config()

    async def run() -> bool:
        async with HttpClient(config, transport=transport) as client:
            checker = RobotsChecker(client)
            return await checker.is_allowed(PAGE_URL)

    assert asyncio.run(run()) is False


def test_respect_robots_can_be_disabled() -> None:
    transport = _mock_transport(robots=ROBOTS_DISALLOW)

    async def run() -> int:
        collector = await _collector_with_transport(transport, respect_robots_txt=False)
        return len(await collector.collect())

    assert asyncio.run(run()) == 3


def test_fetch_html_retries_on_server_error() -> None:
    attempts = 0

    def page_handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            return httpx.Response(503, request=request)
        return httpx.Response(
            200,
            text=HTML_FIXTURE,
            headers={"content-type": "text/html"},
            request=request,
        )

    transport = _mock_transport(page_handler=page_handler, robots=ROBOTS_ALLOW)

    async def run() -> int:
        collector = await _collector_with_transport(transport)
        results = await collector.collect()
        assert results[0].observation.raw is not None
        return results[0].observation.raw["http"]["attempt"]

    attempt = asyncio.run(run())
    assert attempts == 3
    assert attempt == 3


def test_http_timeout_with_retries() -> None:
    def page_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout")

    transport = _mock_transport(page_handler=page_handler, robots=ROBOTS_ALLOW)
    config = _html_source_config(request_retries=2, request_timeout=1.0)

    async def run() -> None:
        collector = await _collector_with_transport(transport, source_config=config)
        await collector.collect()

    with pytest.raises(HttpTimeoutError):
        asyncio.run(run())


def test_user_agent_from_source_config() -> None:
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.headers.get("user-agent", ""))
        path = request.url.path
        if path == "/robots.txt":
            return httpx.Response(200, text=ROBOTS_ALLOW, request=request)
        return httpx.Response(200, text=HTML_FIXTURE, request=request)

    transport = httpx.MockTransport(handler)
    config = _html_source_config(user_agent="HtmlTest-Agent/2.0")

    async def run() -> None:
        collector = await _collector_with_transport(transport, source_config=config)
        await collector.collect()

    asyncio.run(run())
    assert all(ua == "HtmlTest-Agent/2.0" for ua in seen)


def test_rate_limit_between_requests() -> None:
    timestamps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        timestamps.append(time.monotonic())
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=ROBOTS_ALLOW, request=request)
        return httpx.Response(200, text=HTML_FIXTURE, request=request)

    transport = httpx.MockTransport(handler)
    config = _html_source_config(request_delay=0.05)

    async def run() -> None:
        collector = await _collector_with_transport(transport, source_config=config)
        await collector.collect()

    asyncio.run(run())
    assert len(timestamps) >= 2
    assert timestamps[1] - timestamps[0] >= 0.04


def test_html_parse_error_when_no_clubs() -> None:
    empty_html = "<html><body><main></main></body></html>"
    transport = _mock_transport(html=empty_html)

    async def run() -> None:
        collector = await _collector_with_transport(transport)
        await collector.collect()

    with pytest.raises(HtmlParseError):
        asyncio.run(run())


def test_supports_url() -> None:
    collector = ExampleHtmlCollector(source_config=_html_source_config())
    assert collector.supports_url(PAGE_URL)
    assert not collector.supports_url("https://other.example/clubs")


def test_uses_source_config_confidence() -> None:
    transport = _mock_transport()

    async def run() -> float:
        collector = await _collector_with_transport(transport)
        result = (await collector.collect())[0]
        return result.confidence

    assert asyncio.run(run()) == 0.81


def test_html_collector_normalizes_messy_data() -> None:
    messy_html = (FIXTURE_DIR / "example_clubs_messy.html").read_text(encoding="utf-8")
    transport = _mock_transport(html=messy_html)

    async def run() -> object:
        collector = await _collector_with_transport(transport)
        return await run_collector(collector)

    summary = asyncio.run(run())
    obs = summary.observations[0]

    assert obs.name_raw == "Esimerkki Urheiluseura Messy HTML"
    assert obs.municipality_raw == "Tampere"
    assert obs.sports_raw == ["jalkapallo", "futsal"]
    assert obs.email_raw == "info@messy-html.example"
    assert obs.website_raw == "https://example.invalid/messy-html"
    assert obs.phone_raw == "+358409000001"
    assert obs.contact_persons[0].full_name == "Eeva Messy"
    assert obs.contact_persons[0].emails == ["sihteeri@messy-html.example"]
