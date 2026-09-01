import json
from typing import Any

import pytest

from extras.test_utils.factories import IndividualFactory, ProgramFactory
from hope.models import Individual, Program
from hope.one_time_scripts.migrate_latin_names import migrate_to_latin_names

pytestmark = pytest.mark.django_db


@pytest.fixture
def program() -> Program:
    return ProgramFactory()


@pytest.fixture
def individual_missing_latin(program: Program) -> Individual:
    individual = IndividualFactory(
        program=program,
        business_area=program.business_area,
        given_name="Анна",
        family_name="Ковальська",
        full_name="Анна Ковальська",
    )
    Individual.all_objects.filter(pk=individual.pk).update(
        full_name_latin=None,
        given_name_latin=None,
        middle_name_latin=None,
        family_name_latin="Keep Me",
    )
    return individual


@pytest.fixture
def individual_with_broken_name(program: Program) -> Individual:
    individual = IndividualFactory(
        program=program,
        business_area=program.business_area,
        given_name="12345",
        family_name="!!!",
        full_name="12345 !!!",
    )
    Individual.all_objects.filter(pk=individual.pk).update(
        full_name_latin=None,
        given_name_latin=None,
        middle_name_latin=None,
        family_name_latin=None,
    )
    return individual


def test_migrate_fills_missing_latin_and_keeps_existing(individual_missing_latin: Individual, tmp_path: Any) -> None:
    migrate_to_latin_names(failures_path=str(tmp_path / "failures.jsonl"))

    individual_missing_latin.refresh_from_db()
    assert individual_missing_latin.full_name_latin
    assert individual_missing_latin.full_name_latin.isascii()
    assert individual_missing_latin.given_name_latin
    assert individual_missing_latin.given_name_latin.isascii()
    assert individual_missing_latin.family_name_latin == "Keep Me"


def test_migrate_skips_broken_record_and_reports_it(
    individual_missing_latin: Individual,
    individual_with_broken_name: Individual,
    tmp_path: Any,
) -> None:
    failures_path = tmp_path / "failures.jsonl"

    migrate_to_latin_names(failures_path=str(failures_path))

    individual_missing_latin.refresh_from_db()
    individual_with_broken_name.refresh_from_db()
    assert individual_missing_latin.full_name_latin
    assert individual_with_broken_name.given_name_latin is None
    failures = [json.loads(line) for line in failures_path.read_text().splitlines()]
    assert len(failures) == 1
    assert failures[0]["individual_id"] == str(individual_with_broken_name.pk)
    assert failures[0]["business_area"] == individual_with_broken_name.program.business_area.slug
    assert failures[0]["reason"]
