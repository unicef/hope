import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.models import Household, Program

pytestmark = pytest.mark.django_db()


ADMIN_AREA_FIELD_LABEL = "Household resides in which admin area?"
ADMIN_AREA_OPTION = "Dehsabz - AF0102"


def test_household_data_update_admin_area_resolves_pcode_to_label(
    login: HopeTestBrowser,
    household_update_program: Program,
    household_for_update: Household,
) -> None:
    """Regression test for PR #6006.
    Adding an "Admin Area" (admin_area_title) change to a Household Data Update ticket must
    populate the value dropdown
    """
    browser = login
    program = household_update_program

    browser.open(f"/{program.business_area.slug}/programs/{program.code}/grievance/tickets/user-generated")
    browser.wait_for_text("Grievance Tickets", 'h5[data-cy="page-header-title"]', timeout=60)

    browser.click('a[data-cy="button-new-ticket"]')
    browser.select_dropdown_option("category", "Data Change")
    browser.select_dropdown_option("issueType", "Household Data Update")
    browser.click('button[data-cy="button-submit"]')

    browser.wait_for_ready_state_complete()
    browser.wait_for_element_visible('[data-cy="input-radio-household"]').click()
    browser.click('button[data-cy="button-submit"]')

    browser.wait_for_ready_state_complete()
    browser.click('[data-cy="input-consent"]')
    browser.click('button[data-cy="button-submit"]')

    browser.type('textarea[name="description"]', "Admin area update regression #6006")
    browser.select_dropdown_option("householdDataUpdateFields[0].fieldName", ADMIN_AREA_FIELD_LABEL)

    admin_area_input = f'//label[normalize-space()="{ADMIN_AREA_FIELD_LABEL}"]/following-sibling::div//input'
    browser.wait_for_element_visible(admin_area_input).click()
    browser.type(admin_area_input, "Dehsabz")
    browser.select_listbox_element(ADMIN_AREA_OPTION)

    browser.click('button[data-cy="button-submit"]')

    browser.wait_for_element_visible('[data-cy="table-cell-new-value"]', timeout=60)
    browser.assert_text(ADMIN_AREA_OPTION)
