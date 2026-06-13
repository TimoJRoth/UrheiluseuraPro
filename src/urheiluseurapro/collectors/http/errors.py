"""HTTP-keruun poikkeukset."""

from __future__ import annotations


class HttpClientError(Exception):
    """HTTP-keruun yleinen virhe."""

    def __init__(self, message: str, *, url: str | None = None) -> None:
        super().__init__(message)
        self.url = url


class HttpTimeoutError(HttpClientError):
    """Pyyntö ylitti aikakatkaisun."""


class HttpStatusError(HttpClientError):
    """HTTP-vastaus ei ollut onnistunut."""

    def __init__(
        self,
        message: str,
        *,
        url: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message, url=url)
        self.status_code = status_code


class HttpResponseError(HttpClientError):
    """Vastauksen sisältö ei ollut odotetussa muodossa."""
