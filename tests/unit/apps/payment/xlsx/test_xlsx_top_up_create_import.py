from decimal import Decimal
import io
from unittest import mock

import openpyxl
import pytest

from extras.test_utils.factories.household import HouseholdFactory
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from hope.apps.payment.celery_tasks import prepare_top_up_payment_plan_async_task
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.apps.payment.xlsx.xlsx_top_up_create_import_service import XlsxTopUpCreateImportService
from hope.models import Payment, PaymentPlan


@pytest.fixture
def source_pp(db):
    return PaymentPlanFactory(plan_type=PaymentPlan.PlanType.REGULAR, name="ImportSrc PP")


@pytest.fixture
def three_eligible_payments(source_pp):
    program = source_pp.program_cycle.program
    business_area = source_pp.business_area
    payments = []
    for _ in range(3):
        household = HouseholdFactory(program=program, business_area=business_area)
        payments.append(
            PaymentFactory(parent=source_pp, household=household, status=Payment.STATUS_DISTRIBUTION_SUCCESS)
        )
    return payments


def _build_xlsx(rows: list[list], headers: list[str] | None = None) -> io.BytesIO:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = XlsxTopUpCreateImportService.TITLE
    ws.append(headers or ["household_unicef_id", "entitlement_quantity"])
    for row in rows:
        ws.append(row)
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def test_parse_arrange_two_positive_one_zero_act_parse_assert_dict_skips_zero(source_pp, three_eligible_payments):
    hh_a, hh_b, hh_c = (p.household.unicef_id for p in three_eligible_payments)
    file = _build_xlsx([[hh_a, "100"], [hh_b, "0"], [hh_c, "75"]])

    service = XlsxTopUpCreateImportService(source_pp, file)
    amounts = service.parse_and_validate()

    assert amounts == {hh_a: Decimal(100), hh_c: Decimal(75)}
    assert service.errors == []


def test_parse_arrange_unknown_household_act_parse_assert_error(source_pp, three_eligible_payments):
    hh_known = three_eligible_payments[0].household.unicef_id
    file = _build_xlsx([[hh_known, "100"], ["HH-FAKE-9999", "50"]])

    service = XlsxTopUpCreateImportService(source_pp, file)
    amounts = service.parse_and_validate()

    assert amounts == {}
    assert any("not eligible" in error.message for error in service.errors)


def test_parse_arrange_negative_amount_act_parse_assert_error(source_pp, three_eligible_payments):
    hh = three_eligible_payments[0].household.unicef_id
    file = _build_xlsx([[hh, "-10"]])

    service = XlsxTopUpCreateImportService(source_pp, file)
    amounts = service.parse_and_validate()

    assert amounts == {}
    assert any("non-negative" in error.message for error in service.errors)


def test_parse_arrange_missing_entitlement_column_act_parse_assert_error(source_pp, three_eligible_payments):
    file = _build_xlsx(
        [[three_eligible_payments[0].household.unicef_id]],
        headers=["household_unicef_id"],
    )

    service = XlsxTopUpCreateImportService(source_pp, file)
    amounts = service.parse_and_validate()

    assert amounts == {}
    assert any("entitlement_quantity" in error.message for error in service.errors)


def test_parse_arrange_missing_key_column_act_parse_assert_error(source_pp, three_eligible_payments):
    file = _build_xlsx([["100"]], headers=["entitlement_quantity"])

    service = XlsxTopUpCreateImportService(source_pp, file)
    amounts = service.parse_and_validate()

    assert amounts == {}
    assert any("household_unicef_id" in error.message for error in service.errors)


def test_parse_arrange_all_zero_amounts_act_parse_assert_error(source_pp, three_eligible_payments):
    rows = [[p.household.unicef_id, "0"] for p in three_eligible_payments]
    file = _build_xlsx(rows)

    service = XlsxTopUpCreateImportService(source_pp, file)
    amounts = service.parse_and_validate()

    assert amounts == {}
    assert any("positive" in error.message for error in service.errors)


def test_parse_arrange_malformed_xlsx_act_parse_assert_error(source_pp):
    bogus = io.BytesIO(b"not actually xlsx bytes")

    service = XlsxTopUpCreateImportService(source_pp, bogus)
    amounts = service.parse_and_validate()

    assert amounts == {}
    assert any("Unable to open workbook" in error.message for error in service.errors)


def test_parse_arrange_duplicate_household_row_act_parse_assert_error(source_pp, three_eligible_payments):
    hh = three_eligible_payments[0].household.unicef_id
    file = _build_xlsx([[hh, "100"], [hh, "200"]])

    service = XlsxTopUpCreateImportService(source_pp, file)
    amounts = service.parse_and_validate()

    assert amounts == {}
    assert any("Duplicate row" in error.message for error in service.errors)


@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
def test_parse_then_create_top_up_arrange_two_positive_act_full_flow_assert_payments_created(
    get_exchange_rate_mock,
    source_pp,
    three_eligible_payments,
    django_capture_on_commit_callbacks,
):
    hh_a, hh_b, hh_c = (p.household.unicef_id for p in three_eligible_payments)
    file = _build_xlsx([[hh_a, "100"], [hh_b, "0"], [hh_c, "75"]])

    service = XlsxTopUpCreateImportService(source_pp, file)
    amounts = service.parse_and_validate()

    top_up_pp = PaymentPlanService(source_pp).create_top_up(
        source_pp.created_by, source_pp.dispersion_start_date, source_pp.dispersion_end_date, amounts
    )
    with django_capture_on_commit_callbacks(execute=True):
        prepare_top_up_payment_plan_async_task(top_up_pp, amounts)

    top_up_pp.refresh_from_db()
    assert top_up_pp.payment_items.count() == 2
    entitlements = sorted(top_up_pp.payment_items.values_list("entitlement_quantity", flat=True))
    assert entitlements == [Decimal("75.00"), Decimal("100.00")]
