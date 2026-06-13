"""Jaetut enum-tyypit tietomalleille."""

from enum import StrEnum


class SourceCategory(StrEnum):
    """Lähderyhmä (synkronoitu sources.md:hen)."""

    FEDERATION = "lajiliitto"
    REGIONAL = "aluejarjesto"
    MUNICIPALITY = "kunta"
    NATIONAL = "valtakunnallinen"
    REGISTRY = "rekisteri"
    GRANT = "avustusrekisteri"
    FACILITY = "liikuntatila"
    BOOKING = "varausjarjestelma"
    OTHER = "muu"


class SourceFormat(StrEnum):
    HTML = "html"
    API = "api"
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


class ClubType(StrEnum):
    """Seuran/toimijan tyyppi."""

    SPORTS_CLUB = "urheiluseura"
    MULTI_SPORT = "monitoimiseura"
    SPORTS_ASSOCIATION = "liikuntaseura"
    YOUTH_CLUB = "nuorisoseura"
    RECREATION = "liikuntakerho"
    FEDERATION_MEMBER = "lajiliiton_jasen"
    ASSOCIATION = "yhdistys"
    OTHER = "muu"
    UNKNOWN = "tuntematon"


class LegalForm(StrEnum):
    REGISTERED_ASSOCIATION = "ry"
    FOUNDATION = "sr"
    LIMITED_COMPANY = "oy"
    OTHER = "muu"
    UNKNOWN = "tuntematon"


class ClubStatus(StrEnum):
    ACTIVE = "aktiivinen"
    INACTIVE = "passiivinen"
    DISSOLVED = "lakkautettu"
    UNKNOWN = "tuntematon"


class MatchConfidence(StrEnum):
    """Deduplikointiin liittyvä osuman luotettavuus."""

    EXACT = "exact"          # Y-tunnus, Suomisport-ID tms.
    HIGH = "high"            # normalisoitu nimi + kunta + laji
    MEDIUM = "medium"        # fuzzy nimi + kunta
    LOW = "low"              # vain nimi tai heikko signaali
    NO_MATCH = "no_match"


class MatchStatus(StrEnum):
    """Havainnon tila master-tietokannassa."""

    UNMATCHED = "unmatched"
    MATCHED = "matched"
    DUPLICATE = "duplicate"
    NEEDS_REVIEW = "needs_review"
    REJECTED = "rejected"


class FieldSource(StrEnum):
    """Mistä kentän arvo on peräisin merge-vaiheessa."""

    SINGLE_SOURCE = "single"
    MERGED = "merged"
    MANUAL = "manual"
    CONFLICT = "conflict"


class ContactPersonRole(StrEnum):
    """Yhteyshenkilön rooli seurassa."""

    CHAIR = "puheenjohtaja"
    SECRETARY = "sihteeri"
    MANAGING_DIRECTOR = "toiminnanjohtaja"
    TREASURER = "rahastonhoitaja"
    JUNIOR_DIRECTOR = "junioripaallikko"
    COACHING_DIRECTOR = "valmennuspaallikko"
    CONTACT = "yhteyshenkilö"
    OTHER = "muu"
