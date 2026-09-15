from datetime import timedelta
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.db import connection, transaction
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
import openpyxl
import pytest

from extras.test_utils.factories.core import BusinessAreaFactory, CurrencyFactory, FileTempFactory
from extras.test_utils.factories.grievance import TicketPaymentVerificationDetailsFactory
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentFactory,
    PaymentHouseholdSnapshotFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.payment.xlsx.xlsx_error import XlsxError
from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_import_service import XlsxPaymentPlanDeliveryImportService
from hope.apps.payment.xlsx.xlsx_payment_plan_group_delivery_import_service import (
    XlsxPaymentPlanGroupDeliveryImportError,
    XlsxPaymentPlanGroupDeliveryImportService,
)
from hope.models import (
    FileTemp,
    FinancialServiceProvider,
    LogEntry,
    Payment,
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
    ProgramCycle,
)

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
        status=Payment.STATUS_SENT_TO_FSP,
    )
    PaymentHouseholdSnapshotFactory(payment=payment_one, snapshot_data={})
    payment_two = PaymentFactory(
        parent=plan_two,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
        program=plan_two.program,
        entitlement_quantity=Decimal("200.00"),
        entitlement_quantity_usd=Decimal("20.00"),
        status=Payment.STATUS_SENT_TO_FSP,
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
def group_two_plans_with_shared_export_file(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file_temp = FileTemp.objects.create(
        object_id=str(ctx["group"].pk),
        content_type=ContentType.objects.get_for_model(ctx["group"]),
    )
    file_temp.file.save("export.xlsx", ContentFile(b"exported-bytes"))
    PaymentPlan.objects.filter(id__in=[ctx["plan_one"].id, ctx["plan_two"].id]).update(
        export_tag=1, export_file_delivery=file_temp
    )
    ctx["plan_one"].refresh_from_db()
    ctx["plan_two"].refresh_from_db()
    return {**ctx, "file_temp": file_temp, "file_name": file_temp.file.name}


@pytest.fixture
def group_two_plans_with_sparse_fsp_header(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    ctx["payment_one"].extras = {"fsp_extra_fields": {"fsp_reference": "owned-by-fsp"}}
    ctx["payment_one"].save(update_fields=["extras"])
    return ctx


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
        status=Payment.STATUS_SENT_TO_FSP,
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
    top_up_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.ACCEPTED,
        plan_type=PaymentPlan.PlanType.TOP_UP,
    )
    return {
        "group": group,
        "regular_plan": regular_plan,
        "follow_up_plan": follow_up_plan,
        "top_up_plan": top_up_plan,
    }


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
        status=Payment.STATUS_SENT_TO_FSP,
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
    assert service.get_result_counts() == {
        "total_rows": 2,
        "updated_rows": 2,
        "reset_rows": 0,
        "ignored_rows": 0,
    }


def test_group_reconciliation_uses_group_wide_fsp_header_ownership(
    group_two_plans_with_sparse_fsp_header,
):
    ctx = group_two_plans_with_sparse_fsp_header
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "fsp_reference", "returned_code"],
        [
            [str(ctx["payment_two"].unicef_id), Decimal("75.00"), "returned-fsp-value", "RETURNED-002"],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service.validate()
    plan_service = service.per_plan_services[str(ctx["plan_two"].id)]
    row = next(plan_service.ws_payments.iter_rows(min_row=2))

    extras = plan_service._get_extras_for_row(row)

    assert extras == {"returned_code": "RETURNED-002"}


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
    with pytest.raises(XlsxPaymentPlanGroupDeliveryImportError):
        service.import_payment_list()
    ctx["payment_one"].refresh_from_db()
    assert ctx["payment_one"].delivered_quantity is None


def test_validate_accepts_file_when_no_actual_changes(group_two_plans_one_fsp):
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

    assert service.errors == []


def test_normal_import_skips_pending_payment_not_exported_to_fsp(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    payment.status = Payment.STATUS_PENDING
    payment.save(update_fields=["status"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(payment.unicef_id), Decimal("50.00")]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    service.import_payment_list()

    payment.refresh_from_db()
    assert payment.status == Payment.STATUS_PENDING
    assert payment.delivered_quantity is None
    assert service.skipped_rows == [
        {
            "row": 2,
            "payment_id": str(payment.unicef_id),
            "reason": f"Payment status {Payment.STATUS_PENDING} is not eligible for this import mode.",
        }
    ]


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


def test_follow_up_and_top_up_plans_are_included(group_with_follow_up_and_top_up_plans):
    ctx = group_with_follow_up_and_top_up_plans
    file = _make_workbook(["payment_id", "delivered_quantity"], [])
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    assert {plan.id for plan in service.payment_plans} == {
        ctx["regular_plan"].id,
        ctx["follow_up_plan"].id,
        ctx["top_up_plan"].id,
    }


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
    ctx["payment_two"].delivered_quantity = Decimal("50.00")
    ctx["payment_two"].status = Payment.STATUS_DISTRIBUTION_PARTIAL
    ctx["payment_two"].save(update_fields=["delivered_quantity", "status"])

    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    with pytest.raises(XlsxPaymentPlanGroupDeliveryImportError):
        service.import_payment_list()

    ctx["payment_one"].refresh_from_db()
    ctx["payment_two"].refresh_from_db()
    assert ctx["payment_one"].delivered_quantity is None
    assert ctx["payment_two"].delivered_quantity == Decimal("50.00")


def test_import_deletes_whole_shared_export_filetemp(
    group_two_plans_with_shared_export_file, django_capture_on_commit_callbacks
):
    ctx = group_two_plans_with_shared_export_file
    file_temp = ctx["file_temp"]
    storage = file_temp.file.storage
    file_name = ctx["file_name"]
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD"],
            [str(ctx["payment_two"].unicef_id), Decimal("75.00"), "USD"],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    # file delete is deferred to transaction.on_commit, so execute the captured callbacks
    with django_capture_on_commit_callbacks(execute=True):
        service.import_payment_list()

    assert not FileTemp.objects.filter(pk=file_temp.pk).exists()
    assert not storage.exists(file_name)


def test_import_does_not_crash_logging_change_after_removing_shared_export_file(
    group_two_plans_with_shared_export_file,
):
    ctx = group_two_plans_with_shared_export_file
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD"],
            [str(ctx["payment_two"].unicef_id), Decimal("75.00"), "USD"],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    # log_payment_plan_change diffs a pre-remove snapshot whose export_file_delivery FK now
    # points at a deleted FileTemp: this must not raise FileTemp.DoesNotExist.
    service.import_payment_list()

    ctx["payment_one"].refresh_from_db()
    ctx["payment_two"].refresh_from_db()
    assert ctx["payment_one"].delivered_quantity == Decimal("50.00")
    assert ctx["payment_two"].delivered_quantity == Decimal("75.00")


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


def test_import_partial_file_leaves_omitted_payment_unchanged(group_two_plans_one_fsp, django_assert_num_queries):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "currency"],
        [[str(ctx["payment_one"].unicef_id), Decimal("50.00"), "USD"]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    service.import_payment_list()

    with django_assert_num_queries(2):
        ctx["payment_one"].refresh_from_db()
        ctx["payment_two"].refresh_from_db()
    assert ctx["payment_one"].delivered_quantity == Decimal("50.00")
    assert ctx["payment_two"].delivered_quantity is None
    assert ctx["payment_two"].status == Payment.STATUS_SENT_TO_FSP


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


@pytest.fixture
def group_with_closed_plan(program_cycle, business_area, fsp, delivery_mechanism, template):
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    payment_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.CLOSED,
    )
    payment = PaymentFactory(
        parent=payment_plan,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
        program=payment_plan.program,
        entitlement_quantity=Decimal("100.00"),
        delivered_quantity=Decimal("100.00"),
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
        transaction_reference_id="CLOSED-REFERENCE",
    )
    PaymentHouseholdSnapshotFactory(payment=payment, snapshot_data={})
    file_temp = FileTemp.objects.create(
        object_id=str(group.pk),
        content_type=ContentType.objects.get_for_model(group),
    )
    group.delivery_import_file = file_temp
    group.save(update_fields=["delivery_import_file"])
    return {"group": group, "payment_plan": payment_plan, "payment": payment, "file_temp": file_temp}


@pytest.fixture
def group_with_finished_usd_plan(program_cycle, business_area, fsp, delivery_mechanism, template):
    currency = CurrencyFactory(code="USD", name="US Dollar")
    group = PaymentPlanGroupFactory(cycle=program_cycle)
    payment_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        payment_plan_group=group,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        status=PaymentPlan.Status.FINISHED,
        currency=currency,
        exchange_rate=Decimal("1.00"),
    )
    payment = PaymentFactory(
        parent=payment_plan,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
        program=payment_plan.program,
        currency=currency,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("100.00"),
        delivered_quantity=Decimal("100.00"),
        delivered_quantity_usd=Decimal("100.00"),
        status=Payment.STATUS_DISTRIBUTION_SUCCESS,
    )
    PaymentHouseholdSnapshotFactory(payment=payment, snapshot_data={})
    return {"group": group, "payment_plan": payment_plan, "payment": payment}


@pytest.fixture
def group_with_finished_plan(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    ctx["plan_one"].status = PaymentPlan.Status.FINISHED
    ctx["plan_one"].save(update_fields=["status"])
    return ctx


@pytest.fixture
def group_with_flagged_payment(group_two_plans_one_fsp, request):
    ctx = group_two_plans_one_fsp
    field_name, value = request.param
    setattr(ctx["payment_one"], field_name, value)
    ctx["payment_one"].save(update_fields=[field_name])
    return ctx


@pytest.fixture
def group_with_started_verifications(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    ctx["plan_one"].status = PaymentPlan.Status.FINISHED
    ctx["plan_one"].save(update_fields=["status"])
    payment = ctx["payment_one"]
    payment.delivered_quantity = Decimal("100.00")
    payment.status = Payment.STATUS_DISTRIBUTION_SUCCESS
    payment.save(update_fields=["delivered_quantity", "status"])
    PaymentVerificationSummaryFactory(payment_plan=ctx["plan_one"])
    finished_verification_plan = PaymentVerificationPlanFactory(
        payment_plan=ctx["plan_one"],
        status=PaymentVerificationPlan.STATUS_FINISHED,
    )
    finished_verification = PaymentVerificationFactory(
        payment_verification_plan=finished_verification_plan,
        payment=payment,
        status=PaymentVerification.STATUS_RECEIVED,
        received_amount=Decimal("100.00"),
    )
    active_verification_plan = PaymentVerificationPlanFactory(
        payment_plan=ctx["plan_one"],
        status=PaymentVerificationPlan.STATUS_ACTIVE,
    )
    active_verification = PaymentVerificationFactory(
        payment_verification_plan=active_verification_plan,
        payment=payment,
        status=PaymentVerification.STATUS_NOT_RECEIVED,
        received_amount=Decimal("50.00"),
    )
    return {
        **ctx,
        "finished_verification": finished_verification,
        "active_verification": active_verification,
    }


@pytest.fixture
def group_with_pending_verification(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    ctx["plan_one"].status = PaymentPlan.Status.FINISHED
    ctx["plan_one"].save(update_fields=["status"])
    payment = ctx["payment_one"]
    payment.delivered_quantity = Decimal("100.00")
    payment.status = Payment.STATUS_DISTRIBUTION_SUCCESS
    payment.save(update_fields=["delivered_quantity", "status"])
    PaymentVerificationSummaryFactory(payment_plan=ctx["plan_one"])
    verification_plan = PaymentVerificationPlanFactory(
        payment_plan=ctx["plan_one"],
        status=PaymentVerificationPlan.STATUS_PENDING,
        responded_count=1,
        received_count=1,
        not_received_count=0,
        received_with_problems_count=0,
    )
    verification = PaymentVerificationFactory(
        payment_verification_plan=verification_plan,
        payment=payment,
        status=PaymentVerification.STATUS_RECEIVED,
        status_date=timezone.now(),
        received_amount=Decimal("100.00"),
    )
    return {**ctx, "verification_plan": verification_plan, "verification": verification}


@pytest.fixture
def group_with_verification_file(group_with_pending_verification):
    ctx = group_with_pending_verification
    verification_plan = ctx["verification_plan"]
    content_type = ContentType.objects.get_for_model(PaymentVerificationPlan)
    file_temp = FileTempFactory(
        content_type=content_type,
        object_id=str(verification_plan.pk),
        file=ContentFile(b"verification", name="verification.xlsx"),
    )
    empty_file_temp = FileTempFactory(
        content_type=content_type,
        object_id=str(verification_plan.pk),
        file="",
    )
    return {**ctx, "verification_file": file_temp, "empty_verification_file": empty_file_temp}


def test_init_rejects_unsupported_null_delivery_policy(group_two_plans_one_fsp, django_assert_num_queries):
    with django_assert_num_queries(0), pytest.raises(ValueError, match="Unsupported null delivery policy"):
        XlsxPaymentPlanGroupDeliveryImportService(
            group_two_plans_one_fsp["group"], BytesIO(), null_delivery_policy="unsupported"
        )


def test_import_requires_open_workbook(group_two_plans_one_fsp, django_assert_num_queries):
    service = XlsxPaymentPlanGroupDeliveryImportService(group_two_plans_one_fsp["group"], BytesIO())

    with django_assert_num_queries(0), pytest.raises(RuntimeError, match=r"open_workbook\(\) must be called"):
        service.import_payment_list()
    with django_assert_num_queries(0), pytest.raises(RuntimeError, match="before reading import results"):
        service.get_result_counts()


def test_normal_import_reports_finished_plan_row_as_ineligible(group_with_finished_plan, django_assert_num_queries):
    ctx = group_with_finished_plan
    payment = ctx["payment_one"]
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(payment.unicef_id), Decimal("50.00")]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)

    with django_assert_num_queries(4):
        service.open_workbook()
    with django_assert_num_queries(0):
        service.validate()

    assert service.errors == []
    assert service.skipped_rows == [
        {
            "row": 2,
            "payment_id": str(payment.unicef_id),
            "reason": f"Payment Plan status {PaymentPlan.Status.FINISHED} is not eligible for this import mode.",
        }
    ]


@pytest.mark.parametrize(
    "group_with_flagged_payment",
    [
        pytest.param(("conflicted", True), id="conflicted"),
        pytest.param(("excluded", True), id="excluded"),
        pytest.param(("has_valid_wallet", False), id="invalid-wallet"),
    ],
    indirect=True,
)
def test_flagged_payment_is_not_added_to_group_payment_index(group_with_flagged_payment, django_assert_num_queries):
    ctx = group_with_flagged_payment
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], BytesIO())

    with django_assert_num_queries(4):
        service._prepare_payment_data()

    assert str(ctx["payment_one"].unicef_id) not in service.payment_to_plan


@pytest.mark.enable_activity_log
def test_normal_import_ignores_equal_quantity_even_when_reference_differs(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    payment.delivered_quantity = Decimal("100.00")
    payment.status = Payment.STATUS_DISTRIBUTION_SUCCESS
    payment.transaction_reference_id = "OLD-REFERENCE"
    payment.save(update_fields=["delivered_quantity", "status", "transaction_reference_id"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "reference_id"],
        [[str(payment.unicef_id), Decimal("100.00"), "NEW-REFERENCE"]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    service.import_payment_list()

    payment.refresh_from_db()
    assert payment.transaction_reference_id == "OLD-REFERENCE"
    assert not LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(Payment),
        object_id=payment.pk,
    ).exists()


def test_normal_import_reports_different_existing_quantity_as_conflict(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    payment.delivered_quantity = Decimal("100.00")
    payment.status = Payment.STATUS_DISTRIBUTION_SUCCESS
    payment.save(update_fields=["delivered_quantity", "status"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(payment.unicef_id), Decimal("90.00")]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    service.validate()

    assert len(service.errors) == 1
    assert service.conflict_errors == service.errors
    assert "conflicts with the existing delivered quantity" in service.errors[0].message


@pytest.mark.enable_activity_log
def test_normal_import_ignores_empty_quantity(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    payment.transaction_reference_id = "KEEP-ME"
    payment.save(update_fields=["transaction_reference_id"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "reference_id"],
        [[str(payment.unicef_id), None, "DO-NOT-APPLY"]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    service.import_payment_list()

    payment.refresh_from_db()
    assert payment.delivered_quantity is None
    assert payment.transaction_reference_id == "KEEP-ME"
    assert not LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(Payment),
        object_id=payment.pk,
    ).exists()


@pytest.mark.parametrize(
    "invalid_quantity",
    [
        pytest.param(-2, id="negative"),
        pytest.param(-1.004, id="not_exactly_minus_one"),
        pytest.param("invalid", id="text"),
        pytest.param(True, id="boolean"),
    ],
)
def test_validate_rejects_invalid_delivered_quantity(group_two_plans_one_fsp, invalid_quantity):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(ctx["payment_one"].unicef_id), invalid_quantity]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    service.validate()

    assert len(service.errors) == 1
    assert "exactly -1" in service.errors[0].message


def test_minus_one_sets_error_and_stores_no_quantity(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(payment.unicef_id), -1]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    service.import_payment_list()

    payment.refresh_from_db()
    ctx["plan_one"].refresh_from_db()
    assert payment.delivered_quantity is None
    assert payment.delivered_quantity_usd is None
    assert payment.status == Payment.STATUS_ERROR
    assert ctx["plan_one"].status == PaymentPlan.Status.FINISHED


@pytest.mark.enable_activity_log
def test_override_reset_clears_reconciliation_fields_but_preserves_fsp_extras(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    payment.delivered_quantity = Decimal("100.00")
    payment.delivered_quantity_usd = Decimal("10.00")
    payment.status = Payment.STATUS_DISTRIBUTION_SUCCESS
    payment.delivery_date = timezone.now()
    payment.transaction_reference_id = "TX-123"
    payment.reason_for_unsuccessful_payment = "old reason"
    payment.additional_collector_name = "Collector"
    payment.additional_document_type = "Passport"
    payment.additional_document_number = "DOC-1"
    payment.transaction_status_blockchain_link = "https://example.com/transaction"
    payment.status_date = timezone.now() - timedelta(days=1)
    previous_status_date = payment.status_date
    payment.extras = {
        Payment.EXTRA_FIELDS_KEY: {"returned_code": "old"},
        Payment.FSP_EXTRA_FIELDS_KEY: {"fsp_reference": "keep"},
        "unrelated": {"keep": True},
    }
    payment.save()
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(payment.unicef_id), None]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=True)
    service.open_workbook()

    service.import_payment_list()

    payment.refresh_from_db()
    assert payment.delivered_quantity is None
    assert payment.delivered_quantity_usd is None
    assert payment.delivery_date is None
    assert payment.status == Payment.STATUS_SENT_TO_FSP
    assert payment.status_date > previous_status_date
    assert payment.transaction_reference_id is None
    assert payment.reason_for_unsuccessful_payment is None
    assert payment.additional_collector_name is None
    assert payment.additional_document_type is None
    assert payment.additional_document_number is None
    assert payment.transaction_status_blockchain_link is None
    assert payment.extra_fields == {}
    assert payment.fsp_extra_fields == {"fsp_reference": "keep"}
    assert payment.extras["unrelated"] == {"keep": True}
    assert service.get_result_counts() == {
        "total_rows": 1,
        "updated_rows": 0,
        "reset_rows": 1,
        "ignored_rows": 0,
    }
    payment_log = LogEntry.objects.get(
        content_type=ContentType.objects.get_for_model(Payment),
        object_id=payment.pk,
    )
    assert {
        "delivered_quantity_usd",
        "additional_collector_name",
        "additional_document_type",
        "additional_document_number",
        "transaction_status_blockchain_link",
        "extra_fields",
    } <= payment_log.changes.keys()


def test_override_reset_deletes_verifications_and_empty_active_and_finished_plans(
    group_with_started_verifications, django_assert_num_queries
):
    ctx = group_with_started_verifications
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(ctx["payment_one"].unicef_id), None]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=True)
    service.open_workbook()

    service.import_payment_list()

    with django_assert_num_queries(2):
        assert not PaymentVerification.objects.filter(payment=ctx["payment_one"]).exists()
        assert not PaymentVerificationPlan.objects.filter(payment_plan=ctx["plan_one"]).exists()


def test_override_reset_deletes_verification_and_empty_pending_plan(
    group_with_pending_verification, django_assert_num_queries
):
    ctx = group_with_pending_verification
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(ctx["payment_one"].unicef_id), None]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=True)
    service.open_workbook()

    service.import_payment_list()

    with django_assert_num_queries(2):
        assert not PaymentVerification.objects.filter(pk=ctx["verification"].pk).exists()
        assert not PaymentVerificationPlan.objects.filter(pk=ctx["verification_plan"].pk).exists()


def test_verification_cleanup_deletes_attached_file_after_commit(
    group_with_verification_file,
    django_capture_on_commit_callbacks,
    django_assert_num_queries,
):
    ctx = group_with_verification_file
    file_name = ctx["verification_file"].file.name
    storage = ctx["verification_file"].file.storage
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(ctx["payment_one"].unicef_id), None]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=True)
    service.open_workbook()

    with django_capture_on_commit_callbacks(execute=True):
        service.import_payment_list()

    with django_assert_num_queries(2):
        assert not FileTemp.objects.filter(pk=ctx["verification_file"].pk).exists()
        assert not FileTemp.objects.filter(pk=ctx["empty_verification_file"].pk).exists()
    assert not storage.exists(file_name)


@pytest.fixture
def group_with_shared_verification_plan(group_with_pending_verification):
    ctx = group_with_pending_verification
    plan = ctx["verification_plan"]
    plan.status = PaymentVerificationPlan.STATUS_FINISHED
    plan.sample_size = 2
    plan.responded_count = 2
    plan.received_count = 2
    plan.save()
    other_payment = ctx["payment_two"]
    other_payment.parent = ctx["plan_one"]
    other_payment.save(update_fields=["parent"])
    other_verification = PaymentVerificationFactory(
        payment=other_payment,
        payment_verification_plan=plan,
        status=PaymentVerification.STATUS_RECEIVED,
        received_amount=Decimal("200.00"),
    )
    direct_ticket = TicketPaymentVerificationDetailsFactory(payment_verification=ctx["verification"]).ticket
    legacy_details = TicketPaymentVerificationDetailsFactory()
    legacy_details.payment_verifications.add(ctx["verification"])
    unrelated_ticket = TicketPaymentVerificationDetailsFactory(payment_verification=other_verification).ticket
    return {
        **ctx,
        "other_verification": other_verification,
        "direct_ticket": direct_ticket,
        "legacy_ticket": legacy_details.ticket,
        "unrelated_ticket": unrelated_ticket,
    }


@pytest.fixture
def verification_cleanup_import(group_with_shared_verification_plan, file_quantity, override, policy, initial_quantity):
    ctx = group_with_shared_verification_plan
    payment = ctx["payment_one"]
    payment.delivered_quantity = initial_quantity
    payment.status = Payment.STATUS_SENT_TO_FSP if initial_quantity is None else Payment.STATUS_DISTRIBUTION_SUCCESS
    payment.save(update_fields=["delivered_quantity", "status"])
    ctx["plan_one"].status = PaymentPlan.Status.ACCEPTED
    ctx["plan_one"].save(update_fields=["status"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "reference_id"],
        [[str(payment.unicef_id), file_quantity, "NEW-REFERENCE"]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(
        ctx["group"], file, override=override, null_delivery_policy=policy
    )
    service.open_workbook()
    return {**ctx, "service": service}


@pytest.mark.parametrize(
    ("file_quantity", "override", "policy", "initial_quantity", "deleted"),
    [
        pytest.param(None, True, "reset", Decimal(100), True, id="reset"),
        pytest.param(None, True, "reset", None, True, id="reset-already-empty-payment"),
        pytest.param(50, True, "reset", Decimal(100), True, id="changed-quantity"),
        pytest.param(-1, True, "reset", Decimal(100), True, id="error-marker"),
        pytest.param(100, True, "reset", Decimal(100), False, id="only-reference-changed"),
        pytest.param(None, True, "ignore", Decimal(100), False, id="ignore-empty"),
        pytest.param(100, False, "reset", None, False, id="first-reconciliation"),
        pytest.param(100, False, "reset", Decimal(100), False, id="normal-equal"),
    ],
)
def test_verification_cleanup_follows_reconciliation_action(
    verification_cleanup_import, deleted, django_assert_num_queries
):
    ctx = verification_cleanup_import

    ctx["service"].import_payment_list()

    with django_assert_num_queries(6):
        assert PaymentVerification.objects.filter(pk=ctx["verification"].pk).exists() == (not deleted)
        assert GrievanceTicket.objects.filter(pk=ctx["direct_ticket"].pk).exists() == (not deleted)
        assert GrievanceTicket.objects.filter(pk=ctx["legacy_ticket"].pk).exists() == (not deleted)
        assert GrievanceTicket.objects.filter(pk=ctx["unrelated_ticket"].pk).exists()
        ctx["verification_plan"].refresh_from_db()
        ctx["other_verification"].refresh_from_db()
    assert ctx["verification_plan"].sample_size == 2 - int(deleted)
    assert ctx["verification_plan"].responded_count == 2 - int(deleted)
    assert ctx["verification_plan"].received_count == 2 - int(deleted)
    assert ctx["verification_plan"].status == PaymentVerificationPlan.STATUS_FINISHED
    assert ctx["other_verification"].received_amount == Decimal("200.00")


def test_verification_cleanup_rolls_back_with_import(group_with_shared_verification_plan, django_assert_num_queries):
    ctx = group_with_shared_verification_plan
    file = _make_workbook(["payment_id", "delivered_quantity"], [[str(ctx["payment_one"].unicef_id), None]])
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=True)
    service.open_workbook()

    with transaction.atomic():
        service.import_payment_list()
        transaction.set_rollback(True)

    with django_assert_num_queries(4):
        assert PaymentVerification.objects.filter(pk=ctx["verification"].pk).exists()
        assert GrievanceTicket.objects.filter(pk=ctx["direct_ticket"].pk).exists()
        ctx["verification_plan"].refresh_from_db()
        ctx["payment_one"].refresh_from_db()
    assert ctx["verification_plan"].sample_size == 2
    assert ctx["payment_one"].delivered_quantity == Decimal("100.00")


@pytest.mark.enable_activity_log
def test_override_ignore_policy_preserves_empty_quantity_row(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    payment.delivered_quantity = Decimal("100.00")
    payment.status = Payment.STATUS_DISTRIBUTION_SUCCESS
    payment.transaction_reference_id = "KEEP-ME"
    payment.save(update_fields=["delivered_quantity", "status", "transaction_reference_id"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(payment.unicef_id), None]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(
        ctx["group"], file, override=True, null_delivery_policy="ignore"
    )
    service.open_workbook()

    service.import_payment_list()

    payment.refresh_from_db()
    assert payment.delivered_quantity == Decimal("100.00")
    assert payment.transaction_reference_id == "KEEP-ME"
    assert service.get_result_counts() == {
        "total_rows": 1,
        "updated_rows": 0,
        "reset_rows": 0,
        "ignored_rows": 1,
    }
    assert not LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(Payment),
        object_id=payment.pk,
    ).exists()


def test_override_equal_quantity_applies_other_present_fields(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    payment.delivered_quantity = Decimal("100.00")
    payment.status = Payment.STATUS_DISTRIBUTION_SUCCESS
    payment.transaction_reference_id = "OLD"
    old_status_date = payment.status_date
    payment.save(update_fields=["delivered_quantity", "status", "transaction_reference_id"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "reference_id"],
        [[str(payment.unicef_id), Decimal("100.00"), "NEW"]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=True)
    service.open_workbook()

    service.import_payment_list()

    payment.refresh_from_db()
    assert payment.transaction_reference_id == "NEW"
    assert payment.status_date == old_status_date


def test_first_reconciliation_updates_status_date_when_status_changes(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    old_status_date = payment.status_date
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(payment.unicef_id), Decimal("100.00")]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    service.import_payment_list()

    payment.refresh_from_db()
    assert payment.status == Payment.STATUS_DISTRIBUTION_SUCCESS
    assert payment.status_date > old_status_date


def test_override_missing_optional_header_preserves_existing_value(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    payment.status = Payment.STATUS_SENT_TO_FSP
    payment.transaction_reference_id = "KEEP-ME"
    payment.save(update_fields=["status", "transaction_reference_id"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(payment.unicef_id), Decimal("50.00")]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=True)
    service.open_workbook()

    service.import_payment_list()

    payment.refresh_from_db()
    assert payment.transaction_reference_id == "KEEP-ME"


def test_override_empty_optional_cell_clears_existing_value(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    payment.status = Payment.STATUS_SENT_TO_FSP
    payment.transaction_reference_id = "CLEAR-ME"
    payment.save(update_fields=["status", "transaction_reference_id"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "reference_id"],
        [[str(payment.unicef_id), Decimal("50.00"), None]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=True)
    service.open_workbook()

    service.import_payment_list()

    payment.refresh_from_db()
    assert payment.transaction_reference_id is None


@pytest.mark.parametrize("override", [False, True])
@pytest.mark.parametrize("quantity", [None, Decimal("100.00")])
def test_closed_plan_row_with_empty_or_matching_quantity_is_skipped(
    group_with_closed_plan, override, quantity, django_assert_num_queries
):
    ctx = group_with_closed_plan
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "reference_id"],
        [[str(ctx["payment"].unicef_id), quantity, "MUST-NOT-CHANGE"]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=override)
    service.open_workbook()

    service.validate()
    assert service.errors == []
    service.import_payment_list()

    assert service.skipped_rows == [
        {
            "row": 2,
            "payment_id": str(ctx["payment"].unicef_id),
            "reason": (
                f"Payment belongs to CLOSED Payment Plan {ctx['payment_plan'].unicef_id}; existing data was preserved."
            ),
        }
    ]
    with django_assert_num_queries(3):
        ctx["payment"].refresh_from_db()
        ctx["payment_plan"].refresh_from_db()
        ctx["file_temp"].refresh_from_db()
    assert ctx["payment"].delivered_quantity == Decimal("100.00")
    assert ctx["payment"].status == Payment.STATUS_DISTRIBUTION_SUCCESS
    assert ctx["payment"].transaction_reference_id == "CLOSED-REFERENCE"
    assert ctx["payment_plan"].status == PaymentPlan.Status.CLOSED
    assert ctx["file_temp"].extras == {}


@pytest.mark.parametrize("override", [False, True])
def test_closed_plan_row_with_different_quantity_rejects_file(
    group_with_closed_plan, override, django_assert_num_queries
):
    ctx = group_with_closed_plan
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(ctx["payment"].unicef_id), Decimal("50.00")]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=override)
    service.open_workbook()

    with pytest.raises(XlsxPaymentPlanGroupDeliveryImportError):
        service.import_payment_list()

    assert service.skipped_rows == []
    assert len(service.errors) == 1
    assert service.errors[0].coordinates == "A2"
    assert f"CLOSED Payment Plan {ctx['payment_plan'].unicef_id}" in service.errors[0].message
    with django_assert_num_queries(2):
        ctx["payment"].refresh_from_db()
        ctx["payment_plan"].refresh_from_db()
    assert ctx["payment"].delivered_quantity == Decimal("100.00")
    assert ctx["payment"].status == Payment.STATUS_DISTRIBUTION_SUCCESS
    assert ctx["payment_plan"].status == PaymentPlan.Status.CLOSED


@pytest.mark.parametrize("override", [False, True])
def test_closed_plan_row_with_invalid_quantity_rejects_file(
    group_with_closed_plan, override, django_assert_num_queries
):
    ctx = group_with_closed_plan
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(ctx["payment"].unicef_id), "not-a-number"]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=override)
    service.open_workbook()

    with pytest.raises(XlsxPaymentPlanGroupDeliveryImportError):
        service.import_payment_list()

    assert service.skipped_rows == []
    assert len(service.errors) == 1
    assert service.errors[0].coordinates == "B2"
    with django_assert_num_queries(2):
        ctx["payment"].refresh_from_db()
        ctx["payment_plan"].refresh_from_db()
    assert ctx["payment"].delivered_quantity == Decimal("100.00")
    assert ctx["payment"].status == Payment.STATUS_DISTRIBUTION_SUCCESS
    assert ctx["payment_plan"].status == PaymentPlan.Status.CLOSED


@pytest.fixture
def group_with_closed_error_payment(group_with_closed_plan):
    ctx = group_with_closed_plan
    ctx["payment"].delivered_quantity = None
    ctx["payment"].delivered_quantity_usd = None
    ctx["payment"].status = Payment.STATUS_ERROR
    ctx["payment"].save(update_fields=["delivered_quantity", "delivered_quantity_usd", "status"])
    return ctx


@pytest.mark.parametrize("override", [False, True])
def test_closed_error_payment_treats_minus_one_as_matching_result(
    group_with_closed_error_payment, override, django_assert_num_queries
):
    ctx = group_with_closed_error_payment
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(ctx["payment"].unicef_id), Decimal(-1)]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=override)
    service.open_workbook()

    service.import_payment_list()

    assert service.errors == []
    assert len(service.skipped_rows) == 1
    with django_assert_num_queries(2):
        ctx["payment"].refresh_from_db()
        ctx["payment_plan"].refresh_from_db()
    assert ctx["payment"].delivered_quantity is None
    assert ctx["payment"].status == Payment.STATUS_ERROR
    assert ctx["payment_plan"].status == PaymentPlan.Status.CLOSED


@pytest.fixture
def mixed_group_with_closed_plan(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    ctx["plan_two"].status = PaymentPlan.Status.CLOSED
    ctx["plan_two"].save(update_fields=["status"])
    return ctx


@pytest.fixture
def mixed_group_with_reconciled_closed_plan(mixed_group_with_closed_plan):
    ctx = mixed_group_with_closed_plan
    ctx["payment_two"].delivered_quantity = Decimal("75.00")
    ctx["payment_two"].status = Payment.STATUS_DISTRIBUTION_PARTIAL
    ctx["payment_two"].transaction_reference_id = "CLOSED-REFERENCE"
    ctx["payment_two"].save(update_fields=["delivered_quantity", "status", "transaction_reference_id"])
    return ctx


@pytest.mark.parametrize("override", [False, True])
def test_mixed_group_rejects_file_containing_closed_plan_row(
    mixed_group_with_closed_plan, override, django_assert_num_queries
):
    ctx = mixed_group_with_closed_plan
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00")],
            [str(ctx["payment_two"].unicef_id), Decimal("75.00")],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=override)
    service.open_workbook()

    with pytest.raises(XlsxPaymentPlanGroupDeliveryImportError):
        service.import_payment_list()

    with django_assert_num_queries(2):
        ctx["payment_one"].refresh_from_db()
        ctx["payment_two"].refresh_from_db()
    assert ctx["payment_one"].delivered_quantity is None
    assert ctx["payment_two"].delivered_quantity is None
    assert len(service.errors) == 1
    assert service.errors[0].coordinates == "A3"
    assert "CLOSED Payment Plan" in service.errors[0].message


@pytest.mark.parametrize("override", [False, True])
def test_mixed_group_imports_open_plan_when_closed_plan_row_matches(
    mixed_group_with_reconciled_closed_plan, override, django_assert_num_queries
):
    ctx = mixed_group_with_reconciled_closed_plan
    file = _make_workbook(
        ["payment_id", "delivered_quantity", "reference_id"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00"), "OPEN-REFERENCE"],
            [str(ctx["payment_two"].unicef_id), Decimal("75.00"), "MUST-NOT-CHANGE"],
        ],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=override)
    service.open_workbook()

    service.import_payment_list()

    with django_assert_num_queries(3):
        ctx["payment_one"].refresh_from_db()
        ctx["payment_two"].refresh_from_db()
        ctx["plan_two"].refresh_from_db()
    assert ctx["payment_one"].delivered_quantity == Decimal("50.00")
    assert ctx["payment_one"].transaction_reference_id == "OPEN-REFERENCE"
    assert ctx["payment_two"].delivered_quantity == Decimal("75.00")
    assert ctx["payment_two"].status == Payment.STATUS_DISTRIBUTION_PARTIAL
    assert ctx["payment_two"].transaction_reference_id == "CLOSED-REFERENCE"
    assert ctx["plan_two"].status == PaymentPlan.Status.CLOSED
    assert service.errors == []
    assert len(service.skipped_rows) == 1


@pytest.mark.parametrize("override", [False, True])
def test_mixed_group_imports_file_omitting_closed_plan_rows(
    mixed_group_with_closed_plan, override, django_assert_num_queries
):
    ctx = mixed_group_with_closed_plan
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(ctx["payment_one"].unicef_id), Decimal("50.00")]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=override)
    service.open_workbook()

    service.import_payment_list()

    with django_assert_num_queries(2):
        ctx["payment_one"].refresh_from_db()
        ctx["payment_two"].refresh_from_db()
    assert ctx["payment_one"].delivered_quantity == Decimal("50.00")
    assert ctx["payment_two"].delivered_quantity is None
    assert service.errors == []


def test_normal_import_skips_non_pending_payment_without_quantity(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    payment.status = Payment.STATUS_ERROR
    payment.save(update_fields=["status"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(payment.unicef_id), Decimal("50.00")]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    service.import_payment_list()

    payment.refresh_from_db()
    assert payment.status == Payment.STATUS_ERROR
    assert payment.delivered_quantity is None
    assert (
        service.skipped_rows[0]["reason"]
        == f"Payment status {Payment.STATUS_ERROR} is not eligible for this import mode."
    )


def test_override_allows_correcting_error_payment(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    payment.status = Payment.STATUS_ERROR
    payment.save(update_fields=["status"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(payment.unicef_id), Decimal("50.00")]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=True)
    service.open_workbook()

    service.import_payment_list()

    payment.refresh_from_db()
    assert payment.status == Payment.STATUS_DISTRIBUTION_PARTIAL
    assert payment.delivered_quantity == Decimal("50.00")


def test_override_skips_manually_cancelled_payment(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    payment.status = Payment.STATUS_MANUALLY_CANCELLED
    payment.delivered_quantity = Decimal("20.00")
    payment.save(update_fields=["status", "delivered_quantity"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(payment.unicef_id), Decimal("50.00")]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=True)
    service.open_workbook()

    service.import_payment_list()

    payment.refresh_from_db()
    assert payment.status == Payment.STATUS_MANUALLY_CANCELLED
    assert payment.delivered_quantity == Decimal("20.00")
    assert service.skipped_rows[0]["reason"] == (
        f"Payment status {Payment.STATUS_MANUALLY_CANCELLED} is not eligible for this import mode."
    )


@pytest.fixture
def group_with_cancelled_row_containing_text_quantity(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_two"]
    payment.status = Payment.STATUS_MANUALLY_CANCELLED
    payment.save(update_fields=["status"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00")],
            [str(payment.unicef_id), "N/A"],
        ],
    )
    return {**ctx, "file": file}


@pytest.mark.parametrize("override", [False, True])
def test_import_skips_ineligible_text_quantity_and_saves_valid_rows(
    group_with_cancelled_row_containing_text_quantity, override, django_assert_num_queries
):
    ctx = group_with_cancelled_row_containing_text_quantity
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], ctx["file"], override=override)
    service.open_workbook()
    service.validate()
    assert service.errors == []

    service.import_payment_list()

    with django_assert_num_queries(2):
        ctx["payment_one"].refresh_from_db()
        ctx["payment_two"].refresh_from_db()
    assert ctx["payment_one"].delivered_quantity == Decimal("50.00")
    assert ctx["payment_two"].status == Payment.STATUS_MANUALLY_CANCELLED
    assert ctx["payment_two"].delivered_quantity is None
    assert service.skipped_rows == [
        {
            "row": 3,
            "payment_id": str(ctx["payment_two"].unicef_id),
            "reason": f"Payment status {Payment.STATUS_MANUALLY_CANCELLED} is not eligible for this import mode.",
        }
    ]


@pytest.fixture
def group_workbook_with_gap_before_invalid_row(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [
            [str(ctx["payment_one"].unicef_id), Decimal("50.00")],
            [None, None],
            [None, None],
            [str(ctx["payment_two"].unicef_id), "invalid"],
        ],
    )
    return {**ctx, "file": file}


def test_group_validation_preserves_original_error_row_after_gaps(group_workbook_with_gap_before_invalid_row):
    ctx = group_workbook_with_gap_before_invalid_row
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], ctx["file"])
    service.open_workbook()

    service.validate()

    assert len(service.errors) == 1
    assert service.errors[0].coordinates == "B5"


def test_import_revalidates_conflicts_against_latest_payment_data(group_two_plans_one_fsp):
    ctx = group_two_plans_one_fsp
    payment = ctx["payment_one"]
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(payment.unicef_id), Decimal("50.00")]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()
    service.validate()
    assert service.errors == []
    payment.delivered_quantity = Decimal("40.00")
    payment.status = Payment.STATUS_DISTRIBUTION_PARTIAL
    payment.save(update_fields=["delivered_quantity", "status"])

    with pytest.raises(XlsxPaymentPlanGroupDeliveryImportError):
        service.import_payment_list()

    payment.refresh_from_db()
    assert payment.delivered_quantity == Decimal("40.00")


def test_override_reset_reopens_finished_plan_and_recalculates_totals(group_with_finished_usd_plan):
    ctx = group_with_finished_usd_plan
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(ctx["payment"].unicef_id), None]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file, override=True)
    service.open_workbook()

    service.import_payment_list()

    ctx["payment_plan"].refresh_from_db()
    assert ctx["payment_plan"].status == PaymentPlan.Status.ACCEPTED
    assert ctx["payment_plan"].total_entitled_quantity == Decimal("100.00")
    assert ctx["payment_plan"].total_entitled_quantity_usd == Decimal("100.00")
    assert ctx["payment_plan"].total_delivered_quantity == Decimal("0.00")
    assert ctx["payment_plan"].total_delivered_quantity_usd == Decimal("0.00")


def test_usd_reconciliation_saves_both_quantity_fields(group_with_finished_usd_plan):
    ctx = group_with_finished_usd_plan
    payment = ctx["payment"]
    payment.delivered_quantity = None
    payment.delivered_quantity_usd = None
    payment.status = Payment.STATUS_SENT_TO_FSP
    payment.save(update_fields=["delivered_quantity", "delivered_quantity_usd", "status"])
    ctx["payment_plan"].status = PaymentPlan.Status.ACCEPTED
    ctx["payment_plan"].save(update_fields=["status"])
    file = _make_workbook(
        ["payment_id", "delivered_quantity"],
        [[str(payment.unicef_id), Decimal("75.00")]],
    )
    service = XlsxPaymentPlanGroupDeliveryImportService(ctx["group"], file)
    service.open_workbook()

    service.import_payment_list()

    payment.refresh_from_db()
    assert payment.delivered_quantity == Decimal("75.00")
    assert payment.delivered_quantity_usd == Decimal("75.00")
