from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

from django.db import connection
from django.test.utils import CaptureQueriesContext
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
from hope.apps.payment.xlsx.xlsx_error import XlsxError
from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_import_service import XlsxPaymentPlanDeliveryImportService
from hope.apps.payment.xlsx.xlsx_payment_plan_group_delivery_import_service import (
    XlsxPaymentPlanGroupDeliveryImportService,
)
from hope.models import FinancialServiceProvider, Payment, PaymentPlan, ProgramCycle

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
def fsp():
    return FinancialServiceProviderFactory(
        name="Group FSP",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        vision_vendor_number="111111111",
    )


@pytest.fixture
def delivery_mechanism():
    return DeliveryMechanismFactory(code="cash", name="Cash", payment_gateway_id="dm-cash")


@pytest.fixture
def template(fsp, delivery_mechanism):
    return FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        xlsx_template=FinancialServiceProviderXlsxTemplateFactory(
            columns=["payment_id", "delivered_quantity", "currency"]
        ),
    ).xlsx_template


@pytest.fixture
def group_two_plans_one_fsp(program_cycle, business_area, fsp, delivery_mechanism, template):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    plan_one = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
    )
    plan_two = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
    )
    payment_one = PaymentFactory(
        parent=plan_one,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
        program=plan_one.program,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("10.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment_one, snapshot_data={})
    payment_two = PaymentFactory(
        parent=plan_two,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
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
def group_with_plan_without_template(program_cycle, business_area, fsp, delivery_mechanism):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
    )
    payment = PaymentFactory(
        parent=plan,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
        program=plan.program,
        entitlement_quantity=Decimal("100.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment, snapshot_data={})
    return {"group": group, "payment": payment}


@pytest.fixture
def group_with_open_plan(program_cycle, business_area, fsp, delivery_mechanism, template):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    open_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.OPEN,
    )
    payment = PaymentFactory(
        parent=open_plan,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
        program=open_plan.program,
        entitlement_quantity=Decimal("100.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment, snapshot_data={})
    return group


@pytest.fixture
def group_with_follow_up_and_top_up_plans(program_cycle, business_area, fsp, delivery_mechanism, template):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    regular_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
        plan_type=PaymentPlan.PlanType.REGULAR,
    )
    follow_up_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )
    return {"group": group, "regular_plan": regular_plan, "follow_up_plan": follow_up_plan}


@pytest.fixture
def group_with_xlsx_and_payment_gateway_plans(program_cycle, business_area, fsp, delivery_mechanism, template):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    xlsx_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
    )
    pg_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
        use_payment_gateway=True,
    )
    xlsx_payment = PaymentFactory(
        parent=xlsx_plan,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
        program=xlsx_plan.program,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("10.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=xlsx_payment, snapshot_data={})
    pg_payment = PaymentFactory(
        parent=pg_plan,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
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


def test_validate_succeeds_for_correct_header_and_rows(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD"],
            [str(ctx["payment_two"].unicef_id), Decimal("75.00"), "USD"],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert service.errors == []


def test_validate_errors_when_required_column_missing(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "currency"],
        [[str(ctx["payment_one"].unicef_id), "USD"]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert any("delivered_quantity" in error.message for error in service.errors)


def test_validate_errors_for_payment_id_belonging_to_no_group_plan(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00")],
            ["UNKNOWN-ID", Decimal("10.00")],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert any("UNKNOWN-ID" in error.message for error in service.errors)


def test_validate_errors_on_duplicate_payment_id(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment_id = str(ctx["payment_one"].unicef_id)
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [
            [payment_id, Decimal("50.00")],
            [payment_id, Decimal("60.00")],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert any("multiple times" in error.message for error in service.errors)


def test_validate_errors_when_no_actual_changes(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    already_delivered = ctx["payment_one"]
    already_delivered.delivered_quantity = Decimal("100.00")
    already_delivered.status = Payment.STATUS_DISTRIBUTION_SUCCESS
    already_delivered.save(update_fields=["delivered_quantity", "status"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [
            [str(already_delivered.unicef_id), Decimal("100.00")],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert any("aren't any updates" in error.message for error in service.errors)


def test_import_payment_list_writes_delivered_quantity_per_plan(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD"],
            [str(ctx["payment_two"].unicef_id), Decimal("75.00"), "USD"],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service.validate()
    assert service.errors == []
    service.import_payment_list()

    ctx["payment_one"].refresh_from_db()
    ctx["payment_two"].refresh_from_db()
    assert ctx["payment_one"].delivered_quantity == Decimal("50.00")
    assert ctx["payment_two"].delivered_quantity == Decimal("75.00")


def test_import_updates_shared_program_cycle_only_once_for_two_plans(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD"],
            [str(ctx["payment_two"].unicef_id), Decimal("75.00"), "USD"],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service.validate()
    assert service.errors == []
    cycle_table = ProgramCycle._meta.db_table

    with CaptureQueriesContext(connection) as captured:
        service.import_payment_list()

    cycle_updates = [
        query
        for query in captured.captured_queries
        if query["sql"].lstrip().upper().startswith("UPDATE") and cycle_table in query["sql"]
    ]
    assert len(cycle_updates) == 1


def test_import_payment_list_keeps_accepted_status_when_plan_not_fully_reconciled(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    PaymentFactory(
        parent=ctx["plan_one"],
        financial_service_provider=ctx["plan_one"].financial_service_provider,
        delivery_type=ctx["plan_one"].delivery_mechanism,
        program=ctx["plan_one"].program,
        entitlement_quantity=Decimal("300.00"),
        entitlement_quantity_usd=Decimal("30.00"),
        status=Payment.STATUS_PENDING,
    )
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("100.00"), "USD"],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service.validate()
    assert service.errors == []
    service.import_payment_list()

    ctx["plan_one"].refresh_from_db()
    assert ctx["plan_one"].status == PaymentPlan.Status.ACCEPTED


def test_plan_without_fsp_template_payments_still_indexed(group_with_plan_without_template):
    ctx = group_with_plan_without_template
    file = _make_workbook(["payment_id", "delivered_quantity"], [])
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    assert str(ctx["payment"].unicef_id) in service.payment_to_plan


def test_open_plans_are_not_indexed(group_with_open_plan):
    file = _make_workbook(["payment_id", "delivered_quantity"], [])
    service = XlsxPaymentPlanGroupDeliveryImportService(group_with_open_plan, file)
    service.open_workbook()

    assert service.eligible_plans == []


def test_follow_up_and_top_up_plans_are_excluded(group_with_follow_up_and_top_up_plans):
    ctx = group_with_follow_up_and_top_up_plans
    file = _make_workbook(["payment_id", "delivered_quantity"], [])
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    assert [plan.id for plan in service.payment_plans] == [ctx["regular_plan"].id]


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
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert ctx["pg_plan"] not in service.eligible_plans
    assert any(
        "uses payment gateway" in error.message and str(ctx["pg_payment"].unicef_id) in error.message
        for error in service.errors
    )


def test_import_rolls_back_all_plans_when_any_plan_fails(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD"],
            [str(ctx["payment_two"].unicef_id), Decimal("75.00"), "USD"],
        ],
    )
    before_one = ctx["payment_one"].delivered_quantity
    before_two = ctx["payment_two"].delivered_quantity

    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
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


def test_import_payment_list_builds_services_when_validate_not_called(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD"],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    service.import_payment_list()

    ctx["payment_one"].refresh_from_db()
    assert ctx["payment_one"].delivered_quantity == Decimal("50.00")


def test_validate_row_payment_ids_returns_early_without_worksheet(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(["payment_id", "delivered_quantity"], [])
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.ws = None

    service._validate_row_payment_ids()

    assert service.errors == []


def test_row_groups_by_plan_returns_empty_without_worksheet(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(["payment_id", "delivered_quantity"], [])
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.ws = None

    assert service._row_groups_by_plan() == {}


def test_rows_are_routed_only_to_their_owning_plan(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD"],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert service.errors == []
    service.import_payment_list()

    ctx["payment_one"].refresh_from_db()
    other = Payment.objects.get(id=ctx["payment_two"].id)
    assert ctx["payment_one"].delivered_quantity == Decimal("50.00")
    assert other.delivered_quantity != Decimal("50.00")


def test_validate_row_payment_ids_skips_fully_blank_rows(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    # blank row (all None) between two valid rows — should produce no additional errors
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00")],
            [],  # blank row — openpyxl appends a row of empty cells
            [str(ctx["payment_two"].unicef_id), Decimal("75.00")],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service._validate_row_payment_ids()

    assert service.errors == []


def test_validate_row_payment_ids_skips_row_with_null_payment_id(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    # row where payment_id column is None but another column has a value
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [
            [None, Decimal("50.00")],
            [str(ctx["payment_one"].unicef_id), Decimal("75.00")],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service._validate_row_payment_ids()

    assert service.errors == []


def test_row_groups_by_plan_skips_fully_blank_rows(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00")],
            [],  # blank row — skipped
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    result = service._row_groups_by_plan()

    plan_id = str(ctx["plan_one"].id)
    assert plan_id in result
    assert len(result[plan_id]) == 1  # only the valid row, not the blank one


def test_validate_collects_per_plan_header_errors(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency"],
        [[str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD"]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    def fake_validate_headers(self):
        self.errors.append(XlsxError(self.sheetname, None, "bad per-plan header"))

    with patch.object(XlsxPaymentPlanDeliveryImportService, "_validate_headers", fake_validate_headers):
        service.validate()

    assert any("bad per-plan header" in error.message for error in service.errors)


def test_row_groups_by_plan_skips_row_with_null_payment_id(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [
            [None, Decimal("99.00")],  # payment_id is None — skipped
            [str(ctx["payment_one"].unicef_id), Decimal("50.00")],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    result = service._row_groups_by_plan()

    plan_id = str(ctx["plan_one"].id)
    assert plan_id in result
    assert len(result[plan_id]) == 1  # the None-id row is not in the result


def test_validate_skips_fully_blank_rows(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD"],
            [None, None, None],  # fully blank row — skipped without error
            [str(ctx["payment_two"].unicef_id), Decimal("75.00"), "USD"],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service.validate()

    assert service.errors == []
