"""Kerääjien abstrakti perusluokka."""

from abc import ABC, abstractmethod

from urheiluseurapro.models.observation import ClubObservation


class BaseCollector(ABC):
    """Kaikkien tietolähteiden kerääjien yhteinen rajapinta."""

    source_id: str
    display_name: str

    @abstractmethod
    async def collect(self) -> list[ClubObservation]:
        """Kerää seuratiedot lähteestä ClubObservation-havaintoina."""

    @abstractmethod
    def supports_url(self, url: str) -> bool:
        """Tunnistaa, voidaanko annettu URL käsitellä tällä kerääjällä."""
