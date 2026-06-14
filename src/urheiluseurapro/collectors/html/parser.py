"""HTML-parsinta BeautifulSoupilla."""

from __future__ import annotations

from bs4 import BeautifulSoup

from urheiluseurapro.collectors.html.errors import HtmlParseError


def parse_html(html: str, *, url: str | None = None) -> BeautifulSoup:
    """
    Jäsennä HTML-merkkijono BeautifulSoup-olioksi.

    Käyttää html.parser -parseria (stdlib, ei ulkoisia C-riippuvuuksia).
    """
    if not html or not html.strip():
        detail = f" URL: {url}" if url else ""
        raise HtmlParseError(f"Tyhjä HTML-vastaus.{detail}", url=url)

    return BeautifulSoup(html, "html.parser")
