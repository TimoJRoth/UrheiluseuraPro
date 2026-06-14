"""MatchDecisionEngine-testit."""

from __future__ import annotations

from urheiluseurapro.resolution.decision import MatchDecisionEngine, decide_match


def _engine() -> MatchDecisionEngine:
    return MatchDecisionEngine()


def test_same_email() -> None:
    left = {"email": "info@ilves.example", "name": "Ilves ry"}
    right = {"email": "INFO@ILVES.EXAMPLE", "name": "Toinen nimi"}

    decision = decide_match(left, right)

    assert decision.confidence == 1.00
    assert decision.reasons == ["same_email"]


def test_same_website() -> None:
    left = {"website": "https://www.ilves.example", "name": "A"}
    right = {"website": "http://ilves.example/path", "name": "B"}

    decision = decide_match(left, right)

    assert decision.confidence == 0.95
    assert decision.reasons == ["same_website"]


def test_same_phone() -> None:
    left = {"phone": "+358 40 123 4567", "name": "A"}
    right = {"phone": "0401234567", "name": "B"}

    decision = decide_match(left, right)

    assert decision.confidence == 0.90
    assert decision.reasons == ["same_phone"]


def test_same_name_and_municipality() -> None:
    left = {"name": "Ilves Urheiluseura ry", "municipality": "Tampere"}
    right = {"name": "ILVES URHEILUSEURA R.Y.", "municipality": "tampere"}

    decision = decide_match(left, right)

    assert decision.confidence == 0.85
    assert decision.reasons == ["same_name", "same_municipality"]


def test_same_name_different_municipality() -> None:
    left = {"name": "Ilves Urheiluseura ry", "municipality": "Tampere"}
    right = {"name": "Ilves Urheiluseura", "municipality": "Helsinki"}

    decision = decide_match(left, right)

    assert decision.confidence == 0.70
    assert decision.reasons == ["same_name"]


def test_completely_different_clubs() -> None:
    left = {
        "name": "Ilves ry",
        "municipality": "Tampere",
        "email": "info@ilves.example",
    }
    right = {
        "name": "HJK ry",
        "municipality": "Helsinki",
        "email": "info@hjk.example",
    }

    decision = decide_match(left, right)

    assert decision.confidence == 0.0
    assert decision.reasons == []


def test_multiple_matches_at_once() -> None:
    left = {
        "name": "Ilves Urheiluseura ry",
        "municipality": "Tampere",
        "email": "info@ilves.example",
        "phone": "+358 40 111 1111",
        "website": "https://ilves.example",
    }
    right = {
        "name": "Ilves Urheiluseura",
        "municipality": "tampere",
        "email": "info@ilves.example",
        "phone": "0401111111",
        "website": "www.ilves.example",
    }

    decision = _engine().decide(left, right)

    assert decision.confidence == 1.00
    assert decision.reasons == [
        "same_email",
        "same_website",
        "same_phone",
        "same_name",
        "same_municipality",
    ]


def test_name_only_when_municipality_missing() -> None:
    left = {"name": "Ilves Urheiluseura ry"}
    right = {"name": "Ilves Urheiluseura r.y."}

    decision = decide_match(left, right)

    assert decision.confidence == 0.70
    assert decision.reasons == ["same_name"]
