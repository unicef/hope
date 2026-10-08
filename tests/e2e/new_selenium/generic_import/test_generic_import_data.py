import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import (
    Account,
    BusinessArea,
    Document,
    Household,
    Individual,
    Program,
    RegistrationDataImport,
    User,
)

from .conftest import SOMALIA_PROGRAM_NAME

pytestmark = pytest.mark.django_db()


def test_generic_import_creates_rdi_with_household_individual_document_and_account(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    somalia_business_area: BusinessArea,
    somalia_program: Program,
) -> None:
    with grant_permission(user_with_no_permissions, somalia_business_area, Permissions.GENERIC_IMPORT_DATA):
        browser.login(username="noperm_user", wait_for_drawer=False)
        browser.open("/api/generic-import/upload/")
        browser.select_option_by_text("#id_business_area", "Somalia")
        browser.wait_for_text(SOMALIA_PROGRAM_NAME, "#id_program")
        browser.select_option_by_text("#id_program", SOMALIA_PROGRAM_NAME)
        browser.choose_file("#id_file", f"{pytest.SELENIUM_PATH}/helpers/e2e_generic_import_somalia.xlsx")
        browser.wait_for_text("e2e_generic_import_somalia.xlsx", "#file-name-display")
        browser.click("button.submit-button")
        browser.wait_for_and_accept_alert(timeout=60)

    rdi = RegistrationDataImport.objects.get(program=somalia_program, name__contains="Generic Import")
    assert rdi.status == RegistrationDataImport.IN_REVIEW, rdi.error_message
    household = Household.all_merge_status_objects.get(registration_data_import=rdi)
    assert (household.size, household.village) == (3, "Hantiwadaag")
    individual = Individual.all_merge_status_objects.get(registration_data_import=rdi)
    assert individual.full_name == "Jan Michał Michałowski"
    assert individual.sex == "MALE"
    assert Document.all_merge_status_objects.get(individual=individual).document_number == "123"
    assert "+48603603603" in Account.all_objects.get(individual=individual).number
