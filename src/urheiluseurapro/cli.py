"""Komentorivikäyttöliittymä."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from urheiluseurapro import __version__
from urheiluseurapro.collectors.registry import default_registry
from urheiluseurapro.config import get_settings
from urheiluseurapro.logging_setup import setup_logging

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="urheiluseurapro",
        description="UrheiluseuraPro – suomalaisten urheiluseurojen tiedonkeruu",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    sources_parser = subparsers.add_parser(
        "sources",
        help="Listaa käytettävissä olevat tietolähteet",
    )
    sources_parser.set_defaults(func=cmd_sources)

    collect_parser = subparsers.add_parser(
        "collect",
        help="Kerää seuratiedot valitusta lähteestä",
    )
    collect_parser.add_argument(
        "source",
        help="Lähteen tunniste (ks. 'sources')",
    )
    collect_parser.add_argument(
        "--format",
        choices=["csv", "json", "both"],
        default="csv",
        help="Vientiformaatti (oletus: csv)",
    )
    collect_parser.set_defaults(func=cmd_collect)

    return parser


def cmd_sources(_: argparse.Namespace) -> int:
    registry = default_registry()
    sources = registry.list_sources()

    if not sources:
        print("Ei rekisteröityjä lähteitä vielä.")
        print("Katso sources.md ja roadmap.md seuraaville vaiheille.")
        return 0

    print("Saatavilla olevat lähteet:\n")
    for source_id, display_name in sources:
        print(f"  {source_id:<24} {display_name}")
    return 0


def cmd_collect(args: argparse.Namespace) -> int:
    settings = get_settings()
    registry = default_registry()

    try:
        from urheiluseurapro.pipeline.runner import run_collection

        clubs, paths = asyncio.run(
            run_collection(registry, args.source, settings, export_format=args.format)
        )
    except KeyError as exc:
        logger.error("%s", exc)
        return 1
    except NotImplementedError as exc:
        logger.error("%s", exc)
        return 1
    except ValueError as exc:
        logger.error("%s", exc)
        return 1

    for path in paths:
        logger.info("Tallennettu: %s (%d riviä)", path, len(clubs))
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    settings = get_settings()
    setup_logging(settings.log_level)

    sys.exit(args.func(args))
