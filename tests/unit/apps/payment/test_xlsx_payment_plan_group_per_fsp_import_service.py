from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

import openpyxl
import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentFactory,
    PaymentHouseholdSnapshotFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.payment.xlsx.xlsx_payment_plan_group_per_fsp_import_service import (
    XlsxPaymentPlanGroupImportPerFspService,
)
from hope.models import FinancialServiceProvider, Payment, PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program_cycle(program):
    return ProgramCycleFactory(program=program)


@pytest.fixture
def fsp_one():
    return FinancialServiceProviderFactory(
        name="FSP One",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        vision_vendor_number="111111111",
    )


@pytest.fixture
def fsp_two():
    return FinancialServiceProviderFactory(
        name="FSP Two",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        vision_vendor_number="222222222",
    )


@pytest.fixture
def dm_cash():
    return DeliveryMechanismFactory(code="cash", name="Cash", payment_gateway_id="dm-cash")


@pytest.fixture
def dm_voucher():
    return DeliveryMechanismFactory(code="voucher", name="Voucher", payment_gateway_id="dm-voucher")


@pytest.fixture
def template_one(fsp_one, dm_cash):
    return FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp_one,
        delivery_mechanism=dm_cash,
        xlsx_template=FinancialServiceProviderXlsxTemplateFactory(
            columns=["payment_id", "delivered_quantity", "currency"]
        ),
    ).xlsx_template


@pytest.fixture
def template_two(fsp_two, dm_voucher):
    return FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp_two,
        delivery_mechanism=dm_voucher,
        xlsx_template=FinancialServiceProviderXlsxTemplateFactory(
            columns=["payment_id", "delivered_quantity", "entitlement_quantity"]
        ),
    ).xlsx_template


@pytest.fixture
def group_two_plans_two_fsps(
    program_cycle, business_area, fsp_one, fsp_two, dm_cash, dm_voucher, template_one, template_two
):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    plan_one = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp_one,
        delivery_mechanism=dm_cash,
        status=PaymentPlan.Status.ACCEPTED,
    )
    plan_two = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp_two,
        delivery_mechanism=dm_voucher,
        status=PaymentPlan.Status.ACCEPTED,
    )
    payment_one = PaymentFactory(
        parent=plan_one,
        financial_service_provider=fsp_one,
        delivery_type=dm_cash,
        program=plan_one.program,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("10.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment_one, snapshot_data={})
    payment_two = PaymentFactory(
        parent=plan_two,
        financial_service_provider=fsp_two,
        delivery_type=dm_voucher,
        program=plan_two.program,
        entitlement_quantity=Decimal("200.00"),
        entitlement_quantity_usd=Decimal("20.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment_two, snapshot_data={})
    return {
        "group": group,
        "plan_one": plan_one,
        "plan_two": plan_two,
        "payment_one": payment_one,
        "payment_two": payment_two,
    }


@pytest.fixture
def group_with_plan_without_template(program_cycle, business_area, fsp_one, dm_cash):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp_one,
        delivery_mechanism=dm_cash,
        status=PaymentPlan.Status.ACCEPTED,
    )
    payment = PaymentFactory(
        parent=plan,
        financial_service_provider=fsp_one,
        delivery_type=dm_cash,
        program=plan.program,
        entitlement_quantity=Decimal("100.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment, snapshot_data={})
    return {"group": group, "payment": payment}


@pytest.fixture
def group_with_open_plan(program_cycle, business_area, fsp_one, dm_cash, template_one):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    open_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp_one,
        delivery_mechanism=dm_cash,
        status=PaymentPlan.Status.OPEN,
    )
    payment = PaymentFactory(
        parent=open_plan,
        financial_service_provider=fsp_one,
        delivery_type=dm_cash,
        program=open_plan.program,
        entitlement_quantity=Decimal("100.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment, snapshot_data={})
    return group


@pytest.fixture
def group_with_xlsx_and_payment_gateway_plans(program_cycle, business_area, fsp_one, dm_cash, template_one):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    xlsx_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp_one,
        delivery_mechanism=dm_cash,
        status=PaymentPlan.Status.ACCEPTED,
    )
    pg_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp_one,
        delivery_mechanism=dm_cash,
        status=PaymentPlan.Status.ACCEPTED,
        use_payment_gateway=True,
    )
    xlsx_payment = PaymentFactory(
        parent=xlsx_plan,
        financial_service_provider=fsp_one,
        delivery_type=dm_cash,
        program=xlsx_plan.program,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("10.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=xlsx_payment, snapshot_data={})
    pg_payment = PaymentFactory(
        parent=pg_plan,
        financial_service_provider=fsp_one,
        delivery_type=dm_cash,
        program=pg_plan.program,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("10.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=pg_payment, snapshot_data={})
    return {"group": group, "pg_plan": pg_plan, "xlsx_payment": xlsx_payment, "pg_payment": pg_payment}


def _make_workbook(headers: list[str], rows: list[list]) -> BytesIO:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def test_validate_succeeds_for_correct_union_header_and_rows(group_two_plans_two_fsps):
    ctx = group_two_plans_two_fsps
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency", "entitlement_quantity"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD", ""],
            [str(ctx["payment_two"].unicef_id), Decimal("75.00"), "", Decimal("200.00")],
        ],
    )
    service = XlsxPaymentPlanGroupImportPerFspService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert service.errors == []


def test_validate_errors_when_required_column_missing(group_two_plans_two_fsps):
    ctx = group_two_plans_two_fsps
    file = _make_workbook(
        ["payment_id", "currency"],
        [[str(ctx["payment_one"].unicef_id), "USD"]],
    )
    service = XlsxPaymentPlanGroupImportPerFspService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert any("delivered_quantity" in error.message for error in service.errors)


def test_validate_errors_for_payment_id_belonging_to_no_group_plan(group_two_plans_two_fsps):
    ctx = group_two_plans_two_fsps
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00")],
            ["UNKNOWN-ID", Decimal("10.00")],
        ],
    )
    service = XlsxPaymentPlanGroupImportPerFspService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert any("UNKNOWN-ID" in error.message for error in service.errors)


def test_validate_errors_on_duplicate_payment_id(group_two_plans_two_fsps):
    ctx = group_two_plans_two_fsps
    payment_id = str(ctx["payment_one"].unicef_id)
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [
            [payment_id, Decimal("50.00")],
            [payment_id, Decimal("60.00")],
        ],
    )
    service = XlsxPaymentPlanGroupImportPerFspService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert any("multiple times" in error.message for error in service.errors)


def test_validate_errors_when_no_actual_changes(group_two_plans_two_fsps):
    ctx = group_two_plans_two_fsps
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [
            [str(ctx["payment_one"].unicef_id), ""],
        ],
    )
    service = XlsxPaymentPlanGroupImportPerFspService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert any("aren't any updates" in error.message for error in service.errors)


def test_import_payment_list_writes_delivered_quantity_per_plan(group_two_plans_two_fsps):
    ctx = group_two_plans_two_fsps
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency", "entitlement_quantity"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD", ""],
            [str(ctx["payment_two"].unicef_id), Decimal("75.00"), "", Decimal("200.00")],
        ],
    )
    service = XlsxPaymentPlanGroupImportPerFspService(ctx["group"], file)
    service.open_workbook()
    service.validate()
    assert service.errors == []
    service.import_payment_list()

    ctx["payment_one"].refresh_from_db()
    ctx["payment_two"].refresh_from_db()
    assert ctx["payment_one"].delivered_quantity == Decimal("50.00")
    assert ctx["payment_two"].delivered_quantity == Decimal("75.00")


def test_plan_without_fsp_template_is_silently_skipped(group_with_plan_without_template):
    ctx = group_with_plan_without_template
    file = _make_workbook(["payment_id", "delivered_quantity"], [])
    service = XlsxPaymentPlanGroupImportPerFspService(ctx["group"], file)
    service.open_workbook()

    assert service.eligible_plans == []
    assert str(ctx["payment"].unicef_id) not in service.payment_to_plan


def test_open_plans_are_not_indexed(group_with_open_plan):
    file = _make_workbook(["payment_id", "delivered_quantity"], [])
    service = XlsxPaymentPlanGroupImportPerFspService(group_with_open_plan, file)
    service.open_workbook()

    assert service.eligible_plans == []


def test_payment_gateway_plan_is_skipped_and_its_payments_emit_specific_error(
    group_with_xlsx_and_payment_gateway_plans,
):
    ctx = group_with_xlsx_and_payment_gateway_plans
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [
            [str(ctx["xlsx_payment"].unicef_id), Decimal("50.00")],
            [str(ctx["pg_payment"].unicef_id), Decimal("50.00")],
        ],
    )
    service = XlsxPaymentPlanGroupImportPerFspService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert ctx["pg_plan"] not in service.eligible_plans
    assert any(
        "uses payment gateway" in error.message and str(ctx["pg_payment"].unicef_id) in error.message
        for error in service.errors
    )


def test_import_rolls_back_all_plans_when_any_plan_fails(group_two_plans_two_fsps):
    ctx = group_two_plans_two_fsps
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency", "entitlement_quantity"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD", ""],
            [str(ctx["payment_two"].unicef_id), Decimal("75.00"), "", Decimal("200.00")],
        ],
    )
    before_one = ctx["payment_one"].delivered_quantity
    before_two = ctx["payment_two"].delivered_quantity

    service = XlsxPaymentPlanGroupImportPerFspService(ctx["group"], file)
    service.open_workbook()
    service.validate()
    assert service.errors == []

    plan_two_id = str(ctx["plan_two"].id)
    with (
        patch.object(
            service.per_plan_services[plan_two_id],
            "import_payment_list",
            side_effect=RuntimeError("simulated per-plan failure"),
        ),
        pytest.raises(RuntimeError, match="simulated per-plan failure"),
    ):
        service.import_payment_list()

    ctx["payment_one"].refresh_from_db()
    ctx["payment_two"].refresh_from_db()
    assert ctx["payment_one"].delivered_quantity == before_one
    assert ctx["payment_two"].delivered_quantity == before_two


def test_payment_belongs_only_to_its_own_plans_fsp_template_columns(group_two_plans_two_fsps):
    ctx = group_two_plans_two_fsps
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD"],
        ],
    )
    service = XlsxPaymentPlanGroupImportPerFspService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert service.errors == []
    service.import_payment_list()

    ctx["payment_one"].refresh_from_db()
    other = Payment.objects.get(id=ctx["payment_two"].id)
    assert ctx["payment_one"].delivered_quantity == Decimal("50.00")
    assert other.delivered_quantity != Decimal("50.00")
