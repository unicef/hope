from decimal import Decimal
from tempfile import NamedTemporaryFile

import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.payment.services.top_up_amount_service import TopUpAmountTemplateService
from hope.apps.payment.xlsx.xlsx_payment_plan_base_service import XlsxPaymentPlanBaseService
from hope.models import BusinessArea, PaymentPlan, Program

pytestmark = pytest.mark.django_db()


def _open_plan(browser: HopeTestBrowser, business_area: BusinessArea, program: Program, plan: PaymentPlan) -> None:
    browser.open(f"/{business_area.slug}/programs/{program.code}/payment-module/payment-plans/{plan.pk}")
    browser.wait_for_element_visible('h5[data-cy="page-header-title"]')


def _open_top_up_dialog(browser: HopeTestBrowser) -> None:
    browser.wait_for_element_clickable('button[data-cy="button-create-topup"]').click()
    browser.wait_for_element_visible('input[data-cy="input-fixedAmount"]')
    browser.fill_date('input[name="dispersionStartDate"]', "2030-01-01")
    browser.wait_for_element_clickable('input[name="dispersionEndDate"]')
    browser.fill_date('input[name="dispersionEndDate"]', "2030-12-31")


def _amount_file_funding_first_beneficiary(source_plan: PaymentPlan) -> str:
    """Write an amount template funding only the first eligible beneficiary. Returns the file path."""
    workbook = TopUpAmountTemplateService(source_plan).generate_workbook()
    worksheet = workbook.active
    headers = [cell.value for cell in worksheet[1]]
    amount_column = headers.index(XlsxPaymentPlanBaseService.COLUMN_ENTITLEMENT_QUANTITY) + 1
    worksheet.cell(row=2, column=amount_column).value = 40
    with NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        workbook.save(tmp.name)
        return tmp.name


def test_create_top_up_from_finished_plan_with_fixed_amount(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    top_up_program: Program,
    top_up_source_plan: PaymentPlan,
) -> None:
    """A Finished plan offers Top-Up, and a fixed amount funds every eligible beneficiary."""
    _open_plan(login, business_area, top_up_program, top_up_source_plan)

    _open_top_up_dialog(login)
    amount_input = login.find_element('input[data-cy="input-fixedAmount"]')
    amount_input.click()
    amount_input.send_keys("25")
    login.wait_for_element_clickable('button[data-cy="button-submit"]').click()

    login.wait_for_text("Payment Plan Created")
    top_up = PaymentPlan.objects.get(source_payment_plan=top_up_source_plan, plan_type=PaymentPlan.PlanType.TOP_UP)
    assert top_up.payment_items.count() == 3
    assert set(top_up.payment_items.values_list("entitlement_quantity", flat=True)) == {Decimal("25.00")}


def test_create_top_up_with_amount_file_funds_only_listed_beneficiaries(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    top_up_program: Program,
    top_up_source_plan: PaymentPlan,
) -> None:
    """Uploading the template funds only the rows with an amount, and leaves the rest topped-up-able."""
    amount_file = _amount_file_funding_first_beneficiary(top_up_source_plan)
    _open_plan(login, business_area, top_up_program, top_up_source_plan)

    _open_top_up_dialog(login)
    login.choose_file('input[type="file"]', amount_file)
    login.wait_for_element_clickable('button[data-cy="button-submit"]').click()

    login.wait_for_text("Payment Plan Created")
    top_up = PaymentPlan.objects.get(source_payment_plan=top_up_source_plan, plan_type=PaymentPlan.PlanType.TOP_UP)
    assert top_up.payment_items.count() == 1
    assert top_up.payment_items.first().entitlement_quantity == Decimal("40.00")
    assert top_up_source_plan.eligible_payments_for_top_up().count() == 2


def test_top_up_button_absent_when_every_beneficiary_already_topped_up(
    login: HopeTestBrowser,
    business_area: BusinessArea,
    top_up_program: Program,
    top_up_exhausted_plan: PaymentPlan,
) -> None:
    """With nobody left to fund the button is gone, rather than failing on submit."""
    _open_plan(login, business_area, top_up_program, top_up_exhausted_plan)

    login.wait_for_element_visible('h5[data-cy="page-header-title"]')
    login.assert_element_absent('button[data-cy="button-create-topup"]')
