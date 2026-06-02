from decimal import Decimal

import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
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


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def group_with_follow_up_and_top_up_plans(program_cycle, business_area, fsp, delivery_mechanism, fsp_template):
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
    PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
    )
    PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
        plan_type=PaymentPlan.PlanType.TOP_UP,
    )
    return group, regular_plan


@pytest.fixture
def group_with_tagged_and_untagged_plans(program_cycle, business_area, fsp, delivery_mechanism, fsp_template):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    tagged_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
        export_tag=1,
    )
    untagged_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
        export_tag=None,
    )
    return group, tagged_plan, untagged_plan


def test_follow_up_and_top_up_plans_are_excluded(group_with_follow_up_and_top_up_plans):
    group, regular_plan = group_with_follow_up_and_top_up_plans

    service = XlsxPaymentPlanGroupDeliveryExportService(group)

    assert [plan.id for plan in service.payment_plans] == [regular_plan.id]


def test_already_tagged_plans_are_excluded_from_export(group_with_tagged_and_untagged_plans):
    group, _tagged_plan, untagged_plan = group_with_tagged_and_untagged_plans

    service = XlsxPaymentPlanGroupDeliveryExportService(group)

    assert [plan.id for plan in service.payment_plans] == [untagged_plan.id]


def test_save_xlsx_file_stamps_first_batch_with_tag_one(group_with_one_accepted_plan, user):
    plan = group_with_one_accepted_plan.payment_plans.first()

    XlsxPaymentPlanGroupDeliveryExportService(group_with_one_accepted_plan).save_xlsx_file(user)

    plan.refresh_from_db()
    assert plan.export_tag == 1


def test_save_xlsx_file_stores_batch_file_on_first_plan(group_with_one_accepted_plan, user):
    plan = group_with_one_accepted_plan.payment_plans.first()

    XlsxPaymentPlanGroupDeliveryExportService(group_with_one_accepted_plan).save_xlsx_file(user)

    plan.refresh_from_db()
    assert plan.group_export_file is not None
    assert plan.group_export_file.file.name.endswith("_batch_1.xlsx")


def test_save_xlsx_file_no_eligible_plans_creates_no_file(empty_group, user):
    XlsxPaymentPlanGroupDeliveryExportService(empty_group).save_xlsx_file(user)

    assert not empty_group.payment_plans.filter(group_export_file__isnull=False).exists()


def test_save_xlsx_file_one_batch_tags_all_plans_file_on_first(group_with_two_plans_and_payments, user):
    group = group_with_two_plans_and_payments

    XlsxPaymentPlanGroupDeliveryExportService(group).save_xlsx_file(user)

    plans = list(group.payment_plans.order_by("unicef_id"))
    assert all(plan.export_tag == 1 for plan in plans)
    assert plans[0].group_export_file is not None
    assert plans[1].group_export_file is None


def test_save_xlsx_file_second_export_increments_tag_and_excludes_first_batch(
    program_cycle, business_area, fsp, delivery_mechanism, fsp_template, user
):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    first_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
    )
    XlsxPaymentPlanGroupDeliveryExportService(group).save_xlsx_file(user)
    second_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
    )

    second_service = XlsxPaymentPlanGroupDeliveryExportService(group)
    assert [plan.id for plan in second_service.payment_plans] == [second_plan.id]
    second_service.save_xlsx_file(user)

    first_plan.refresh_from_db()
    second_plan.refresh_from_db()
    assert first_plan.export_tag == 1
    assert second_plan.export_tag == 2


def test_save_xlsx_file_does_not_tag_plan_whose_fsp_has_no_template(group_with_plan_without_template, user):
    plan = group_with_plan_without_template.payment_plans.first()

    XlsxPaymentPlanGroupDeliveryExportService(group_with_plan_without_template).save_xlsx_file(user)

    plan.refresh_from_db()
    assert plan.export_tag is None
