"""Esimerkkiseurat HTML-sivulta (HTTP + BeautifulSoup, ei selainautomaatiota)."""

from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup, Tag

from urheiluseurapro.collectors.html.base import HtmlCollector
from urheiluseurapro.collectors.html.errors import HtmlParseError
from urheiluseurapro.collectors.http.client import HttpClient
from urheiluseurapro.config import Settings
from urheiluseurapro.models.source_config import SourceConfig
from urheiluseurapro.sources.registry import SourceConfigRegistry


class ExampleHtmlCollector(HtmlCollector):
    """
    Esimerkki-HTML-collector – malli tuleville HTML-lähteille.

    Poimii seurat `<article class="club">` -elementeistä.
    Käyttää vain example.invalid -domainia testeissä – ei oikeita verkkosivuja.

    Rekisteröi collector erikseen: registry.register(ExampleHtmlCollector(...))
    """

    SOURCE_CONFIG_KEY = "example-html-page"

    def __init__(
        self,
        *,
        source_config: SourceConfig | None = None,
        source_registry: SourceConfigRegistry | None = None,
        settings: Settings | None = None,
        http_client: HttpClient | None = None,
        feed_url: str | None = None,
        respect_robots_txt: bool = True,
    ) -> None:
        super().__init__(
            source_config=source_config,
            source_registry=source_registry,
            settings=settings,
            http_client=http_client,
            feed_url=feed_url,
            respect_robots_txt=respect_robots_txt,
        )

    def parse_records(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        articles = soup.select("article.club")
        if not articles:
            raise HtmlParseError("HTML-sivulta puuttuu article.club -elementit")
        return [self._parse_club_article(article) for article in articles]

    def _parse_club_article(self, article: Tag) -> dict[str, Any]:
        name_el = article.select_one(".name")
        if name_el is None:
            raise HtmlParseError("Seura-elementistä puuttuu .name")

        sports = [li.get_text(strip=True) for li in article.select(".sports li")]
        contact_persons = [self._parse_contact_person(node) for node in article.select(".contact-person")]

        website_el = article.select_one("a.website")
        email_el = article.select_one("a.email")

        return {
            "source_record_key": article.get("data-source-record-key"),
            "source_url": article.get("data-source-url"),
            "name": name_el.get_text(strip=True),
            "municipality": self._text(article, ".municipality"),
            "sports": sports,
            "website": website_el["href"] if website_el else None,
            "email": self._href_email(email_el),
            "phone": self._text(article, ".phone"),
            "address": self._text(article, "address.address"),
            "contact_persons": contact_persons,
        }

    @staticmethod
    def _parse_contact_person(node: Tag) -> dict[str, Any]:
        name_el = node.select_one(".full-name")
        emails = [
            ExampleHtmlCollector._href_email(el)
            for el in node.select("a.email")
            if ExampleHtmlCollector._href_email(el)
        ]
        phones = [span.get_text(strip=True) for span in node.select("span.phone")]
        return {
            "full_name": name_el.get_text(strip=True) if name_el else "",
            "role": node.get("data-role"),
            "emails": emails,
            "phones": phones,
        }

    @staticmethod
    def _text(parent: Tag, selector: str) -> str | None:
        el = parent.select_one(selector)
        if el is None:
            return None
        text = el.get_text(strip=True)
        return text or None

    @staticmethod
    def _href_email(el: Tag | None) -> str | None:
        if el is None:
            return None
        href = el.get("href", "")
        if isinstance(href, str) and href.startswith("mailto:"):
            return href.removeprefix("mailto:")
        return el.get_text(strip=True) or None

    def supports_url(self, url: str) -> bool:
        lowered = url.lower()
        base = (self.base_url or "").lower()
        return base in lowered or "example.invalid/clubs" in lowered
