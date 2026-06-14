"""HTML-keruun poikkeukset."""

from __future__ import annotations

from urheiluseurapro.collectors.http.errors import HttpClientError, HttpResponseError


class HtmlParseError(HttpResponseError):
    """HTML-sisällön parsinta tai poiminta epäonnistui."""


class RobotsDisallowedError(HttpClientError):
    """robots.txt kieltää pyynnön tälle URL:lle."""

    def __init__(
        self,
        message: str,
        *,
        url: str | None = None,
        robots_url: str | None = None,
    ) -> None:
        super().__init__(message, url=url)
        self.robots_url = robots_url
