import pytest

from extras.test_utils.factories import (
    DataCollectingTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    ProgramFactory,
)
from hope.apps.core.attributes_qet_queries import get_collector_has_valid_phone_no_query
from hope.apps.household.const import ROLE_ALTERNATE
from hope.models import DataCollectingType, Household, Individual

pytestmark = pytest.mark.django_db


def _set_phone_validity(individual_id: str, *, primary: bool, alternative: bool) -> None:
    Individual.objects.filter(pk=individual_id).update(
        phone_no_valid=primary, phone_no_alternative_valid=alternative
    )


def _filtered_pks(arg: bool) -> set:
    return set(
        Household.objects.filter(get_collector_has_valid_phone_no_query(None, [arg])).values_list("pk", flat=True)
    )


def test_includes_when_primary_or_alternative_phone_valid() -> None:
    # HouseholdFactory creates the head_of_household as the ROLE_PRIMARY collector.
    hh_primary = HouseholdFactory()
    _set_phone_validity(hh_primary.head_of_household_id, primary=True, alternative=False)

    hh_alternative = HouseholdFactory()
    _set_phone_validity(hh_alternative.head_of_household_id, primary=False, alternative=True)

    hh_invalid = HouseholdFactory()
    _set_phone_validity(hh_invalid.head_of_household_id, primary=False, alternative=False)

    included = _filtered_pks(True)
    assert hh_primary.pk in included
    assert hh_alternative.pk in included
    assert hh_invalid.pk not in included


def test_false_argument_is_the_exact_complement() -> None:
    hh_valid = HouseholdFactory()
    _set_phone_validity(hh_valid.head_of_household_id, primary=True, alternative=False)

    hh_invalid = HouseholdFactory()
    _set_phone_validity(hh_invalid.head_of_household_id, primary=False, alternative=False)

    excluded = _filtered_pks(False)
    assert hh_invalid.pk in excluded
    assert hh_valid.pk not in excluded


def test_checks_collector_not_just_any_member() -> None:
    # Collector has an INVALID phone, but a non-collector member has a valid one -> excluded.
    hh = HouseholdFactory()
    _set_phone_validity(hh.head_of_household_id, primary=False, alternative=False)
    IndividualFactory(
        household=hh,
        business_area=hh.business_area,
        program=hh.program,
        registration_data_import=hh.registration_data_import,
        phone_no_valid=True,
    )

    assert hh.pk not in _filtered_pks(True)


def test_follows_the_collector_role_not_the_head_of_household() -> None:
    # Head has an invalid phone; a distinct ROLE_PRIMARY collector has a valid one -> included.
    hh = HouseholdFactory()
    _set_phone_validity(hh.head_of_household_id, primary=False, alternative=False)
    collector = IndividualFactory(
        household=hh,
        business_area=hh.business_area,
        program=hh.program,
        registration_data_import=hh.registration_data_import,
        phone_no_valid=True,
    )
    hh.individuals_and_roles.all().delete()
    IndividualRoleInHouseholdFactory(household=hh, individual=collector)

    assert hh.pk in _filtered_pks(True)


def test_includes_when_alternate_collector_has_valid_phone() -> None:
    # Primary collector invalid, a distinct ALTERNATE collector valid -> included (primary+alternate).
    hh = HouseholdFactory()
    _set_phone_validity(hh.head_of_household_id, primary=False, alternative=False)
    alternate = IndividualFactory(
        household=hh,
        business_area=hh.business_area,
        program=hh.program,
        registration_data_import=hh.registration_data_import,
        phone_no_valid=True,
    )
    IndividualRoleInHouseholdFactory(household=hh, individual=alternate, role=ROLE_ALTERNATE)

    assert hh.pk in _filtered_pks(True)


def test_works_for_social_worker_people_program() -> None:
    # People (social-worker) programs use the same household + ROLE_PRIMARY structure;
    # the query is program-agnostic, so it filters them identically.
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.SOCIAL)
    program = ProgramFactory(data_collecting_type=dct)
    assert program.is_social_worker_program is True

    hh_valid = HouseholdFactory(program=program, business_area=program.business_area)
    _set_phone_validity(hh_valid.head_of_household_id, primary=True, alternative=False)

    hh_invalid = HouseholdFactory(program=program, business_area=program.business_area)
    _set_phone_validity(hh_invalid.head_of_household_id, primary=False, alternative=False)

    included = set(
        Household.objects.filter(
            get_collector_has_valid_phone_no_query(None, [True], is_social_worker_query=True)
        ).values_list("pk", flat=True)
    )
    assert hh_valid.pk in included
    assert hh_invalid.pk not in included


def test_not_equals_comparison_inverts_the_match() -> None:
    # The SELECT_ONE field also allows NOT_EQUALS; "NOT_EQUALS has-valid" == "has not valid".
    hh_valid = HouseholdFactory()
    _set_phone_validity(hh_valid.head_of_household_id, primary=True, alternative=False)
    hh_invalid = HouseholdFactory()
    _set_phone_validity(hh_invalid.head_of_household_id, primary=False, alternative=False)

    pks = set(
        Household.objects.filter(
            get_collector_has_valid_phone_no_query("NOT_EQUALS", [True])
        ).values_list("pk", flat=True)
    )
    assert hh_invalid.pk in pks
    assert hh_valid.pk not in pks
