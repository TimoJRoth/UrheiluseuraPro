"""HTTP-asiakas kerääjille."""

import asyncio
from typing import Any

import httpx

from urheiluseurapro.config import Settings


class HttpClient:
    """Yhteinen HTTP-asiakas kohtuullisella viiveellä ja aikakatkaisulla."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(
            timeout=settings.request_timeout,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        )

    async def get_text(self, url: str) -> str:
        await asyncio.sleep(self._settings.request_delay)
        response = await self._client.get(url)
        response.raise_for_status()
        return response.text

    async def get_json(self, url: str) -> Any:
        await asyncio.sleep(self._settings.request_delay)
        response = await self._client.get(url)
        response.raise_for_status()
        return response.json()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "HttpClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()
