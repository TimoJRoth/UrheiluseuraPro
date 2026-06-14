"""HTML-keruu – BeautifulSoup-pohjainen ingestio-kerros."""

from urheiluseurapro.collectors.html.base import HtmlCollector
from urheiluseurapro.collectors.html.errors import HtmlParseError, RobotsDisallowedError
from urheiluseurapro.collectors.html.parser import parse_html
from urheiluseurapro.collectors.html.robots import RobotsChecker

__all__ = [
    "HtmlCollector",
    "HtmlParseError",
    "RobotsChecker",
    "RobotsDisallowedError",
    "parse_html",
]
