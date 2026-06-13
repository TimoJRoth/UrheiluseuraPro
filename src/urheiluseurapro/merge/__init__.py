"""Lähteiden yhdistäminen."""

from urheiluseurapro.merge.contact_persons import (
    append_contact_person_observations,
    apply_contact_person_masters,
    get_contact_person_observations,
    normalize_contact_role,
    recompute_master_contact_persons,
)
from urheiluseurapro.merge.engine import (
    append_observation_fields,
    get_field_observations,
    merge_observation_into_club,
    observation_to_club,
    recompute_master_values,
    select_master_for_field,
)
from urheiluseurapro.merge.priorities import resolve_source_priority

__all__ = [
    "append_contact_person_observations",
    "append_observation_fields",
    "apply_contact_person_masters",
    "get_contact_person_observations",
    "get_field_observations",
    "merge_observation_into_club",
    "normalize_contact_role",
    "observation_to_club",
    "recompute_master_contact_persons",
    "recompute_master_values",
    "resolve_source_priority",
    "select_master_for_field",
]
