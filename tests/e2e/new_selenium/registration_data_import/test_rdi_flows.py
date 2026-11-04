import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import (
    BusinessArea,
    Household,
    Individual,
    MergeStatusModel,
    Program,
    RegistrationDataImport,
    User,
)

pytestmark = pytest.mark.django_db()

VIEW_PERMISSIONS = (
    Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    Permissions.RDI_VIEW_LIST,
    Permissions.RDI_VIEW_DETAILS,
)


def rdi_list_url(program: Program) -> str:
    return f"/{program.business_area.slug}/programs/{program.code}/registration-data-import"


def rdi_details_url(rdi: RegistrationDataImport) -> str:
    return f"{rdi_list_url(rdi.program)}/{rdi.id}"


def open_import_dialog(browser: HopeTestBrowser, import_type: str) -> None:
    browser.wait_for_element_clickable('button[data-cy="button-import"]').click()
    browser.click('[data-cy="import-type-select"]')
    browser.select_option_by_name(import_type, f'li[data-cy="{import_type}-menu-item"]')


def assert_population_removed(rdi: RegistrationDataImport) -> None:
    assert not Household.all_objects.filter(registration_data_import=rdi).exists()
    assert not Individual.all_objects.filter(registration_data_import=rdi).exists()


def test_xlsx_import_goes_to_review_and_merges(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    rdi_business_area: BusinessArea,
    rdi_program: Program,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        rdi_business_area,
        *VIEW_PERMISSIONS,
        Permissions.RDI_IMPORT_DATA,
        Permissions.RDI_MERGE_IMPORT,
    ):
        browser.login(username="noperm_user")
        browser.open(rdi_list_url(rdi_program))
        open_import_dialog(browser, "excel")
        browser.choose_file(
            'input[data-cy="file-input"]', f"{pytest.SELENIUM_PATH}/helpers/rdi_import_50_hh_50_ind.xlsx"
        )
        browser.assert_text("50 Items Groups available to import", '[data-cy="number-of-households"]', timeout=60)
        browser.assert_text("208 Items available to import", '[data-cy="number-of-individuals"]')
        browser.type('input[data-cy="input-name"]', "XLSX e2e import")
        browser.wait_for_element_clickable('button[data-cy="button-import-rdi"]').click()

        browser.assert_text("IN REVIEW", 'div[data-cy="label-status"]', timeout=60)
        browser.assert_text("50", '[data-cy="label-Total Number of Items Groups"]')
        browser.assert_text("208", '[data-cy="label-Total Number of Items"]')
        browser.wait_for_element_clickable('button[data-cy="button-merge-rdi"]').click()
        browser.wait_for_element_clickable('button[data-cy="button-merge"]').click()
        browser.assert_text("MERGED", 'div[data-cy="label-status"]', timeout=60)

    rdi = RegistrationDataImport.objects.get(program=rdi_program, name="XLSX e2e import")
    assert rdi.status == RegistrationDataImport.MERGED, rdi.error_message
    households = Household.all_objects.filter(registration_data_import=rdi)
    individuals = Individual.all_objects.filter(registration_data_import=rdi)
    assert households.count() == 50
    assert individuals.count() == 208
    assert not households.exclude(rdi_merge_status=MergeStatusModel.MERGED).exists()
    assert not individuals.exclude(rdi_merge_status=MergeStatusModel.MERGED).exists()


def test_refuse_import_with_reason_removes_its_population(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    rdi_business_area: BusinessArea,
    in_review_rdi: RegistrationDataImport,
) -> None:
    with grant_permission(
        user_with_no_permissions,
        rdi_business_area,
        *VIEW_PERMISSIONS,
        Permissions.RDI_MERGE_IMPORT,
        Permissions.RDI_REFUSE_IMPORT,
    ):
        browser.login(username="noperm_user")
        browser.open(rdi_details_url(in_review_rdi))
        browser.wait_for_element_clickable('button[data-cy="button-refuse-rdi"]').click()
        browser.type('textarea[data-cy="input-refuseReason"]', "Duplicate data")
        browser.click('button[data-cy="button-save"]')
        browser.assert_text("RDI refused")
        browser.assert_text("REFUSED", 'div[data-cy="label-status"]')
        browser.assert_text("Duplicate data", '[data-cy="label-Refuse Reason"]')

    in_review_rdi.refresh_from_db()
    assert in_review_rdi.status == RegistrationDataImport.REFUSED_IMPORT
    assert in_review_rdi.refuse_reason == "Duplicate data"
    assert_population_removed(in_review_rdi)


def test_refuse_button_needs_merge_permission_too(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    rdi_business_area: BusinessArea,
    in_review_rdi: RegistrationDataImport,
) -> None:
    with grant_permission(
        user_with_no_permissions, rdi_business_area, *VIEW_PERMISSIONS, Permissions.RDI_REFUSE_IMPORT
    ):
        browser.login(username="noperm_user")
        browser.open(rdi_details_url(in_review_rdi))
        browser.assert_text("IN REVIEW", 'div[data-cy="label-status"]')
        browser.assert_elements_absent('button[data-cy="button-refuse-rdi"]', 'button[data-cy="button-merge-rdi"]')


def test_erase_failed_import_removes_its_population(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    rdi_business_area: BusinessArea,
    import_error_rdi: RegistrationDataImport,
) -> None:
    with grant_permission(
        user_with_no_permissions, rdi_business_area, *VIEW_PERMISSIONS, Permissions.RDI_REFUSE_IMPORT
    ):
        browser.login(username="noperm_user")
        browser.open(rdi_details_url(import_error_rdi))
        browser.wait_for_element_clickable('button[data-cy="button-erase-rdi"]').click()
        browser.wait_for_element_clickable('button[data-cy="button-confirm"]').click()
        browser.wait_for_element_absent('button[data-cy="button-erase-rdi"]')

    import_error_rdi.refresh_from_db()
    assert import_error_rdi.erased
    assert import_error_rdi.status == RegistrationDataImport.IMPORT_ERROR
    assert_population_removed(import_error_rdi)


def test_import_from_another_programme_population(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    rdi_business_area: BusinessArea,
    rdi_program: Program,
    source_program: Program,
) -> None:
    with grant_permission(user_with_no_permissions, rdi_business_area, *VIEW_PERMISSIONS, Permissions.RDI_IMPORT_DATA):
        browser.login(username="noperm_user")
        browser.open(rdi_list_url(rdi_program))
        open_import_dialog(browser, "program-population")
        browser.type('input[data-cy="input-name"]', "Population e2e import")
        browser.click('[data-cy="autocomplete-import-from-program"] input')
        browser.select_listbox_element(source_program.name)
        browser.click('button[data-cy="button-import-rdi"]')
        browser.assert_text("IN REVIEW", 'div[data-cy="label-status"]', timeout=60)

    rdi = RegistrationDataImport.objects.get(program=rdi_program, name="Population e2e import")
    assert rdi.status == RegistrationDataImport.IN_REVIEW, rdi.error_message
    source_ids = set(Household.objects.filter(program=source_program).values_list("unicef_id", flat=True))
    imported = Household.all_objects.filter(registration_data_import=rdi, program=rdi_program)
    assert set(imported.values_list("unicef_id", flat=True)) == source_ids
    assert len(source_ids) == 3
    assert not imported.exclude(rdi_merge_status=MergeStatusModel.PENDING).exists()
