import pytest

from extras.test_utils.factories import HouseholdFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import BusinessArea, Household, Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def household_with_cyrillic_head(program: Program, business_area: BusinessArea) -> Household:
    household = HouseholdFactory(business_area=business_area, program=program)
    head = household.head_of_household
    head.given_name = "Олександр"
    head.middle_name = "Іванович"
    head.family_name = "Шевченко"
    head.full_name = "Олександр Іванович Шевченко"
    head.set_names_latin()
    head.save()
    return household


def test_individual_details_show_names_with_latin_twins(
    login: HopeTestBrowser,
    program: Program,
    household_with_cyrillic_head: Household,
) -> None:
    head = household_with_cyrillic_head.head_of_household
    login.open(f"/{program.business_area.slug}/programs/{program.code}/population/individuals/{head.pk}")

    login.assert_text("Олександр Іванович Шевченко", 'div[data-cy="label-Full Name"]')
    login.assert_text(head.full_name_latin, 'div[data-cy="label-Full Name"]')
    login.assert_text("Олександр", 'div[data-cy="label-Given Name"]')
    login.assert_text(head.given_name_latin, 'div[data-cy="label-Given Name"]')
    login.assert_text("Шевченко", 'div[data-cy="label-Family Name"]')
    login.assert_text(head.family_name_latin, 'div[data-cy="label-Family Name"]')


def test_household_details_show_head_name_with_latin_twin(
    login: HopeTestBrowser,
    program: Program,
    household_with_cyrillic_head: Household,
) -> None:
    head = household_with_cyrillic_head.head_of_household
    label = f'div[data-cy="label-Head of {program.beneficiary_group.group_label}"]'
    login.open(
        f"/{program.business_area.slug}/programs/{program.code}/population/household/{household_with_cyrillic_head.pk}"
    )

    login.assert_text("Олександр Іванович Шевченко", label)
    login.assert_text(head.full_name_latin, label)
    login.assert_text(head.full_name_latin, 'tr[data-cy="household-members-row"]')
    login.assert_text(head.full_name_latin, 'tr[data-cy="collectors-row"]')


def test_individuals_list_shows_names_with_latin_twins(
    login: HopeTestBrowser,
    program: Program,
    household_with_cyrillic_head: Household,
) -> None:
    head = household_with_cyrillic_head.head_of_household
    login.open(f"/{program.business_area.slug}/programs/{program.code}/population/individuals")

    login.assert_text("Олександр Іванович Шевченко", 'tr[data-cy="individual-table-row"]')
    login.assert_text(head.full_name_latin, 'tr[data-cy="individual-table-row"]')
