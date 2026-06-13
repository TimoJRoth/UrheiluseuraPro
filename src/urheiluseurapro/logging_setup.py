"""Lokituksen konfigurointi."""

import logging

from rich.logging import RichHandler


def setup_logging(level: str = "INFO") -> None:
    """Alustaa konsolilokituksen Rich-käsittelijällä."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
        force=True,
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
