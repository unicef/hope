from collections.abc import Callable

import pytest

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    DataCollectingTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    ProgramFactory,
)
from hope.apps.core.attributes_qet_queries import get_collector_has_valid_phone_no_query
from hope.apps.household.const import ROLE_ALTERNATE, ROLE_PRIMARY
from hope.models import DataCollectingType, Household, Individual

pytestmark = pytest.mark.django_db


@pytest.fixture
def set_phone_validity() -> Callable[..., None]:
    def _set(individual_id: str, *, primary: bool, alternative: bool) -> None:
        Individual.objects.filter(pk=individual_id).update(
            phone_no_valid=primary, phone_no_alternative_valid=alternative
        )

    return _set


@pytest.fixture
def filtered_pks() -> Callable[[bool], set]:
    def _filter(arg: bool) -> set:
        return set(
            Household.objects.filter(get_collector_has_valid_phone_no_query(None, [arg])).values_list("pk", flat=True)
        )

    return _filter


@pytest.mark.parametrize(
    ("primary", "alternative", "expected_included"),
    [
        (True, False, True),
        (False, True, True),
        (False, False, False),
    ],
)
def test_includes_when_primary_or_alternative_phone_valid(
    set_phone_validity: Callable[..., None],
    filtered_pks: Callable[[bool], set],
    primary: bool,
    alternative: bool,
    expected_included: bool,
) -> None:
    hh = HouseholdFactory()
    set_phone_validity(hh.head_of_household_id, primary=primary, alternative=alternative)

    assert (hh.pk in filtered_pks(True)) is expected_included


def test_false_argument_is_the_exact_complement(
    set_phone_validity: Callable[..., None], filtered_pks: Callable[[bool], set]
) -> None:
    hh_valid = HouseholdFactory()
    set_phone_validity(hh_valid.head_of_household_id, primary=True, alternative=False)

    hh_invalid = HouseholdFactory()
    set_phone_validity(hh_invalid.head_of_household_id, primary=False, alternative=False)

    excluded = filtered_pks(False)
    assert hh_invalid.pk in excluded
    assert hh_valid.pk not in excluded


def test_checks_collector_not_just_any_member(
    set_phone_validity: Callable[..., None], filtered_pks: Callable[[bool], set]
) -> None:
    hh = HouseholdFactory()
    set_phone_validity(hh.head_of_household_id, primary=False, alternative=False)
    IndividualFactory(
        household=hh,
        business_area=hh.business_area,
        program=hh.program,
        registration_data_import=hh.registration_data_import,
        phone_no_valid=True,
    )

    assert hh.pk not in filtered_pks(True)


def test_follows_the_collector_role_not_the_head_of_household(
    set_phone_validity: Callable[..., None], filtered_pks: Callable[[bool], set]
) -> None:
    hh = HouseholdFactory(create_role=False)
    set_phone_validity(hh.head_of_household_id, primary=False, alternative=False)
    collector = IndividualFactory(
        household=hh,
        business_area=hh.business_area,
        program=hh.program,
        registration_data_import=hh.registration_data_import,
    )
    collector.phone_no_valid = True
    collector.save()
    IndividualRoleInHouseholdFactory(household=hh, individual=collector, role=ROLE_PRIMARY)
    assert collector.phone_no_valid is True
    assert hh.individuals_and_roles.count() == 1
    assert hh.pk in filtered_pks(True)


def test_includes_when_alternate_collector_has_valid_phone(
    set_phone_validity: Callable[..., None], filtered_pks: Callable[[bool], set]
) -> None:
    hh = HouseholdFactory()
    set_phone_validity(hh.head_of_household_id, primary=False, alternative=False)
    alternate = IndividualFactory(
        household=hh,
        business_area=hh.business_area,
        program=hh.program,
        registration_data_import=hh.registration_data_import,
    )
    alternate.phone_no_valid = True
    alternate.save()
    IndividualRoleInHouseholdFactory(household=hh, individual=alternate, role=ROLE_ALTERNATE)
    assert hh.pk in filtered_pks(True)


def test_works_for_social_worker_people_program(set_phone_validity: Callable[..., None]) -> None:
    beneficiary_group = BeneficiaryGroupFactory(name="Social", master_detail=False)
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.SOCIAL)
    program = ProgramFactory(data_collecting_type=dct, beneficiary_group=beneficiary_group)
    assert program.is_social_worker_program is True

    hh_valid = HouseholdFactory(program=program, business_area=program.business_area)
    set_phone_validity(hh_valid.head_of_household_id, primary=True, alternative=False)

    hh_invalid = HouseholdFactory(program=program, business_area=program.business_area)
    set_phone_validity(hh_invalid.head_of_household_id, primary=False, alternative=False)

    included = set(
        Household.objects.filter(
            get_collector_has_valid_phone_no_query(None, [True], is_social_worker_query=True)
        ).values_list("pk", flat=True)
    )
    assert hh_valid.pk in included
    assert hh_invalid.pk not in included


def test_not_equals_comparison_inverts_the_match(set_phone_validity: Callable[..., None]) -> None:
    hh_valid = HouseholdFactory()
    set_phone_validity(hh_valid.head_of_household_id, primary=True, alternative=False)
    hh_invalid = HouseholdFactory()
    set_phone_validity(hh_invalid.head_of_household_id, primary=False, alternative=False)

    pks = set(
        Household.objects.filter(get_collector_has_valid_phone_no_query("NOT_EQUALS", [True])).values_list(
            "pk", flat=True
        )
    )
    assert hh_invalid.pk in pks
    assert hh_valid.pk not in pks
