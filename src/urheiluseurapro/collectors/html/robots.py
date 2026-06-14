"""robots.txt-tarkistus HTTP-keruulle."""

from __future__ import annotations

import logging
from urllib import robotparser
from urllib.parse import ParseResult, urljoin, urlparse

from urheiluseurapro.collectors.html.errors import RobotsDisallowedError
from urheiluseurapro.collectors.http.client import HttpClient
from urheiluseurapro.collectors.http.errors import HttpStatusError

logger = logging.getLogger(__name__)

_SKIP_SCHEMES = frozenset({"mock", "file", "data"})


class RobotsChecker:
    """
    Tarkistaa robots.txt ennen HTML-hakua.

    robots.txt haetaan hostikohtaisesti ja välimuistitetaan collector-ajon ajaksi.
    Jos robots.txt puuttuu (404) tai haku epäonnistuu, pyyntö sallitaan (de facto -käytäntö).
    """

    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client
        self._user_agent = http_client.source_config.user_agent
        self._parsers: dict[str, robotparser.RobotFileParser | None] = {}

    async def assert_allowed(self, url: str) -> None:
        """Nosta RobotsDisallowedError jos User-Agent ei saa hakea URL:ia."""
        parsed = urlparse(url)
        if parsed.scheme in _SKIP_SCHEMES or not parsed.netloc:
            return

        parser = await self._get_parser(parsed)
        if parser is None:
            return

        if not parser.can_fetch(self._user_agent, url):
            robots_url = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")
            raise RobotsDisallowedError(
                f"robots.txt kieltää haun: {url} (User-Agent: {self._user_agent})",
                url=url,
                robots_url=robots_url,
            )

    async def is_allowed(self, url: str) -> bool:
        try:
            await self.assert_allowed(url)
        except RobotsDisallowedError:
            return False
        return True

    async def _get_parser(self, parsed: ParseResult) -> robotparser.RobotFileParser | None:
        host_key = f"{parsed.scheme}://{parsed.netloc}"
        if host_key in self._parsers:
            return self._parsers[host_key]

        robots_url = urljoin(host_key + "/", "/robots.txt")
        parser: robotparser.RobotFileParser | None = None

        try:
            text, _meta = await self._http_client.get_text(robots_url)
            rp = robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.parse(text.splitlines())
            parser = rp
        except HttpStatusError as exc:
            if exc.status_code == 404:
                logger.debug("robots.txt puuttuu (%s) – ei rajoituksia", robots_url)
            else:
                logger.warning(
                    "robots.txt HTTP %s (%s) – sallitaan haku",
                    exc.status_code,
                    robots_url,
                )
        except Exception as exc:
            logger.warning("robots.txt-haku epäonnistui (%s): %s – sallitaan haku", robots_url, exc)

        self._parsers[host_key] = parser
        return parser
