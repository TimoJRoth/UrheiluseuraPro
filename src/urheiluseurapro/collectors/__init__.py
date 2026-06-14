"""Kerääjät – geneerinen ingest-arkkitehtuuri."""

from urheiluseurapro.collectors.base import BaseCollector
from urheiluseurapro.collectors.examples.html_page import ExampleHtmlCollector
from urheiluseurapro.collectors.examples.json_feed import JsonFeedCollector
from urheiluseurapro.collectors.file_import import FileImportCollector
from urheiluseurapro.collectors.html import HtmlCollector, RobotsChecker
from urheiluseurapro.collectors.http import HttpClient, HttpCollector
from urheiluseurapro.collectors.mock import MockCollector
from urheiluseurapro.collectors.registry import CollectorRegistry, default_registry
from urheiluseurapro.collectors.runner import CollectorRunSummary, run_collector
from urheiluseurapro.models.collector import CollectorResult

__all__ = [
    "BaseCollector",
    "CollectorRegistry",
    "CollectorResult",
    "CollectorRunSummary",
    "ExampleHtmlCollector",
    "FileImportCollector",
    "HtmlCollector",
    "HttpClient",
    "HttpCollector",
    "JsonFeedCollector",
    "MockCollector",
    "RobotsChecker",
    "default_registry",
    "run_collector",
]
