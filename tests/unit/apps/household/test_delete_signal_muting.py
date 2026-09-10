import threading
from typing import TYPE_CHECKING

from constance.test import override_config
from django.core.cache import cache
from django.db.models.signals import pre_delete
from django.test import TestCase
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    ProgramFactory,
)
from hope.apps.household.api.caches import (
    get_household_list_program_key,
    get_individual_list_program_key,
)
from hope.apps.household.signals import population_delete_signals_muted
from hope.models import BusinessArea, Household, Program

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

pytestmark = pytest.mark.django_db

# Deleting the `households` fixture collects 3 Households plus their 3 cascaded head Individuals.
# increment_household_list_cache_version is registered on pre_delete for both senders
# (signals.py:59, :61), so the unmuted path bumps the household key 6 times;
# increment_individual_list_cache_version is Individual-only (signals.py:79), so 3 times.
UNMUTED_HOUSEHOLD_KEY_BUMPS = 6
UNMUTED_INDIVIDUAL_KEY_BUMPS = 3
# One remove_elasticsearch_documents_by_matching_ids call per row, over those same 6 rows.
UNMUTED_ES_REMOVALS = 6


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def other_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def households(program: Program) -> list[Household]:
    """Three households with no head, so they can be hard-deleted past the PROTECT on head_of_household."""
    created = [HouseholdFactory(program=program, business_area=program.business_area) for _ in range(3)]
    Household.all_objects.filter(program=program).update(head_of_household=None)
    return created


@pytest.fixture
def household(program: Program) -> Household:
    return HouseholdFactory(program=program, business_area=program.business_area)


@pytest.fixture
def mock_remove_es_documents(mocker: "MockerFixture") -> "MagicMock":
    return mocker.patch("hope.apps.utils.elasticsearch_utils.remove_elasticsearch_documents_by_matching_ids")


def test_bulk_delete_inside_block_bumps_each_cache_once(program: Program, households: list[Household]) -> None:
    cache.clear()
    initial_household_version = get_household_list_program_key(program.id)
    initial_individual_version = get_individual_list_program_key(program.id)

    with TestCase.captureOnCommitCallbacks(execute=True), population_delete_signals_muted([program.id]):
        Household.all_objects.filter(program=program).delete()

    assert get_household_list_program_key(program.id) - initial_household_version == 1
    assert get_individual_list_program_key(program.id) - initial_individual_version == 1


def test_bulk_delete_outside_block_bumps_each_cache_per_row(program: Program, households: list[Household]) -> None:
    cache.clear()
    initial_household_version = get_household_list_program_key(program.id)
    initial_individual_version = get_individual_list_program_key(program.id)

    with TestCase.captureOnCommitCallbacks(execute=True):
        Household.all_objects.filter(program=program).delete()

    assert get_household_list_program_key(program.id) - initial_household_version == UNMUTED_HOUSEHOLD_KEY_BUMPS
    assert get_individual_list_program_key(program.id) - initial_individual_version == UNMUTED_INDIVIDUAL_KEY_BUMPS


def test_block_invalidates_every_given_program(program: Program, other_program: Program) -> None:
    cache.clear()
    initial_version = get_household_list_program_key(program.id)
    initial_other_version = get_household_list_program_key(other_program.id)

    with (
        TestCase.captureOnCommitCallbacks(execute=True),
        population_delete_signals_muted([program.id, other_program.id]),
    ):
        pass

    assert get_household_list_program_key(program.id) - initial_version == 1
    assert get_household_list_program_key(other_program.id) - initial_other_version == 1


def test_repeated_program_id_invalidates_once(program: Program) -> None:
    cache.clear()
    initial_version = get_household_list_program_key(program.id)

    with (
        TestCase.captureOnCommitCallbacks(execute=True),
        population_delete_signals_muted([program.id, program.id, program.id]),
    ):
        pass

    assert get_household_list_program_key(program.id) - initial_version == 1


def test_save_inside_block_still_bumps_household_cache(program: Program, household: Household) -> None:
    cache.clear()
    initial_version = get_household_list_program_key(program.id)

    with TestCase.captureOnCommitCallbacks(execute=True), population_delete_signals_muted([program.id]):
        household.size = 5
        household.save(update_fields=["size"])

    # one bump from the unmuted post_save receiver, one from the block's own invalidation on exit
    assert get_household_list_program_key(program.id) - initial_version == 2


def test_nested_block_inner_exit_keeps_outer_muted(program: Program, households: list[Household]) -> None:
    cache.clear()
    initial_version = get_household_list_program_key(program.id)

    with TestCase.captureOnCommitCallbacks(execute=True), population_delete_signals_muted([program.id]):
        with population_delete_signals_muted([]):
            pass

        Household.all_objects.filter(program=program).delete()

    assert get_household_list_program_key(program.id) - initial_version == 1


def test_bulk_delete_after_exception_in_block_bumps_per_row(program: Program, households: list[Household]) -> None:
    with pytest.raises(RuntimeError), population_delete_signals_muted([program.id]):
        raise RuntimeError("boom")

    cache.clear()
    initial_version = get_household_list_program_key(program.id)

    with TestCase.captureOnCommitCallbacks(execute=True):
        Household.all_objects.filter(program=program).delete()

    assert get_household_list_program_key(program.id) - initial_version == UNMUTED_HOUSEHOLD_KEY_BUMPS


def test_block_does_not_mute_receivers_in_another_thread(program: Program, household: Household) -> None:
    cache.clear()

    def fire_delete_signal_in_thread() -> None:
        pre_delete.send(sender=Household, instance=household)

    with population_delete_signals_muted([program.id]):
        initial_version = get_household_list_program_key(program.id)
        thread = threading.Thread(target=fire_delete_signal_in_thread)
        thread.start()
        thread.join()

        version_after_thread = get_household_list_program_key(program.id)

    assert version_after_thread - initial_version == 1


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_bulk_delete_inside_block_skips_elasticsearch_removal(
    program: Program, households: list[Household], mock_remove_es_documents: "MagicMock"
) -> None:
    with population_delete_signals_muted([program.id]):
        Household.all_objects.filter(program=program).delete()

    mock_remove_es_documents.assert_not_called()


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_bulk_delete_outside_block_removes_from_elasticsearch_per_row(
    program: Program, households: list[Household], mock_remove_es_documents: "MagicMock"
) -> None:
    Household.all_objects.filter(program=program).delete()

    assert mock_remove_es_documents.call_count == UNMUTED_ES_REMOVALS
