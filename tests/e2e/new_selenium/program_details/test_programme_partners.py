import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.models import Partner, PaymentPlanPurpose, Program, User

from .conftest import choose_partner, open_create_programme_partners_step

pytestmark = pytest.mark.django_db()

PAGE_HEADER_TITLE = 'h5[data-cy="page-header-title"]'
BUTTON_SAVE = 'button[data-cy="button-save"]'
PARTNER_ACCESS = 'div[data-cy="label-Partner Access"]'
PARTNER_NAME = 'h6[data-cy="label-partner-name"]'
LISTBOX_OPTIONS = 'ul[role="listbox"] li'
FIRST_PARTNER = 'div[data-cy="select-partners[0].id"]'
SECOND_PARTNER = 'div[data-cy="select-partners[1].id"]'

SELECTED_PARTNERS = "Only Selected Partners within the business area"
ALL_PARTNERS = "All Current Partners within the business area"
NO_PARTNERS = "None of the Partners should have access"


def partner_names(browser: HopeTestBrowser) -> list[str]:
    browser.wait_for_element_visible(PARTNER_NAME)
    return [element.text.strip() for element in browser.find_elements(PARTNER_NAME)]


def test_delete_partner_while_creating_programme(purpose: PaymentPlanPurpose, login: HopeTestBrowser) -> None:
    open_create_programme_partners_step(login)
    login.select_dropdown_option("partnerAccess", SELECTED_PARTNERS)
    choose_partner(login, "UNHCR")
    login.click('button[data-cy="button-add-partner"]')
    login.wait_for_element_visible(SECOND_PARTNER)

    login.click('button[data-cy="button-delete"]')
    login.click('div[role="dialog"] button[data-cy="button-delete"]')

    login.wait_for_element_absent(SECOND_PARTNER)
    login.assert_text_not_visible("UNHCR", FIRST_PARTNER)
    choose_partner(login, "TEST")
    login.click(BUTTON_SAVE)
    login.wait_for_text("Test Programme", PAGE_HEADER_TITLE)
    login.assert_text(SELECTED_PARTNERS, PARTNER_ACCESS)
    # The details page lists every partner with a role across the business area, UNHCR included,
    # so check which partners got access to the programme itself.
    program = Program.objects.get(name="Test Programme")
    assert list(program.role_assignments.values_list("partner__name", flat=True)) == ["TEST"]


def test_partner_with_admin_area_access(
    superuser_of_unhcr: User, purpose: PaymentPlanPurpose, login: HopeTestBrowser
) -> None:
    open_create_programme_partners_step(login)
    login.select_dropdown_option("partnerAccess", SELECTED_PARTNERS)
    choose_partner(login, "UNHCR")
    login.js_click('input[type="radio"][value="ADMIN_AREA"]')
    login.wait_for_element_visible("//div[text()='Kabul']/span", by="xpath")
    login.click("//div[text()='Kabul']/span", by="xpath")
    login.click(BUTTON_SAVE)

    login.wait_for_text("Test Programme", PAGE_HEADER_TITLE)
    assert partner_names(login) == ["TEST", "UNHCR"]
    login.assert_text("1", 'div[data-cy="labelized-field-container-admin-area-1-total-count"]')
    login.assert_text("15", 'div[data-cy="label-Admin Area 2"]')


@pytest.mark.parametrize(
    "partner_access",
    [
        pytest.param(NO_PARTNERS, id="none-of-the-partners"),
        pytest.param(ALL_PARTNERS, id="all-partners-within-business-area"),
    ],
)
def test_partner_access_is_saved(purpose: PaymentPlanPurpose, login: HopeTestBrowser, partner_access: str) -> None:
    open_create_programme_partners_step(login)
    login.select_dropdown_option("partnerAccess", partner_access)
    login.click(BUTTON_SAVE)

    login.wait_for_text("Test Programme", PAGE_HEADER_TITLE)
    login.assert_text(partner_access, PARTNER_ACCESS)
    login.assert_text("Partial", 'div[data-cy="label-Data Collecting Type"]')


def test_only_partners_with_role_in_business_area_can_be_selected(
    partner_in_business_area: Partner,
    partner_without_role: Partner,
    purpose: PaymentPlanPurpose,
    login: HopeTestBrowser,
) -> None:
    open_create_programme_partners_step(login)
    login.select_dropdown_option("partnerAccess", SELECTED_PARTNERS)

    login.click(FIRST_PARTNER)

    login.wait_for_element_visible('li[data-cy="select-option-UNHCR"]')
    # textContent, because .text is empty while the menu is still fading in.
    labels = {option.get_attribute("textContent") for option in login.find_elements(LISTBOX_OPTIONS)}
    assert {"TEST", "Test Partner 1", "UNHCR"} <= labels
    assert "Test Partner 2" not in labels


def test_edit_partner_access(
    partner_in_business_area: Partner, purpose: PaymentPlanPurpose, login: HopeTestBrowser
) -> None:
    # Partners with a role across the whole business area are always listed, and
    # TEST, Test Partner 1 and UNHCR all have one, so only the access label changes.
    open_create_programme_partners_step(login, name="Test Program Partners")
    login.select_dropdown_option("partnerAccess", SELECTED_PARTNERS)
    choose_partner(login, "UNHCR")
    login.assert_text("UNHCR", FIRST_PARTNER)
    login.click(BUTTON_SAVE)
    login.wait_for_text("Test Program Partners", PAGE_HEADER_TITLE)
    login.assert_text(SELECTED_PARTNERS, PARTNER_ACCESS)
    assert partner_names(login) == ["TEST", "Test Partner 1", "UNHCR"]

    login.click('button[data-cy="button-edit-program"]')
    login.click('li[data-cy="menu-item-edit-partners"]')
    login.select_dropdown_option("partnerAccess", ALL_PARTNERS)
    login.click(BUTTON_SAVE)

    login.assert_text(ALL_PARTNERS, PARTNER_ACCESS)
    assert "/details/" in login.get_current_url()
    assert sorted(partner_names(login)) == ["TEST", "Test Partner 1", "UNHCR"]
