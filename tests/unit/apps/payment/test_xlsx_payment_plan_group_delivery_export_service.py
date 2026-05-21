from decimal import Decimal

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
from hope.apps.payment.xlsx.xlsx_payment_plan_group_delivery_export_service import (
    XlsxPaymentPlanGroupDeliveryExportService,
)
from hope.models import DataCollectingType, FinancialServiceProvider, PaymentPlan

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
def fsp_template(fsp, delivery_mechanism):
    """Default FSP XLSX template (all default columns) bound to fsp + delivery_mechanism."""
    return FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
    ).xlsx_template


@pytest.fixture
def empty_group(program_cycle):
    return PaymentPlanGroupFactory(cycle=program_cycle)


@pytest.fixture
def group_with_one_accepted_plan(program_cycle, business_area, fsp, delivery_mechanism, fsp_template):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
    )
    return group


@pytest.fixture
def group_with_two_plans_on_distinct_templates(program_cycle, business_area):
    fsp_one = FinancialServiceProviderFactory(
        name="FSP One",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        vision_vendor_number="111111111",
    )
    fsp_two = FinancialServiceProviderFactory(
        name="FSP Two",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        vision_vendor_number="222222222",
    )
    dm_one = DeliveryMechanismFactory(code="cash", name="Cash", payment_gateway_id="dm-cash")
    dm_two = DeliveryMechanismFactory(code="voucher", name="Voucher", payment_gateway_id="dm-voucher")
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp_one,
        delivery_mechanism=dm_one,
        xlsx_template=FinancialServiceProviderXlsxTemplateFactory(columns=["payment_id", "fsp_name"]),
    )
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp_two,
        delivery_mechanism=dm_two,
        xlsx_template=FinancialServiceProviderXlsxTemplateFactory(columns=["payment_id", "entitlement_quantity"]),
    )
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    plan_one = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp_one,
        delivery_mechanism=dm_one,
        status=PaymentPlan.Status.ACCEPTED,
    )
    plan_two = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp_two,
        delivery_mechanism=dm_two,
        status=PaymentPlan.Status.ACCEPTED,
    )
    payment_one = PaymentFactory(
        parent=plan_one,
        financial_service_provider=fsp_one,
        delivery_type=dm_one,
        program=plan_one.program,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("10.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment_one, snapshot_data={})
    payment_two = PaymentFactory(
        parent=plan_two,
        financial_service_provider=fsp_two,
        delivery_type=dm_two,
        program=plan_two.program,
        entitlement_quantity=Decimal("200.00"),
        entitlement_quantity_usd=Decimal("20.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment_two, snapshot_data={})
    return group


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
        entitlement_quantity_usd=Decimal("10.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment, snapshot_data={})
    return group


@pytest.fixture
def group_with_open_plan(program_cycle, business_area, fsp, delivery_mechanism, fsp_template):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.OPEN,
    )
    payment = PaymentFactory(
        parent=plan,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
        program=plan.program,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("10.00"),
    )
    PaymentHouseholdSnapshotFactory(payment=payment, snapshot_data={})
    return group


@pytest.fixture
def group_with_social_worker_program(business_area, fsp, delivery_mechanism, fsp_template):
    program = ProgramFactory(
        business_area=business_area,
        data_collecting_type__type=DataCollectingType.Type.SOCIAL,
        beneficiary_group__master_detail=False,
    )
    cycle = ProgramCycleFactory(program=program)
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
    )
    return group


@pytest.fixture
def group_with_payment_and_full_snapshot(program_cycle, business_area, fsp, delivery_mechanism, fsp_template):
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
        entitlement_quantity=Decimal("123.45"),
        entitlement_quantity_usd=Decimal("12.34"),
    )
    PaymentHouseholdSnapshotFactory(
        payment=payment,
        snapshot_data={
            "unicef_id": "HH-SNAP-001",
            "size": 5,
            "primary_collector": {"unicef_id": "IND-COL-7", "full_name": "Jan Kowalski"},
        },
    )
    return group


@pytest.fixture
def group_with_two_plans_and_payments(program_cycle, business_area, fsp, delivery_mechanism, fsp_template):
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
        status=PaymentPlan.Status.FINISHED,
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


def test_workbook_has_single_sheet_with_group_title(group_with_one_accepted_plan):
    wb = XlsxPaymentPlanGroupDeliveryExportService(group_with_one_accepted_plan).generate_workbook()

    assert wb.sheetnames == ["Payment Plan Group - Payment List"]


def test_header_row_contains_fsp_template_columns(group_with_one_accepted_plan):
    wb = XlsxPaymentPlanGroupDeliveryExportService(group_with_one_accepted_plan).generate_workbook()
    header_row = [cell.value for cell in wb.active[1]]

    assert header_row[0] == "payment_id"
    assert "currency" in header_row
    assert "entitlement_quantity" in header_row
    assert "individual_id" not in header_row


def test_empty_group_produces_workbook_with_no_payment_rows(empty_group):
    wb = XlsxPaymentPlanGroupDeliveryExportService(empty_group).generate_workbook()
    ws = wb.active

    assert ws.max_row == 1


def test_plan_whose_fsp_has_no_template_is_skipped(group_with_plan_without_template):
    wb = XlsxPaymentPlanGroupDeliveryExportService(group_with_plan_without_template).generate_workbook()
    ws = wb.active

    assert ws.max_row == 1


def test_open_plans_are_not_exported(group_with_open_plan):
    wb = XlsxPaymentPlanGroupDeliveryExportService(group_with_open_plan).generate_workbook()
    ws = wb.active

    assert ws.max_row == 1


def test_headers_for_social_worker_program(group_with_social_worker_program):
    wb = XlsxPaymentPlanGroupDeliveryExportService(group_with_social_worker_program).generate_workbook()
    header_row = [cell.value for cell in wb.active[1]]

    assert "individual_id" in header_row
    assert "household_id" not in header_row
    assert "household_size" not in header_row


def test_payment_row_contains_entitlement_quantities(group_with_payment_and_full_snapshot):
    wb = XlsxPaymentPlanGroupDeliveryExportService(group_with_payment_and_full_snapshot).generate_workbook()
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    entitlement_col = headers.index("entitlement_quantity") + 1
    entitlement_usd_col = headers.index("entitlement_quantity_usd") + 1

    assert ws.cell(row=2, column=entitlement_col).value == Decimal("123.45")
    assert ws.cell(row=2, column=entitlement_usd_col).value == Decimal("12.34")


def test_payment_row_contains_snapshot_household_data(group_with_payment_and_full_snapshot):
    wb = XlsxPaymentPlanGroupDeliveryExportService(group_with_payment_and_full_snapshot).generate_workbook()
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    household_id_col = headers.index("household_id") + 1
    household_size_col = headers.index("household_size") + 1
    collector_name_col = headers.index("collector_name") + 1

    assert ws.cell(row=2, column=household_id_col).value == "HH-SNAP-001"
    assert ws.cell(row=2, column=household_size_col).value == 5
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

    wb = XlsxPaymentPlanGroupDeliveryExportService(group).generate_workbook()
    ws = wb.active
    payment_ids_in_order = [ws.cell(row=row, column=1).value for row in range(2, ws.max_row + 1)]

    assert payment_ids_in_order == expected_order


def test_header_is_union_of_all_fsp_template_columns(group_with_two_plans_on_distinct_templates):
    wb = XlsxPaymentPlanGroupDeliveryExportService(group_with_two_plans_on_distinct_templates).generate_workbook()
    header_row = [cell.value for cell in wb.active[1]]

    assert set(header_row) == {"payment_id", "fsp_name", "entitlement_quantity"}
    assert len(header_row) == 3


def test_columns_outside_a_plans_template_are_blank_for_its_payments(group_with_two_plans_on_distinct_templates):
    wb = XlsxPaymentPlanGroupDeliveryExportService(group_with_two_plans_on_distinct_templates).generate_workbook()
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    fsp_name_col = headers.index("fsp_name") + 1
    entitlement_col = headers.index("entitlement_quantity") + 1

    assert ws.cell(row=2, column=fsp_name_col).value == "FSP One"
    assert ws.cell(row=2, column=entitlement_col).value == ""
    assert ws.cell(row=3, column=fsp_name_col).value == ""
    assert ws.cell(row=3, column=entitlement_col).value == Decimal("200.00")
