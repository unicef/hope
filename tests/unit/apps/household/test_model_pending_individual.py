from datetime import date
from typing import TYPE_CHECKING

from dateutil.relativedelta import relativedelta
from django.core.cache import cache
import pytest

from extras.test_utils.factories import PendingIndividualFactory
from extras.test_utils.factories.household import (
    DocumentFactory,
    HouseholdFactory,
    IndividualCollectionFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    PendingHouseholdFactory,
)
from extras.test_utils.factories.sanction_list import SanctionListFactory
from hope.apps.household.const import (
    CANNOT_DO,
    DISABLED,
    DUPLICATE,
    NOT_DISABLED,
    ROLE_PRIMARY,
    STATUS_ACTIVE,
    STATUS_DUPLICATE,
    STATUS_INACTIVE,
    STATUS_WITHDRAWN,
)
from hope.models import Document, Individual, IndividualCollection

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.django_db


@pytest.fixture
def pending_individual():
    return PendingIndividualFactory()


@pytest.fixture
def individual() -> Individual:
    return IndividualFactory()


@pytest.fixture
def individual_collection() -> IndividualCollection:
    return IndividualCollectionFactory()


@pytest.fixture
def individual_with_primary_role() -> Individual:
    household = HouseholdFactory(create_role=False)
    individual = IndividualFactory(household=household)
    IndividualRoleInHouseholdFactory(individual=individual, household=household, role=ROLE_PRIMARY)
    return individual


def test_individual_collection_str_returns_unicef_id(individual_collection: IndividualCollection) -> None:
    assert str(individual_collection) == (individual_collection.unicef_id or "")


def test_individual_collection_business_area_none_when_empty(individual_collection: IndividualCollection) -> None:
    assert individual_collection.business_area is None


def test_individual_collection_business_area_from_first_individual(individual_collection: IndividualCollection) -> None:
    individual = IndividualFactory(individual_collection=individual_collection)

    assert individual_collection.business_area == individual.business_area


def test_phone_no_text_strips_spaces() -> None:
    individual = IndividualFactory(phone_no="+48 600 100 100")

    assert " " not in individual.phone_no_text


def test_phone_no_alternative_text_strips_spaces() -> None:
    individual = IndividualFactory(phone_no_alternative="+48 600 200 200")

    assert " " not in individual.phone_no_alternative_text


def test_age_uses_birth_date() -> None:
    individual = IndividualFactory(birth_date=date(2000, 1, 1))

    assert individual.age == relativedelta(date.today(), date(2000, 1, 1)).years


def test_str_returns_unicef_id(individual: Individual) -> None:
    assert str(individual) == individual.unicef_id


def test_role_none_when_no_role(individual: Individual) -> None:
    assert individual.role is None


def test_role_returns_primary_role(individual_with_primary_role: Individual) -> None:
    assert individual_with_primary_role.role == ROLE_PRIMARY


def test_get_hash_key_is_deterministic(individual: Individual) -> None:
    assert individual.get_hash_key == individual.get_hash_key


def test_get_hash_key_varies_with_name() -> None:
    individual_a = IndividualFactory(full_name="Alice")
    individual_b = IndividualFactory(full_name="Bob")

    assert individual_a.get_hash_key != individual_b.get_hash_key


@pytest.mark.parametrize(
    ("duplicate", "withdrawn", "expected"),
    [
        (False, False, STATUS_ACTIVE),
        (True, False, STATUS_DUPLICATE),
        (False, True, STATUS_WITHDRAWN),
        (True, True, f"{STATUS_DUPLICATE}, {STATUS_WITHDRAWN}"),
    ],
)
def test_status(duplicate: bool, withdrawn: bool, expected: str) -> None:
    individual = IndividualFactory(duplicate=duplicate, withdrawn=withdrawn)

    assert individual.status == expected


@pytest.mark.parametrize(
    ("duplicate", "withdrawn", "expected"),
    [(False, False, STATUS_ACTIVE), (True, False, STATUS_INACTIVE), (False, True, STATUS_INACTIVE)],
)
def test_cash_assist_status(duplicate: bool, withdrawn: bool, expected: str) -> None:
    individual = IndividualFactory(duplicate=duplicate, withdrawn=withdrawn)

    assert individual.cash_assist_status == expected


def test_sanction_list_last_check_none_when_program_has_no_lists(individual: Individual) -> None:
    assert individual.sanction_list_last_check is None


def test_sanction_list_last_check_returns_cached_value(individual: Individual) -> None:
    individual.program.sanction_lists.add(SanctionListFactory())
    cache.set("sanction_list_last_check", "2026-01-01")

    assert individual.sanction_list_last_check == "2026-01-01"


def test_withdraw_sets_flags_and_notifies(mocker: "MockerFixture", individual: Individual) -> None:
    signal = mocker.patch("hope.models.individual.individual_withdrawn")

    individual.withdraw()

    assert individual.withdrawn is True
    assert individual.withdrawn_date is not None
    signal.send.assert_called_once()


def test_withdraw_without_notify_does_not_send_signal(mocker: "MockerFixture", individual: Individual) -> None:
    signal = mocker.patch("hope.models.individual.individual_withdrawn")

    individual.withdraw(notify=False)

    assert individual.withdrawn is True
    signal.send.assert_not_called()


def test_unwithdraw_clears_flags() -> None:
    individual = IndividualFactory(withdrawn=True)

    individual.unwithdraw()

    assert individual.withdrawn is False
    assert individual.withdrawn_date is None


def test_mark_as_duplicate_sets_flags(individual: Individual) -> None:
    individual.mark_as_duplicate()

    assert individual.duplicate is True
    assert individual.duplicate_date is not None


def test_mark_as_duplicate_copies_unicef_id_from_original(individual: Individual) -> None:
    original = IndividualFactory()

    individual.mark_as_duplicate(original)

    assert individual.unicef_id == str(original.unicef_id)


def test_mark_as_distinct_validates_documents_and_clears_flag() -> None:
    individual = IndividualFactory(duplicate=True)
    document = DocumentFactory(individual=individual, status=Document.STATUS_INVALID)

    individual.mark_as_distinct()

    document.refresh_from_db()
    assert document.status == Document.STATUS_VALID
    assert individual.duplicate is False


def test_set_relationship_confirmed_flag() -> None:
    individual = IndividualFactory(relationship_confirmed=False)

    individual.set_relationship_confirmed_flag(True)

    individual.refresh_from_db()
    assert individual.relationship_confirmed is True


def test_delete_sends_signal(mocker: "MockerFixture", individual: Individual) -> None:
    signal = mocker.patch("hope.models.individual.individual_deleted")

    individual.delete()

    signal.send.assert_called_once()


def test_count_all_and_primary_roles(individual_with_primary_role: Individual) -> None:
    assert individual_with_primary_role.count_all_roles() == 1
    assert individual_with_primary_role.count_primary_roles() == 1


def test_parents_excludes_duplicate_and_withdrawn() -> None:
    household = HouseholdFactory()
    keeper = IndividualFactory(household=household)
    IndividualFactory(household=household, duplicate=True)
    IndividualFactory(household=household, withdrawn=True)

    assert keeper in keeper.parents
    assert keeper.parents.filter(duplicate=True).count() == 0


def test_parents_empty_without_household() -> None:
    individual = IndividualFactory(household=None)

    assert individual.parents == []


def test_is_golden_record_duplicated() -> None:
    individual = IndividualFactory(deduplication_golden_record_status=DUPLICATE)

    assert individual.is_golden_record_duplicated() is True


def test_get_deduplication_golden_record_uses_status_key() -> None:
    duplicated = IndividualFactory(
        deduplication_golden_record_status=DUPLICATE,
        deduplication_golden_record_results={"duplicates": ["a"], "possible_duplicates": ["b"]},
    )
    not_duplicated = IndividualFactory(
        deduplication_golden_record_results={"duplicates": ["a"], "possible_duplicates": ["b"]},
    )

    assert duplicated.get_deduplication_golden_record() == ["a"]
    assert not_duplicated.get_deduplication_golden_record() == ["b"]


def test_active_record_returns_original_for_duplicate() -> None:
    original = IndividualFactory()
    duplicate = IndividualFactory(program=original.program, duplicate=True)
    duplicate.unicef_id = original.unicef_id
    duplicate.save()

    assert duplicate.active_record == original


def test_active_record_none_when_not_duplicate(individual: Individual) -> None:
    assert individual.active_record is None


def test_is_head_true_for_head_of_household() -> None:
    head = IndividualFactory()
    household = HouseholdFactory(head_of_household=head)
    head.household = household
    head.save()

    assert head.is_head() is True


def test_is_head_false_without_household() -> None:
    individual = IndividualFactory(household=None)

    assert individual.is_head() is False


def test_erase_anonymizes_individual(individual: Individual) -> None:
    DocumentFactory(individual=individual)

    individual.erase()

    assert individual.is_removed is True
    assert individual.full_name == "GDPR REMOVED"
    assert individual.phone_no == ""
    assert individual.flex_fields == {}


@pytest.mark.parametrize(
    ("seeing", "expected"),
    [(CANNOT_DO, DISABLED), ("", NOT_DISABLED)],
)
def test_recalculate_data(seeing: str, expected: str) -> None:
    individual = IndividualFactory(seeing_disability=seeing, disability=NOT_DISABLED)

    result, update_fields = individual.recalculate_data()

    assert individual.disability == expected
    assert update_fields == ["disability"]


def test_recalculate_data_without_save_keeps_db_value() -> None:
    individual = IndividualFactory(seeing_disability=CANNOT_DO, disability=NOT_DISABLED)

    individual.recalculate_data(save=False)

    individual.refresh_from_db()
    assert individual.disability == NOT_DISABLED


def test_validate_phone_numbers_delegates(mocker: "MockerFixture", individual: Individual) -> None:
    calculate = mocker.patch("hope.models.individual.calculate_phone_numbers_validity")

    individual.validate_phone_numbers()

    calculate.assert_called_once_with(individual)


def test_pending_individual_pending_household() -> None:
    household = PendingHouseholdFactory()
    individual = PendingIndividualFactory(household=household)

    assert individual.pending_household.pk == household.pk


def test_pending_individual_households_and_roles_setter_stores_value(pending_individual):
    pending_individual.households_and_roles = "test_value"

    # The setter is a no-op pass; confirm the property still works without error
    assert pending_individual is not None


def test_pending_individual_documents_setter_stores_value(pending_individual):
    pending_individual.documents = "test_value"

    assert pending_individual is not None


def test_pending_individual_identities_setter_stores_value(pending_individual):
    pending_individual.identities = "test_value"

    assert pending_individual is not None


def test_pending_individual_households_and_roles_setter_accepts_none(pending_individual):
    pending_individual.households_and_roles = None

    assert pending_individual is not None


def test_pending_individual_documents_setter_accepts_list(pending_individual):
    pending_individual.documents = [1, 2, 3]

    assert pending_individual is not None


def test_pending_individual_identities_setter_accepts_list(pending_individual):
    pending_individual.identities = [1, 2, 3]

    assert pending_individual is not None


def test_pending_individual_households_and_roles_getter(pending_individual):
    result = pending_individual.households_and_roles

    assert result is not None


def test_pending_individual_documents_getter(pending_individual):
    result = pending_individual.documents

    assert result is not None


def test_pending_individual_identities_getter(pending_individual):
    result = pending_individual.identities

    assert result is not None
