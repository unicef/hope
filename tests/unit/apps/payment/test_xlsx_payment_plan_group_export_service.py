from decimal import Decimal

import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentHouseholdSnapshotFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.payment.flows import PaymentPlanFlow
from hope.apps.payment.xlsx.xlsx_payment_plan_group_export_service import (
    XlsxPaymentPlanGroupExportService,
)
from hope.models import DataCollectingType, FinancialServiceProvider

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
        name="Test FSP 1",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        vision_vendor_number="123456789",
    )


@pytest.fixture
def delivery_mechanism():
    return DeliveryMechanismFactory(code="cash", name="Cash", payment_gateway_id="dm-cash")


@pytest.fixture
def empty_group(program_cycle):
    return PaymentPlanGroupFactory(cycle=program_cycle)


@pytest.fixture
def group_with_one_locked_plan(program_cycle, business_area, fsp, delivery_mechanism):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
    )
    flow = PaymentPlanFlow(plan)
    flow.status_lock()
    plan.save()
    return group


@pytest.fixture
def group_with_two_plans_and_payments(program_cycle, business_area, fsp, delivery_mechanism):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    plan_one = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
    )
    flow_one = PaymentPlanFlow(plan_one)
    flow_one.status_lock()
    plan_one.save()
    plan_two = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
    )
    flow_two = PaymentPlanFlow(plan_two)
    flow_two.status_lock()
    plan_two.save()
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
        parent=plan_one,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
        program=plan_one.program,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("10.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment_two, snapshot_data={})
    payment_three = PaymentFactory(
        parent=plan_two,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
        program=plan_two.program,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("10.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment_three, snapshot_data={})
    return group


def test_workbook_has_single_sheet_with_group_title(group_with_one_locked_plan):
    wb = XlsxPaymentPlanGroupExportService(group_with_one_locked_plan).generate_workbook()

    assert wb.sheetnames == ["Payment Plan Group - Payment List"]


def test_first_row_contains_household_program_headers(group_with_one_locked_plan):
    wb = XlsxPaymentPlanGroupExportService(group_with_one_locked_plan).generate_workbook()
    header_row = [cell.value for cell in wb.active[1]]

    assert header_row[0] == "payment_id"
    assert "collector_id" in header_row
    assert "household_id" in header_row
    assert "individual_id" not in header_row


def test_empty_group_produces_workbook_with_only_headers(empty_group):
    wb = XlsxPaymentPlanGroupExportService(empty_group).generate_workbook()
    ws = wb.active

    assert ws.max_row == 1
    assert ws.cell(row=1, column=1).value == "payment_id"


@pytest.fixture
def group_with_social_worker_program(business_area, fsp, delivery_mechanism):
    program = ProgramFactory(
        business_area=business_area,
        data_collecting_type__type=DataCollectingType.Type.SOCIAL,
        beneficiary_group__master_detail=False,
    )
    cycle = ProgramCycleFactory(program=program)
    group = PaymentPlanGroupFactory(cycle=cycle)
    plan = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
    )
    flow = PaymentPlanFlow(plan)
    flow.status_lock()
    plan.save()
    return group


def test_headers_for_social_worker_program(group_with_social_worker_program):
    wb = XlsxPaymentPlanGroupExportService(group_with_social_worker_program).generate_workbook()
    header_row = [cell.value for cell in wb.active[1]]

    assert "individual_id" in header_row
    assert "household_id" not in header_row
    assert "household_size" not in header_row
    assert "collector_id" not in header_row


@pytest.fixture
def group_with_payment_and_full_snapshot(program_cycle, business_area, fsp, delivery_mechanism):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
    )
    flow = PaymentPlanFlow(plan)
    flow.status_lock()
    plan.save()
    payment = PaymentFactory(
        parent=plan,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
        program=plan.program,
        entitlement_quantity=Decimal("123.45"),
        entitlement_quantity_usd=Decimal("12.34"),
    )
    PaymentHouseholdSnapshotFactory(
        payment=payment,
        snapshot_data={
            "unicef_id": "HH-SNAP-001",
            "size": 5,
            "village": "Lorem Ipsum",
            "primary_collector": {"unicef_id": "IND-COL-7", "full_name": "Jan Kowalski"},
        },
    )
    return group


def test_payment_row_contains_entitlement_quantities(group_with_payment_and_full_snapshot):
    wb = XlsxPaymentPlanGroupExportService(group_with_payment_and_full_snapshot).generate_workbook()
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    entitlement_col = headers.index("entitlement_quantity") + 1
    entitlement_usd_col = headers.index("entitlement_quantity_usd") + 1

    assert ws.cell(row=2, column=entitlement_col).value == Decimal("123.45")
    assert ws.cell(row=2, column=entitlement_usd_col).value == Decimal("12.34")


def test_payment_row_contains_snapshot_household_data(group_with_payment_and_full_snapshot):
    wb = XlsxPaymentPlanGroupExportService(group_with_payment_and_full_snapshot).generate_workbook()
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    household_id_col = headers.index("household_id") + 1
    household_size_col = headers.index("household_size") + 1
    village_col = headers.index("village") + 1
    collector_name_col = headers.index("collector_name") + 1

    assert ws.cell(row=2, column=household_id_col).value == "HH-SNAP-001"
    assert ws.cell(row=2, column=household_size_col).value == 5
    assert ws.cell(row=2, column=village_col).value == "Lorem Ipsum"
    assert ws.cell(row=2, column=collector_name_col).value == "Jan Kowalski"


def test_payments_grouped_by_plan_and_sorted_within_each_plan(group_with_two_plans_and_payments):
    group = group_with_two_plans_and_payments
    plans_in_order = list(group.payment_plans.order_by("unicef_id"))
    plan_one_payment_ids = list(
        plans_in_order[0].eligible_payments.order_by("unicef_id").values_list("unicef_id", flat=True)
    )
    plan_two_payment_ids = list(
        plans_in_order[1].eligible_payments.order_by("unicef_id").values_list("unicef_id", flat=True)
    )
    expected_order = plan_one_payment_ids + plan_two_payment_ids

    wb = XlsxPaymentPlanGroupExportService(group).generate_workbook()
    ws = wb.active
    payment_ids_in_order = [ws.cell(row=row, column=1).value for row in range(2, ws.max_row + 1)]

    assert payment_ids_in_order == expected_order
