"""Tests for check_program_indexes."""

from typing import Callable, Generator

from django.conf import settings
from django.test import override_settings
from elasticsearch import Elasticsearch
import pytest

from extras.test_utils.factories import BusinessAreaFactory, HouseholdFactory, IndividualFactory, ProgramFactory
from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.apps.household.index_management import (
    check_program_indexes,
    create_program_indexes,
    delete_program_indexes,
    populate_program_indexes,
    rebuild_program_indexes,
)
from hope.models import BusinessArea, Program

pytestmark = [
    pytest.mark.usefixtures("django_elasticsearch_setup", "enable_es_autosync"),
    pytest.mark.elasticsearch,
    pytest.mark.django_db,
]


@pytest.fixture
def enable_es_autosync() -> Generator[None, None, None]:
    with override_settings(ELASTICSEARCH_DSL_AUTOSYNC=True):
        yield


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    with override_settings(ELASTICSEARCH_DSL_AUTOSYNC=False):
        return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def es() -> Elasticsearch:
    return Elasticsearch(settings.ELASTICSEARCH_HOST)


# --- check_program_indexes ---


def test_check_program_indexes_both_counts_match(
    django_elasticsearch_setup: None, create_program_es_index: Callable, program: Program
) -> None:
    hh = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(program=program, business_area=program.business_area, household=hh)

    create_program_es_index(program)
    populate_program_indexes(str(program.id))

    ok, msg = check_program_indexes(str(program.id))

    assert ok is True
    assert msg == "Indexes exist and counts match."


def test_check_program_indexes_indexes_missing(django_elasticsearch_setup: None, program: Program) -> None:
    ok, msg = check_program_indexes(str(program.id))

    assert ok is False
    assert "does not exist" in msg


def test_check_program_indexes_individual_count_mismatch(
    django_elasticsearch_setup: None, create_program_es_index: Callable, program: Program
) -> None:
    hh = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(program=program, business_area=program.business_area, household=hh)

    create_program_es_index(program)
    populate_program_indexes(str(program.id))

    # Add a new individual to DB without re-indexing → count mismatch
    with override_settings(ELASTICSEARCH_DSL_AUTOSYNC=False):
        IndividualFactory(program=program, business_area=program.business_area, household=hh)

    ok, msg = check_program_indexes(str(program.id))

    assert ok is False
    assert "does not mach" in msg


def test_check_program_indexes_household_count_mismatch(
    django_elasticsearch_setup: None, create_program_es_index: Callable, program: Program
) -> None:
    hh = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(program=program, business_area=program.business_area, household=hh)

    create_program_es_index(program)
    populate_program_indexes(str(program.id))

    # Add a new household to DB without re-indexing → count mismatch
    with override_settings(ELASTICSEARCH_DSL_AUTOSYNC=False):
        HouseholdFactory(program=program, business_area=program.business_area)

    ok, msg = check_program_indexes(str(program.id))

    assert ok is False
    assert "does not mach" in msg


def test_check_program_indexes_empty_program(
    django_elasticsearch_setup: None, create_program_es_index: Callable, program: Program
) -> None:
    create_program_es_index(program)
    populate_program_indexes(str(program.id))

    ok, msg = check_program_indexes(str(program.id))

    assert ok is True
    assert msg == "Indexes exist and counts match."


# --- create_program_indexes ---


def test_create_program_indexes_creates_both_indexes(
    django_elasticsearch_setup: None, es: Elasticsearch, program: Program
) -> None:
    ind_doc = get_individual_doc(str(program.id))
    hh_doc = get_household_doc(str(program.id))

    assert not es.indices.exists(index=ind_doc._index._name)
    assert not es.indices.exists(index=hh_doc._index._name)

    ok, msg = create_program_indexes(str(program.id))

    assert ok is True
    assert msg == ""
    assert es.indices.exists(index=ind_doc._index._name)
    assert es.indices.exists(index=hh_doc._index._name)


def test_create_program_indexes_call_again(
    django_elasticsearch_setup: None, create_program_es_index: Callable, es: Elasticsearch, program: Program
) -> None:
    create_program_es_index(program)

    # calling again should not raise
    ok, msg = create_program_indexes(str(program.id))

    assert ok is True
    assert msg == ""


# --- delete_program_indexes ---


def test_delete_program_indexes_removes_both_indexes(
    django_elasticsearch_setup: None, create_program_es_index: Callable, es: Elasticsearch, program: Program
) -> None:
    create_program_es_index(program)
    ind_doc = get_individual_doc(str(program.id))
    hh_doc = get_household_doc(str(program.id))

    assert es.indices.exists(index=ind_doc._index._name)
    assert es.indices.exists(index=hh_doc._index._name)

    ok, msg = delete_program_indexes(str(program.id))

    assert ok is True
    assert msg == ""
    assert not es.indices.exists(index=ind_doc._index._name)
    assert not es.indices.exists(index=hh_doc._index._name)


# --- populate_program_indexes ---


def test_populate_program_indexes_indexes_data(
    django_elasticsearch_setup: None, create_program_es_index: Callable, es: Elasticsearch, program: Program
) -> None:
    hh = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(program=program, business_area=program.business_area, household=hh)

    create_program_es_index(program)

    ok, msg = populate_program_indexes(str(program.id))

    assert ok is True
    assert msg == ""
    ok, msg = check_program_indexes(str(program.id))
    assert ok is True


def test_populate_program_indexes_empty_program(
    django_elasticsearch_setup: None, create_program_es_index: Callable, program: Program
) -> None:
    create_program_es_index(program)

    ok, msg = populate_program_indexes(str(program.id))

    assert ok is True
    assert msg == ""


# --- rebuild_program_indexes ---


def test_rebuild_program_indexes(
    django_elasticsearch_setup: None, create_program_es_index: Callable, program: Program
) -> None:
    hh = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(program=program, business_area=program.business_area, household=hh)

    create_program_es_index(program)
    populate_program_indexes(str(program.id))

    # Add more data after initial index — rebuild should sync counts
    IndividualFactory(program=program, business_area=program.business_area, household=hh)

    ok, msg = rebuild_program_indexes(str(program.id))

    assert ok is True
    assert f"Rebuilt indexes for program {program.id}" in msg
    ok, msg = check_program_indexes(str(program.id))
    assert ok is True


def test_rebuild_program_indexes_from_scratch(django_elasticsearch_setup: None, program: Program) -> None:
    # no indexes exist yet - should create and populate
    hh = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(program=program, business_area=program.business_area, household=hh)

    ok, msg = rebuild_program_indexes(str(program.id))

    assert ok is True
    ok, msg = check_program_indexes(str(program.id))
    assert ok is True
