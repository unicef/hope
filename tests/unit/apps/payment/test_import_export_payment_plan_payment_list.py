from decimal import Decimal
from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from unittest import mock
from unittest.mock import patch

from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.urls import reverse
import pytest

from extras.test_utils.factories.account import RoleAssignmentFactory, RoleFactory, UserFactory
from extras.test_utils.factories.core import BusinessAreaFactory, FileTempFactory, FlexibleAttributeFactory
from extras.test_utils.factories.geo import CountryFactory
from extras.test_utils.factories.household import DocumentFactory, HouseholdFactory
from extras.test_utils.factories.payment import (
    AccountFactory,
    AccountTypeFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanSplitFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.household.const import IDENTIFICATION_TYPE_NATIONAL_ID, ROLE_PRIMARY
from hope.apps.payment.flows import PaymentPlanFlow
from hope.apps.payment.services.payment_household_snapshot_service import create_payment_plan_snapshot_data
from hope.apps.payment.utils import to_decimal
from hope.apps.payment.xlsx.xlsx_error import XlsxError
from hope.apps.payment.xlsx.xlsx_payment_plan_base_service import XlsxPaymentPlanBaseService
from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_export_service import XlsxPaymentPlanDeliveryExportService
from hope.apps.payment.xlsx.xlsx_payment_plan_export_service import XlsxPaymentPlanExportService
from hope.apps.payment.xlsx.xlsx_payment_plan_import_service import XlsxPaymentPlanImportService
from hope.models import (
    DataCollectingType,
    Document,
    FinancialServiceProvider,
    FlexibleAttribute,
    IndividualRoleInHousehold,
    MergeStatusModel,
    Payment,
    PaymentHouseholdSnapshot,
)

pytestmark = pytest.mark.django_db


def valid_file() -> File:
    content = Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/pp_payment_list_valid.xlsx").read_bytes()
    return File(BytesIO(content), name="pp_payment_list_valid.xlsx")


def invalid_file() -> File:
    content = Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/pp_payment_list_invalid.xlsx").read_bytes()
    return File(BytesIO(content), name="pp_payment_list_invalid.xlsx")


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def country_origin():
    return CountryFactory(iso_code2="PL", iso_code3="POL", name="Poland", short_name="Poland")


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program_cycle(program):
    return program.cycles.first()


@pytest.fixture
def delivery_mechanisms():
    account_type = AccountTypeFactory(key="transfer", label="Transfer")
    return {
        "cash": DeliveryMechanismFactory(code="cash", name="Cash", payment_gateway_id="dm-cash"),
        "transfer": DeliveryMechanismFactory(
            code="transfer",
            name="Transfer",
            payment_gateway_id="dm-transfer",
            account_type=account_type,
        ),
        "atm_card": DeliveryMechanismFactory(code="atm_card", name="ATM Card", payment_gateway_id="dm-atm_card"),
    }


@pytest.fixture
def fsp(delivery_mechanisms):
    fsp = FinancialServiceProviderFactory(
        name="Test FSP 1",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        vision_vendor_number="123456789",
    )
    fsp.delivery_mechanisms.add(delivery_mechanisms["cash"])
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanisms["cash"],
    )
    return fsp


@pytest.fixture
def payment_plan(program_cycle, business_area, fsp, delivery_mechanisms):
    payment_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        business_area=business_area,
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanisms["cash"],
    )
    flow = PaymentPlanFlow(payment_plan)
    flow.status_lock()
    payment_plan.save()
    return payment_plan


@pytest.fixture
def payment_plan_split(payment_plan):
    return PaymentPlanSplitFactory(payment_plan=payment_plan)


@pytest.fixture
def households(business_area, program, country_origin):
    return [
        HouseholdFactory(
            business_area=business_area,
            program=program,
            size=size,
            address="Lorem Ipsum",
            country_origin=country_origin,
            village="TEST_VILLAGE",
        )
        for size in range(1, 4)
    ]


@pytest.fixture
def payments(payment_plan, payment_plan_split, households, fsp, delivery_mechanisms):
    return [
        PaymentFactory(
            parent=payment_plan,
            parent_split=payment_plan_split,
            household=household,
            collector=household.head_of_household,
            financial_service_provider=fsp,
            delivery_type=delivery_mechanisms["cash"],
            program=payment_plan.program,
            entitlement_quantity=Decimal("100.00"),
            entitlement_quantity_usd=Decimal("10.00"),
        )
        for household in households
    ]


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def xlsx_valid_file(payment_plan, user):
    file_temp = FileTempFactory(
        object_id=payment_plan.pk,
        content_type=get_content_type_for_model(payment_plan),
        created_by=user,
        file=valid_file(),
    )
    return file_temp.file


@pytest.fixture
def xlsx_invalid_file(payment_plan, user):
    file_temp = FileTempFactory(
        object_id=payment_plan.pk,
        content_type=get_content_type_for_model(payment_plan),
        created_by=user,
        file=invalid_file(),
    )
    return file_temp.file


@pytest.fixture
def flex_decimal_attribute():
    return FlexibleAttributeFactory(
        type=FlexibleAttribute.DECIMAL,
        name="flex_decimal_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        label={"English(EN)": "value"},
    )


@pytest.fixture
def flex_date_attribute():
    return FlexibleAttributeFactory(
        type=FlexibleAttribute.DECIMAL,
        name="flex_date_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
        label={"English(EN)": "value"},
    )


def test_import_invalid_file(payment_plan, xlsx_invalid_file, payments):
    error_msg = [
        XlsxError(
            "Payment Plan - Payment List",
            "A2",
            "This payment id 123123 is not in Payment Plan Payment List",
        ),
    ]
    service = XlsxPaymentPlanImportService(payment_plan, xlsx_invalid_file)
    wb = service.open_workbook()
    wb.active["A3"].value = str(payment_plan.eligible_payments.order_by("id")[1].unicef_id)

    service.validate()
    assert service.errors == error_msg


def test_import_invalid_file_without_required_columns(payment_plan):
    error_msg_1 = XlsxError(
        sheet="Payment Plan - Payment List",
        coordinates=None,
        message="Header entitlement_quantity is required",
    )
    error_msg_2 = XlsxError(
        sheet="Payment Plan - Payment List",
        coordinates=None,
        message="Header entitlement_quantity is required",
    )
    content = Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/pp_payment_list_unexpected_column.xlsx").read_bytes()
    file = BytesIO(content)

    service = XlsxPaymentPlanImportService(payment_plan, file)
    service.open_workbook()
    service.validate()

    assert error_msg_1 in service.errors
    assert error_msg_2 in service.errors


def test_import_valid_file(payment_plan, xlsx_valid_file, payments):
    payment_plan.exchange_rate = Decimal("1.00")
    payment_plan.save(update_fields=["exchange_rate"])
    not_excluded_payments = list(payment_plan.eligible_payments.order_by("id")[:2])
    payment_id_1 = str(not_excluded_payments[0].unicef_id)
    payment_id_2 = str(not_excluded_payments[1].unicef_id)
    payment_1 = not_excluded_payments[0]
    payment_2 = not_excluded_payments[1]

    service = XlsxPaymentPlanImportService(payment_plan, xlsx_valid_file)
    wb = service.open_workbook()

    wb.active["A2"].value = payment_id_1
    wb.active["A3"].value = payment_id_2

    service.validate()
    assert service.errors == []

    service.import_payment_list()
    payment_1.refresh_from_db()
    payment_2.refresh_from_db()

    assert to_decimal(wb.active["K2"].value) == payment_1.entitlement_quantity
    assert to_decimal(wb.active["K3"].value) == payment_2.entitlement_quantity


def test_import_valid_file_with_reordered_required_columns(payment_plan, payments):
    payment_plan.exchange_rate = Decimal("1.00")
    payment_plan.save(update_fields=["exchange_rate"])
    not_excluded_payments = list(payment_plan.eligible_payments.order_by("id")[:2])
    payment_1 = not_excluded_payments[0]
    payment_2 = not_excluded_payments[1]
    export_service = XlsxPaymentPlanExportService(payment_plan)
    wb = export_service.generate_workbook()
    ws = wb.active

    header_to_column_index = {ws.cell(row=1, column=index).value: index for index in range(1, ws.max_column + 1)}
    payment_id_column_index = header_to_column_index["payment_id"]
    entitlement_column_index = header_to_column_index["entitlement_quantity"]

    for row_index in range(1, ws.max_row + 1):
        payment_id_value = ws.cell(row=row_index, column=payment_id_column_index).value
        entitlement_value = ws.cell(row=row_index, column=entitlement_column_index).value
        ws.cell(row=row_index, column=payment_id_column_index).value = entitlement_value
        ws.cell(row=row_index, column=entitlement_column_index).value = payment_id_value

    header_to_column_index = {ws.cell(row=1, column=index).value: index for index in range(1, ws.max_column + 1)}
    payment_id_column_index = header_to_column_index["payment_id"]
    entitlement_column_index = header_to_column_index["entitlement_quantity"]
    ws.cell(row=2, column=payment_id_column_index).value = str(payment_1.unicef_id)
    ws.cell(row=3, column=payment_id_column_index).value = str(payment_2.unicef_id)
    ws.cell(row=2, column=entitlement_column_index).value = "111.00"
    ws.cell(row=3, column=entitlement_column_index).value = "222.00"

    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        file = BytesIO(tmp.read())

    service = XlsxPaymentPlanImportService(payment_plan, file)
    service.open_workbook()
    service.validate()
    assert service.errors == []

    service.import_payment_list()

    payment_1.refresh_from_db()
    payment_2.refresh_from_db()

    assert payment_1.entitlement_quantity == Decimal("111.00")
    assert payment_2.entitlement_quantity == Decimal("222.00")


def test_entitlement_import_updates_only_modified_rows_for_household_program(
    payment_plan,
    payments,
    django_assert_num_queries,
):
    payment_plan.exchange_rate = Decimal("1.00")
    payment_plan.save(update_fields=["exchange_rate"])
    PaymentHouseholdSnapshot.objects.all().delete()
    create_payment_plan_snapshot_data(payment_plan)

    payment_1, payment_2, payment_3 = list(payment_plan.eligible_payments.order_by("unicef_id"))
    original_amount_3 = payment_3.entitlement_quantity
    original_usd_3 = payment_3.entitlement_quantity_usd
    original_date_3 = payment_3.entitlement_date

    export_service = XlsxPaymentPlanExportService(payment_plan)
    wb = export_service.generate_workbook()
    ws = wb.active
    payment_id_col = export_service.headers.index(XlsxPaymentPlanBaseService.COLUMN_PAYMENT_ID) + 1
    entitlement_col = export_service.headers.index(XlsxPaymentPlanBaseService.COLUMN_ENTITLEMENT_QUANTITY) + 1

    assert ws.cell(row=2, column=payment_id_col).value == str(payment_1.unicef_id)
    assert ws.cell(row=3, column=payment_id_col).value == str(payment_2.unicef_id)
    assert ws.cell(row=4, column=payment_id_col).value == str(payment_3.unicef_id)

    ws.cell(row=2, column=entitlement_col).value = "111.00"
    ws.cell(row=3, column=entitlement_col).value = "222.00"

    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        file = BytesIO(tmp.read())

    import_service = XlsxPaymentPlanImportService(payment_plan, file)
    import_service.open_workbook()
    import_service.validate()
    assert import_service.errors == []

    # bulk_update of entitlements + signature_hash refresh path; pinned to catch N+1 regressions.
    # +2 constant queries for per-payment activity logging (bulk log insert, program m2m).
    ContentType.objects.get_for_model(Payment)  # warm cache so the count is order-independent
    with django_assert_num_queries(5):
        import_service.import_payment_list()

    payment_1.refresh_from_db()
    payment_2.refresh_from_db()
    payment_3.refresh_from_db()

    assert payment_1.entitlement_quantity == Decimal("111.00")
    assert payment_2.entitlement_quantity == Decimal("222.00")
    assert payment_1.entitlement_quantity_usd == Decimal("111.00")
    assert payment_2.entitlement_quantity_usd == Decimal("222.00")
    assert payment_3.entitlement_quantity == original_amount_3
    assert payment_3.entitlement_quantity_usd == original_usd_3
    assert payment_3.entitlement_date == original_date_3


def test_entitlement_import_updates_only_modified_rows_for_social_worker_program(
    payment_plan,
    payments,
    django_assert_num_queries,
):
    program = payment_plan.program
    program.beneficiary_group.master_detail = False
    program.beneficiary_group.save()
    program.data_collecting_type.type = DataCollectingType.Type.SOCIAL
    program.save()
    assert payment_plan.is_social_worker_program is True

    payment_plan.exchange_rate = Decimal("1.00")
    payment_plan.save(update_fields=["exchange_rate"])
    PaymentHouseholdSnapshot.objects.all().delete()
    create_payment_plan_snapshot_data(payment_plan)

    payment_1, payment_2, payment_3 = list(payment_plan.eligible_payments.order_by("unicef_id"))
    original_amount_3 = payment_3.entitlement_quantity
    original_usd_3 = payment_3.entitlement_quantity_usd
    original_date_3 = payment_3.entitlement_date

    export_service = XlsxPaymentPlanExportService(payment_plan)
    wb = export_service.generate_workbook()
    ws = wb.active
    payment_id_col = export_service.headers.index(XlsxPaymentPlanBaseService.COLUMN_PAYMENT_ID) + 1
    entitlement_col = export_service.headers.index(XlsxPaymentPlanBaseService.COLUMN_ENTITLEMENT_QUANTITY) + 1

    assert ws.cell(row=2, column=payment_id_col).value == str(payment_1.unicef_id)
    assert ws.cell(row=3, column=payment_id_col).value == str(payment_2.unicef_id)
    assert ws.cell(row=4, column=payment_id_col).value == str(payment_3.unicef_id)

    ws.cell(row=2, column=entitlement_col).value = "111.00"
    ws.cell(row=3, column=entitlement_col).value = "222.00"

    with NamedTemporaryFile() as tmp:
        wb.save(tmp.name)
        tmp.seek(0)
        file = BytesIO(tmp.read())

    import_service = XlsxPaymentPlanImportService(payment_plan, file)
    import_service.open_workbook()
    import_service.validate()
    assert import_service.errors == []

    # bulk_update of entitlements + signature_hash refresh path; pinned to catch N+1 regressions.
    # +2 constant queries for per-payment activity logging (bulk log insert, program m2m).
    ContentType.objects.get_for_model(Payment)  # warm cache so the count is order-independent
    with django_assert_num_queries(5):
        import_service.import_payment_list()

    payment_1.refresh_from_db()
    payment_2.refresh_from_db()
    payment_3.refresh_from_db()

    assert payment_1.entitlement_quantity == Decimal("111.00")
    assert payment_2.entitlement_quantity == Decimal("222.00")
    assert payment_1.entitlement_quantity_usd == Decimal("111.00")
    assert payment_2.entitlement_quantity_usd == Decimal("222.00")
    assert payment_3.entitlement_quantity == original_amount_3
    assert payment_3.entitlement_quantity_usd == original_usd_3
    assert payment_3.entitlement_date == original_date_3


def test_validate_headers_resolves_positions_when_mapping_empty(payment_plan, xlsx_valid_file):
    service = XlsxPaymentPlanImportService(payment_plan, xlsx_valid_file)
    service.open_workbook()
    service.header_to_index = {}

    with patch.object(service, "_resolve_header_positions", wraps=service._resolve_header_positions) as resolve_mock:
        service._validate_headers()

    resolve_mock.assert_called_once()
    assert service.errors == []


def test_validate_headers_does_not_resolve_when_mapping_present(payment_plan, xlsx_valid_file):
    service = XlsxPaymentPlanImportService(payment_plan, xlsx_valid_file)
    service.open_workbook()

    with patch.object(service, "_resolve_header_positions", wraps=service._resolve_header_positions) as resolve_mock:
        service._validate_headers()

    resolve_mock.assert_not_called()
    assert service.errors == []


def test_raise_if_required_columns_are_missing_resolves_when_mapping_empty(payment_plan):
    content = Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/pp_payment_list_unexpected_column.xlsx").read_bytes()
    service = XlsxPaymentPlanImportService(payment_plan, BytesIO(content))
    service.open_workbook()
    service.header_to_index = {}

    with patch.object(service, "_resolve_header_positions", wraps=service._resolve_header_positions) as resolve_mock:
        with pytest.raises(ValueError, match=r"Header .* is required"):
            service._raise_if_required_columns_are_missing()

    resolve_mock.assert_called_once()


def test_raise_if_required_columns_are_missing_does_not_resolve_when_mapping_present(payment_plan, xlsx_valid_file):
    service = XlsxPaymentPlanImportService(payment_plan, xlsx_valid_file)
    service.open_workbook()

    with patch.object(service, "_resolve_header_positions", wraps=service._resolve_header_positions) as resolve_mock:
        service._raise_if_required_columns_are_missing()

    resolve_mock.assert_not_called()


@pytest.mark.parametrize("entitlement_amount", [None, ""])
def test_validate_entitlement_ignores_empty_values(payment_plan, xlsx_valid_file, payments, entitlement_amount):
    payment = payment_plan.eligible_payments.order_by("id").first()
    assert payment is not None
    service = XlsxPaymentPlanImportService(payment_plan, xlsx_valid_file)
    service.open_workbook()
    row = next(service.ws_payments.iter_rows(min_row=2))
    row[service.header_to_index["payment_id"]].value = str(payment.unicef_id)
    row[service.header_to_index["entitlement_quantity"]].value = entitlement_amount

    service._validate_entitlement(row)

    assert service.is_updated is False


def test_validate_entitlement_marks_update_for_changed_value(payment_plan, xlsx_valid_file, payments):
    payment = payment_plan.eligible_payments.order_by("id").first()
    assert payment is not None
    service = XlsxPaymentPlanImportService(payment_plan, xlsx_valid_file)
    service.open_workbook()
    row = next(service.ws_payments.iter_rows(min_row=2))
    row[service.header_to_index["payment_id"]].value = str(payment.unicef_id)
    row[service.header_to_index["entitlement_quantity"]].value = "999.00"

    service._validate_entitlement(row)

    assert service.is_updated is True


def test_import_payment_list_uses_payment_plan_exchange_rate(payment_plan, xlsx_valid_file, payments):
    payment_plan.exchange_rate = Decimal("2.00")
    payment_plan.save(update_fields=["exchange_rate"])
    payment = payment_plan.eligible_payments.order_by("id").first()
    assert payment is not None

    service = XlsxPaymentPlanImportService(payment_plan, xlsx_valid_file)
    wb = service.open_workbook()
    wb.active["A2"].value = str(payment.unicef_id)
    wb.active["K2"].value = "111.00"

    with patch.object(payment_plan, "get_exchange_rate") as mock_get_exchange_rate:
        service.import_payment_list()

    payment.refresh_from_db()
    mock_get_exchange_rate.assert_not_called()
    assert payment.entitlement_quantity == Decimal("111.00")
    assert payment.entitlement_quantity_usd == Decimal("55.50")


def test_import_row_returns_none_for_unknown_payment_id(payment_plan, xlsx_valid_file, payments):
    payment_plan.exchange_rate = Decimal("1.00")
    payment_plan.save(update_fields=["exchange_rate"])
    service = XlsxPaymentPlanImportService(payment_plan, xlsx_valid_file)
    service.open_workbook()
    row = next(service.ws_payments.iter_rows(min_row=2))
    row[service.headers.index("payment_id")].value = "UNKNOWN-PAYMENT-ID"
    row[service.headers.index("entitlement_quantity")].value = "100.00"

    result = service._import_row(row)

    assert result is None


def test_import_row_returns_none_for_empty_entitlement(payment_plan, xlsx_valid_file, payments):
    payment_plan.exchange_rate = Decimal("1.00")
    payment_plan.save(update_fields=["exchange_rate"])
    payment = payment_plan.eligible_payments.order_by("id").first()
    assert payment is not None
    service = XlsxPaymentPlanImportService(payment_plan, xlsx_valid_file)
    service.open_workbook()
    row = next(service.ws_payments.iter_rows(min_row=2))
    row[service.headers.index("payment_id")].value = str(payment.unicef_id)
    row[service.headers.index("entitlement_quantity")].value = ""

    result = service._import_row(row)

    assert result is None


def test_import_row_returns_none_for_unchanged_entitlement(payment_plan, xlsx_valid_file, payments):
    payment_plan.exchange_rate = Decimal("1.00")
    payment_plan.save(update_fields=["exchange_rate"])
    payment = payment_plan.eligible_payments.order_by("id").first()
    assert payment is not None
    service = XlsxPaymentPlanImportService(payment_plan, xlsx_valid_file)
    service.open_workbook()
    row = next(service.ws_payments.iter_rows(min_row=2))
    row[service.headers.index("payment_id")].value = str(payment.unicef_id)
    row[service.headers.index("entitlement_quantity")].value = str(payment.entitlement_quantity)

    result = service._import_row(row)

    assert result is None


def test_import_payment_list_skips_blank_rows_and_flushes_by_batch_size(payment_plan, xlsx_valid_file, payments):
    payment_plan.exchange_rate = Decimal("1.00")
    payment_plan.save(update_fields=["exchange_rate"])
    service = XlsxPaymentPlanImportService(payment_plan, xlsx_valid_file)
    service.open_workbook()
    service.BATCH_SIZE = 1

    blank_row = [mock.Mock(value=None), mock.Mock(value=None)]
    non_blank_row = [mock.Mock(value="PAYMENT-ID"), mock.Mock(value=None)]
    service.ws_payments.iter_rows = mock.Mock(return_value=[tuple(blank_row), tuple(non_blank_row)])  # type: ignore[method-assign]

    imported_payment = mock.Mock()
    with (
        patch.object(service, "_import_row", return_value=imported_payment) as import_row_mock,
        patch.object(service, "_save_payments") as save_payments_mock,
    ):
        service.import_payment_list()

    import_row_mock.assert_called_once_with(tuple(non_blank_row))
    save_payments_mock.assert_called_once_with([imported_payment])


def test_export_payment_plan_payment_list(payment_plan, payments, user):
    payment = payment_plan.eligible_payments.order_by("unicef_id").first()
    DocumentFactory(
        status=Document.STATUS_VALID,
        program=payment_plan.program,
        type__key=IDENTIFICATION_TYPE_NATIONAL_ID.lower(),
        document_number="Test_Number_National_Id_123",
        individual=payment.collector,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    PaymentHouseholdSnapshot.objects.all().delete()
    assert payment.collector.documents.all().count() == 1
    create_payment_plan_snapshot_data(payment_plan)
    export_service = XlsxPaymentPlanExportService(payment_plan)
    export_service.save_xlsx_file(user)

    assert payment_plan.has_export_file

    wb = export_service.generate_workbook()

    assert wb.active["A2"].value == str(payment.unicef_id)
    assert wb.active["K2"].value == payment.entitlement_quantity
    assert wb.active["L2"].value == payment.entitlement_quantity_usd
    assert wb.active["F2"].value == "TEST_VILLAGE"
    assert wb.active["N1"].value == "national_id"
    assert wb.active["N2"].value == "Test_Number_National_Id_123"


def test_payment_row_flex_fields(payment_plan, fsp, payments, flex_decimal_attribute, flex_date_attribute):
    core_fields = [
        "account_holder_name",
    ]
    flex_fields = [
        flex_decimal_attribute.name,
        flex_date_attribute.name,
    ]

    export_service = XlsxPaymentPlanDeliveryExportService(payment_plan)
    fsp_xlsx_template = FinancialServiceProviderXlsxTemplateFactory(core_fields=core_fields, flex_fields=flex_fields)
    headers = export_service.prepare_headers(fsp_xlsx_template)
    payment = payments[0]
    household = payment.household
    individual = payment.collector
    individual.flex_fields = {
        flex_decimal_attribute.name: 123.45,
    }
    individual.save()
    household.flex_fields = {
        flex_date_attribute.name: "2021-01-01",
    }
    household.save()
    decimal_flexible_attribute_index = headers.index(flex_decimal_attribute.name)
    date_flexible_attribute_index = headers.index(flex_date_attribute.name)

    PaymentHouseholdSnapshot.objects.all().delete()
    create_payment_plan_snapshot_data(payment_plan)
    payment.refresh_from_db()

    payment_row = export_service.get_payment_row(payment)
    assert payment_row[decimal_flexible_attribute_index] == 123.45
    assert payment_row[date_flexible_attribute_index] == "2021-01-01"


def test_flex_fields_admin_visibility(client, business_area, flex_decimal_attribute, flex_date_attribute):
    user = UserFactory(is_superuser=True, is_staff=True, is_active=True)
    user.set_password("password")
    user.save()
    permission_list = [Permissions.PM_ADMIN_FINANCIAL_SERVICE_PROVIDER_UPDATE.name]
    role = RoleFactory(name="LOL", permissions=permission_list)
    RoleAssignmentFactory(user=user, role=role, business_area=business_area)
    client.login(username=user.username, password="password")
    instance = FinancialServiceProviderXlsxTemplateFactory(flex_fields=[], name="Test FSP XLSX Template")
    url = reverse(
        "admin:payment_financialserviceproviderxlsxtemplate_change",
        args=[instance.pk],
    )
    response: Any = client.get(url)
    assert response.status_code == 200
    assert "flex_fields" in response.context["adminform"].form.fields
    assert flex_decimal_attribute.name in (
        name for name, _ in response.context["adminform"].form.fields["flex_fields"].choices
    )
    assert flex_date_attribute.name in (
        name for name, _ in response.context["adminform"].form.fields["flex_fields"].choices
    )


def test_payment_row_get_flex_field_if_no_snapshot_data(payment_plan):
    export_service = XlsxPaymentPlanDeliveryExportService(payment_plan)
    payment = PaymentFactory(parent=payment_plan)
    empty_payment_row = export_service.get_payment_row(payment)
    for value in empty_payment_row:
        assert value == ""


def test_payment_row_get_account_fields_from_snapshot_data(payment_plan, payments, delivery_mechanisms):
    required_fields_for_account = [
        "name",
        "number",
        "uba_code",
        "holder_name",
        "financial_institution_pk",
        "financial_institution_name",
    ]
    IndividualRoleInHousehold.all_objects.all().delete()
    for payment in payment_plan.eligible_payments:
        payment.delivery_type = delivery_mechanisms["transfer"]
        payment.save()
        payment.refresh_from_db()
        payment.collector.household = payment.household
        payment.collector.save()
        IndividualRoleInHousehold.objects.get_or_create(
            role=ROLE_PRIMARY,
            household=payment.collector.household,
            individual=payment.collector,
            rdi_merge_status="MERGED",
        )
        payment.collector.household.__dict__.pop("primary_collector", None)
        payment.collector.household.__dict__.pop("alternate_collector", None)

        AccountFactory(
            number=payment.id,
            account_type=delivery_mechanisms["transfer"].account_type,
            individual=payment.collector,
            rdi_merge_status=MergeStatusModel.MERGED,
            data={
                "name": "Union Bank",
                "uba_code": "123456",
                "holder_name": f"Admin {payment.collector.given_name}",
            },
        )
    PaymentHouseholdSnapshot.objects.all().delete()
    create_payment_plan_snapshot_data(payment_plan)

    export_service = XlsxPaymentPlanDeliveryExportService(payment_plan)
    fsp_xlsx_template = FinancialServiceProviderXlsxTemplateFactory(core_fields=[], flex_fields=[])

    headers = export_service.prepare_headers(fsp_xlsx_template=fsp_xlsx_template)
    assert headers[-6:] == required_fields_for_account

    for payment in payment_plan.eligible_payments:
        payment_row = export_service.get_payment_row(payment)
        assert payment_row[-6] == "Union Bank"
        assert payment_row[-5] == str(payment.id)
        assert payment_row[-4] == "123456"
        assert payment_row[-3] == f"Admin {payment.collector.given_name}"
        assert payment_row[-2] == ""
        assert payment_row[-1] == ""

    for payment in payment_plan.eligible_payments:
        payment.household_snapshot.snapshot_data["primary_collector"]["account_data"].pop("number")
        payment.household_snapshot.snapshot_data["primary_collector"]["account_data"].pop("financial_institution_pk")
        payment.household_snapshot.snapshot_data["primary_collector"]["account_data"].pop("financial_institution_name")
        payment.household_snapshot.save()
    export_service = XlsxPaymentPlanDeliveryExportService(payment_plan)
    headers = export_service.prepare_headers(fsp_xlsx_template=fsp_xlsx_template)
    assert headers[-6:] == [
        "name",
        "uba_code",
        "holder_name",
        "financial_institution_pk",
        "financial_institution_name",
        "number",
    ]

    PaymentHouseholdSnapshot.objects.all().delete()
    payment_row_without_snapshot = export_service.get_payment_row(payment_plan.eligible_payments.first())
    assert payment_row_without_snapshot[-4] == ""


def test_headers_for_social_worker_program(payment_plan, xlsx_valid_file):
    program = payment_plan.program
    program.beneficiary_group.master_detail = False
    program.beneficiary_group.name = "People"
    program.beneficiary_group.save()
    program.data_collecting_type.type = DataCollectingType.Type.SOCIAL
    program.save()

    assert payment_plan.is_social_worker_program is True

    export_service = XlsxPaymentPlanExportService(payment_plan)
    assert len(export_service.headers) == 12
    assert "household_size" not in export_service.headers
    assert "household_id" not in export_service.headers
    assert "collector_id" not in export_service.headers
    assert "individual_id" in export_service.headers

    import_service = XlsxPaymentPlanImportService(payment_plan, xlsx_valid_file)
    assert len(import_service.headers) == 12
    assert "household_size" not in import_service.headers
    assert "household_id" not in import_service.headers
    assert "collector_id" not in export_service.headers
    assert "individual_id" in import_service.headers


def test_as_plain_text_returns_empty_string_for_none():
    assert XlsxPaymentPlanDeliveryExportService._as_plain_text(None) == ""


def test_as_plain_text_decodes_bytes():
    assert XlsxPaymentPlanDeliveryExportService._as_plain_text(b"secret") == "secret"


def test_as_plain_text_decodes_memoryview():
    assert XlsxPaymentPlanDeliveryExportService._as_plain_text(memoryview(b"mv-value")) == "mv-value"


def test_as_plain_text_returns_str_unchanged():
    assert XlsxPaymentPlanDeliveryExportService._as_plain_text("plain") == "plain"


def test_send_file_passwords_with_no_file_temp(user):
    with patch.object(user, "email_user") as mock_email:
        XlsxPaymentPlanDeliveryExportService._send_file_passwords(user, None, "Test Title")

    mock_email.assert_called_once()
    call_kwargs = mock_email.call_args[1]
    assert "Test Title" in call_kwargs["subject"]
    assert "ZIP file password: \n" in call_kwargs["text_body"]
    assert "XLSX file password: \n" in call_kwargs["text_body"]


def test_send_file_passwords_with_file_temp_sends_passwords(user):
    file_temp = FileTempFactory()
    file_temp.password = "zip-pw"
    file_temp.xlsx_password = "xlsx-pw"
    file_temp.save()

    with patch.object(user, "email_user") as mock_email:
        XlsxPaymentPlanDeliveryExportService._send_file_passwords(user, file_temp, "My Plan")

    mock_email.assert_called_once()
    call_kwargs = mock_email.call_args[1]
    assert "My Plan" in call_kwargs["subject"]
    assert "ZIP file password: zip-pw" in call_kwargs["text_body"]
    assert "XLSX file password: xlsx-pw" in call_kwargs["text_body"]


def test_send_delivery_passwords_sends_email_with_plan_title(payment_plan, user):
    with patch.object(user, "email_user") as mock_email:
        XlsxPaymentPlanDeliveryExportService.send_delivery_passwords(user, payment_plan)

    mock_email.assert_called_once()
    assert f"Payment Plan {payment_plan.unicef_id}" in mock_email.call_args[1]["subject"]


def test_send_delivery_passwords_for_file_sends_email_with_label(user):
    file_temp = FileTempFactory()
    with patch.object(user, "email_user") as mock_email:
        XlsxPaymentPlanDeliveryExportService.send_delivery_passwords_for_file(user, file_temp, "Batch Label")

    mock_email.assert_called_once()
    assert "Batch Label" in mock_email.call_args[1]["subject"]
