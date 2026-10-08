from decimal import Decimal
from pathlib import Path

import openpyxl
import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, PaymentPlan, Rule, User

pytestmark = pytest.mark.django_db()

FORMULA_SELECT = 'div[data-cy="input-entitlement-formula"]'
FORMULA_ENABLED = f"{FORMULA_SELECT} .MuiSelect-select:not(.Mui-disabled)"
FORMULA_DISABLED = f"{FORMULA_SELECT} .MuiSelect-select.Mui-disabled"
APPLY_FORMULA = 'button[data-cy="button-apply-steficon"]'
FLAT_AMOUNT_INPUT = 'div[data-cy="input-flat-amount"] input'
APPLY_FLAT_AMOUNT = 'button[data-cy="button-apply-flat-amount"]'
EXPORT_XLSX = 'button[data-cy="button-export-xlsx"]'
DOWNLOAD_XLSX = 'a[data-cy="button-download-template"]'
UPLOAD_XLSX = 'button[data-cy="button-import"]'
IMPORT_DIALOG = '[data-cy="dialog-import"]'
IMPORT_SUBMIT = 'button[data-cy="button-import-entitlement"]'
TOTAL_ENTITLED = '[data-cy="total-entitled-quantity-usd"]'
UNORE_RATE_RADIO = '[data-cy="radio-unore-exchange-rate"] input'
CUSTOM_RATE_OPTION = '[data-cy="radio-custom-exchange-rate"]'
CUSTOM_RATE_RADIO = f"{CUSTOM_RATE_OPTION} input"
CUSTOM_RATE_INPUT = 'div[data-cy="input-custom-exchange-rate"] input'
APPLY_EXCHANGE_RATE = 'button[data-cy="button-apply-exchange-rate"]'
VIEW_PERMISSIONS = (
    Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    Permissions.PM_VIEW_LIST,
    Permissions.PM_VIEW_DETAILS,
    Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS,
)


def payment_plan_url(payment_plan: PaymentPlan) -> str:
    return (
        f"/{payment_plan.business_area.slug}/programs/{payment_plan.program.code}"
        f"/payment-module/payment-plans/{payment_plan.id}"
    )


def entitlement_cell(amount: str, amount_usd: str) -> str:
    return f'//td[@data-cy="entitlement-quantity-cell"][contains(., "{amount}")][contains(., "{amount_usd}")]'


def payment_entitlements(payment_plan: PaymentPlan) -> list[tuple[Decimal, Decimal]]:
    return list(
        payment_plan.eligible_payments.order_by("unicef_id").values_list(
            "entitlement_quantity", "entitlement_quantity_usd"
        )
    )


def assert_entitlements_shown(browser: HopeTestBrowser, total: str, rows: list[tuple[str, str]]) -> None:
    browser.wait_for_text(total, TOTAL_ENTITLED)
    for amount, amount_usd in rows:
        browser.wait_for_element_visible(entitlement_cell(amount, amount_usd))


def export_entitlement_xlsx(browser: HopeTestBrowser, payment_plan: PaymentPlan) -> str:
    browser.wait_for_element_clickable(EXPORT_XLSX).click()
    browser.wait_for_text("Exporting XLSX started")
    payment_plan.refresh_from_db()
    filename = Path(payment_plan.export_file_entitlement.file.name).name
    browser.delete_downloaded_file_if_present(filename, browser=True)
    browser.wait_for_element_clickable(DOWNLOAD_XLSX).click()
    browser.assert_downloaded_file(filename, browser=True)
    return browser.get_path_of_downloaded_file(filename, browser=True)


def upload_entitlement_xlsx(browser: HopeTestBrowser, path: Path | str) -> None:
    browser.wait_for_element_clickable(UPLOAD_XLSX).click()
    browser.wait_for_element_visible(IMPORT_DIALOG)
    browser.choose_file(f'{IMPORT_DIALOG} [data-cy="file-input"]', str(path))
    browser.wait_for_element_clickable(IMPORT_SUBMIT).click()


def test_apply_entitlement_formula(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    locked_entitlement_payment_plan: PaymentPlan,
    household_size_entitlement_rule: Rule,
) -> None:
    payment_plan = locked_entitlement_payment_plan
    with grant_permission(
        user_with_no_permissions,
        business_area,
        *VIEW_PERMISSIONS,
        Permissions.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS,
    ):
        browser.login(username="noperm_user")
        browser.open(payment_plan_url(payment_plan))
        browser.wait_for_element_clickable(FORMULA_SELECT).click()
        browser.select_listbox_element(household_size_entitlement_rule.name)
        browser.wait_for_element_clickable(APPLY_FORMULA).click()
        browser.wait_for_text("Formula is executing, please wait until completed")

        assert_entitlements_shown(browser, "40 PLN (20 USD)", [("10.00", "5.00"), ("30.00", "15.00")])

    payment_plan.refresh_from_db()
    assert payment_plan.steficon_rule.rule == household_size_entitlement_rule
    assert payment_entitlements(payment_plan) == [
        (Decimal("10.00"), Decimal("5.00")),
        (Decimal("30.00"), Decimal("15.00")),
    ]


def test_apply_flat_amount(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    locked_entitlement_payment_plan: PaymentPlan,
) -> None:
    payment_plan = locked_entitlement_payment_plan
    with grant_permission(
        user_with_no_permissions,
        business_area,
        *VIEW_PERMISSIONS,
        Permissions.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS,
    ):
        browser.login(username="noperm_user")
        browser.open(payment_plan_url(payment_plan))
        browser.type(FLAT_AMOUNT_INPUT, "50")
        browser.wait_for_element_clickable(APPLY_FLAT_AMOUNT).click()
        browser.wait_for_text("Flat amount is being applied, please wait until completed")

        assert_entitlements_shown(browser, "100 PLN (50 USD)", [("50.00", "25.00")])

    payment_plan.refresh_from_db()
    assert payment_plan.flat_amount_value == Decimal("50.00")
    assert payment_entitlements(payment_plan) == [
        (Decimal("50.00"), Decimal("25.00")),
        (Decimal("50.00"), Decimal("25.00")),
    ]


def test_entitlement_xlsx_export_and_import(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    entitled_locked_payment_plan: PaymentPlan,
    tmp_path: Path,
) -> None:
    payment_plan = entitled_locked_payment_plan
    with grant_permission(
        user_with_no_permissions,
        business_area,
        *VIEW_PERMISSIONS,
        Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS,
    ):
        browser.login(username="noperm_user")
        browser.open(payment_plan_url(payment_plan))
        export_path = export_entitlement_xlsx(browser, payment_plan)

        workbook = openpyxl.load_workbook(export_path)
        worksheet = workbook["Payment Plan - Payment List"]
        headers = [cell.value for cell in worksheet[1]]
        payment_id_column = headers.index("payment_id")
        entitlement_column = headers.index("entitlement_quantity")
        rows = list(worksheet.iter_rows(min_row=2))
        assert [row[payment_id_column].value for row in rows] == ["RCPT-ENTITLEMENT-E2E-1", "RCPT-ENTITLEMENT-E2E-2"]
        assert [row[entitlement_column].value for row in rows] == [10, 30]
        rows[0][entitlement_column].value = 70
        rows[1][entitlement_column].value = 90
        upload_path = tmp_path / "entitlement_import.xlsx"
        workbook.save(upload_path)

        upload_entitlement_xlsx(browser, upload_path)
        browser.wait_for_text("Your import was successful!")
        browser.wait_for_text("entitlement_import", '[data-cy="imported-file-name"]')
        assert_entitlements_shown(browser, "160 PLN (80 USD)", [("70.00", "35.00"), ("90.00", "45.00")])

    assert payment_entitlements(payment_plan) == [
        (Decimal("70.00"), Decimal("35.00")),
        (Decimal("90.00"), Decimal("45.00")),
    ]


def test_entitlement_import_without_changes_shows_error(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    entitled_locked_payment_plan: PaymentPlan,
) -> None:
    payment_plan = entitled_locked_payment_plan
    with grant_permission(
        user_with_no_permissions,
        business_area,
        *VIEW_PERMISSIONS,
        Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS,
    ):
        browser.login(username="noperm_user")
        browser.open(payment_plan_url(payment_plan))
        export_path = export_entitlement_xlsx(browser, payment_plan)

        upload_entitlement_xlsx(browser, export_path)
        browser.wait_for_text(
            "There aren't any updates in imported file, please add changes and try again",
            f'{IMPORT_DIALOG} [data-cy="error-list"]',
        )

    assert payment_entitlements(payment_plan) == [
        (Decimal("10.00"), Decimal("5.00")),
        (Decimal("30.00"), Decimal("15.00")),
    ]


def test_custom_exchange_rate(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    entitled_open_payment_plan: PaymentPlan,
) -> None:
    payment_plan = entitled_open_payment_plan
    with grant_permission(
        user_with_no_permissions,
        business_area,
        *VIEW_PERMISSIONS,
        Permissions.PM_CUSTOM_EXCHANGE_RATE,
    ):
        browser.login(username="noperm_user")
        browser.open(payment_plan_url(payment_plan))
        browser.wait_for_element_clickable(CUSTOM_RATE_OPTION).click()
        browser.type(CUSTOM_RATE_INPUT, "4")
        browser.wait_for_element_clickable(APPLY_EXCHANGE_RATE).click()
        browser.wait_for_text("Exchange rate is being applied, please wait until completed")

        browser.wait_for_text("4", 'div[data-cy="label-FX Rate Applied"]')
        browser.wait_for_element_visible(entitlement_cell("100.00", "25.00"))
        browser.wait_for_element_visible(entitlement_cell("300.00", "75.00"))

    payment_plan.refresh_from_db()
    assert payment_plan.custom_exchange_rate is True
    assert payment_plan.exchange_rate == Decimal(4)
    assert payment_plan.custom_exchange_rate_set_by == user_with_no_permissions
    assert payment_plan.total_entitled_quantity_usd == Decimal("100.00")
    assert payment_entitlements(payment_plan) == [
        (Decimal("100.00"), Decimal("25.00")),
        (Decimal("300.00"), Decimal("75.00")),
    ]


@pytest.mark.parametrize(
    ("permission", "expected_controls"),
    [
        pytest.param(
            None,
            (FORMULA_DISABLED, f"{FLAT_AMOUNT_INPUT}:disabled", f"{UPLOAD_XLSX}:disabled"),
            id="view-only",
        ),
        pytest.param(
            Permissions.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS,
            (FORMULA_ENABLED, f"{FLAT_AMOUNT_INPUT}:enabled", f"{UPLOAD_XLSX}:disabled"),
            id="apply-formula",
        ),
        pytest.param(
            Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS,
            (FORMULA_DISABLED, f"{FLAT_AMOUNT_INPUT}:disabled", f"{UPLOAD_XLSX}:enabled"),
            id="import-xlsx",
        ),
    ],
)
def test_entitlement_actions_follow_permissions(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    entitled_locked_payment_plan: PaymentPlan,
    permission: Permissions | None,
    expected_controls: tuple[str, ...],
) -> None:
    extra_permissions = (permission,) if permission else ()
    with grant_permission(user_with_no_permissions, business_area, *VIEW_PERMISSIONS, *extra_permissions):
        browser.login(username="noperm_user")
        browser.open(payment_plan_url(entitled_locked_payment_plan))
        browser.wait_for_element_clickable(EXPORT_XLSX)
        browser.assert_elements_present(*expected_controls)


@pytest.mark.parametrize(
    ("permission", "radio_state"),
    [
        pytest.param(None, ":disabled", id="view-only"),
        pytest.param(Permissions.PM_CUSTOM_EXCHANGE_RATE, ":enabled", id="custom-exchange-rate"),
    ],
)
def test_exchange_rate_options_follow_permission(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    entitled_open_payment_plan: PaymentPlan,
    permission: Permissions | None,
    radio_state: str,
) -> None:
    extra_permissions = (permission,) if permission else ()
    with grant_permission(user_with_no_permissions, business_area, *VIEW_PERMISSIONS, *extra_permissions):
        browser.login(username="noperm_user")
        browser.open(payment_plan_url(entitled_open_payment_plan))
        browser.wait_for_element_present(f"{UNORE_RATE_RADIO}{radio_state}")
        browser.wait_for_element_present(f"{CUSTOM_RATE_RADIO}{radio_state}")
