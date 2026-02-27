from decimal import Decimal
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest import mock
from unittest.mock import patch
import zipfile

from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.urls import reverse
import pytest
from rest_framework.exceptions import ValidationError

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
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.household.const import IDENTIFICATION_TYPE_NATIONAL_ID, ROLE_PRIMARY
from hope.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from hope.apps.payment.flows import PaymentPlanFlow
from hope.apps.payment.services.payment_household_snapshot_service import create_payment_plan_snapshot_data
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.apps.payment.utils import to_decimal
from hope.apps.payment.xlsx.xlsx_error import XlsxError
from hope.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import XlsxPaymentPlanExportPerFspService
from hope.apps.payment.xlsx.xlsx_payment_plan_export_service import XlsxPaymentPlanExportService
from hope.apps.payment.xlsx.xlsx_payment_plan_import_service import XlsxPaymentPlanImportService
from hope.models import (
    DataCollectingType,
    Document,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    FlexibleAttribute,
    FspXlsxTemplatePerDeliveryMechanism,
    IndividualRoleInHousehold,
    MergeStatusModel,
    PaymentHouseholdSnapshot,
    PaymentPlan,
    PaymentPlanSplit,
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
    return ProgramCycleFactory(program=program)


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
            currency="PLN",
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


def test_export_payment_plan_payment_list_per_fsp(payment_plan, payments, user):
    payment_plan.status = PaymentPlan.Status.ACCEPTED
    payment_plan.save()

    payment = payment_plan.eligible_payments.first()
    assert payment.token_number is None
    assert payment.order_number is None

    export_service = XlsxPaymentPlanExportPerFspService(payment_plan)
    export_service.generate_token_and_order_numbers(payment_plan.eligible_payments.all(), payment_plan.program)
    payment.refresh_from_db(fields=["token_number", "order_number"])
    assert len(str(payment.token_number)) == 7
    assert len(str(payment.order_number)) == 9

    export_service.export_per_fsp(user)

    assert payment_plan.has_export_file
    assert payment_plan.payment_list_export_file_link is not None
    assert payment_plan.export_file_per_fsp.file.name.startswith(f"payment_plan_payment_list_{payment_plan.unicef_id}")
    fsp_id = payment_plan.financial_service_provider_id
    with zipfile.ZipFile(payment_plan.export_file_per_fsp.file, mode="r") as zip_file:  # type: ignore
        file_list = zip_file.namelist()
        fsp_xlsx_template_per_delivery_mechanism_list = FspXlsxTemplatePerDeliveryMechanism.objects.filter(
            financial_service_provider_id=fsp_id,
        )
        file_list_fsp = [
            f.replace(".xlsx", "").replace(f"payment_plan_payment_list_{payment_plan.unicef_id}_FSP_", "")
            for f in file_list
        ]
        for fsp_xlsx_template_per_delivery_mechanism in fsp_xlsx_template_per_delivery_mechanism_list:
            assert (
                f"{fsp_xlsx_template_per_delivery_mechanism.financial_service_provider.name}_"
                f"{fsp_xlsx_template_per_delivery_mechanism.delivery_mechanism}" in file_list_fsp
            )


@patch("hope.models.payment_plan_split.PaymentPlanSplit.MIN_NO_OF_PAYMENTS_IN_CHUNK")
def test_export_payment_plan_payment_list_per_split(
    min_no_of_payments_in_chunk_mock: Any,
    payment_plan,
    payments,
    user,
):
    min_no_of_payments_in_chunk_mock.__get__ = mock.Mock(return_value=2)

    payment_plan.status = PaymentPlan.Status.ACCEPTED
    payment_plan.save()

    payment_items = payment_plan.eligible_payments.all()
    assert payment_items.count() == 3

    pp_service = PaymentPlanService(payment_plan)
    pp_service.split(PaymentPlanSplit.SplitType.BY_RECORDS, 2)

    export_service = XlsxPaymentPlanExportPerFspService(payment_plan)
    export_service.export_per_fsp(user)

    assert payment_plan.has_export_file
    assert payment_plan.payment_list_export_file_link is not None
    assert payment_plan.export_file_per_fsp.file.name.startswith(f"payment_plan_payment_list_{payment_plan.unicef_id}")
    splits_count = payment_plan.splits.count()
    assert splits_count == 2
    with zipfile.ZipFile(payment_plan.export_file_per_fsp.file, mode="r") as zip_file:  # type: ignore
        file_list = zip_file.namelist()
        assert splits_count == len(file_list)

    pp_service.split(PaymentPlanSplit.SplitType.BY_COLLECTOR)

    export_service = XlsxPaymentPlanExportPerFspService(payment_plan)
    export_service.export_per_fsp(user)
    payment_plan.refresh_from_db()
    assert payment_plan.has_export_file
    assert payment_plan.payment_list_export_file_link is not None
    assert payment_plan.export_file_per_fsp.file.name.startswith(f"payment_plan_payment_list_{payment_plan.unicef_id}")
    splits_count = payment_plan.splits.count()
    assert splits_count == 3
    with zipfile.ZipFile(payment_plan.export_file_per_fsp.file, mode="r") as zip_file:  # type: ignore
        file_list = zip_file.namelist()
        assert splits_count == len(file_list)


def test_payment_row_flex_fields(payment_plan, fsp, payments, flex_decimal_attribute, flex_date_attribute):
    core_fields = [
        "account_holder_name",
    ]
    flex_fields = [
        flex_decimal_attribute.name,
        flex_date_attribute.name,
    ]

    export_service = XlsxPaymentPlanExportPerFspService(payment_plan)
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


def test_export_payment_plan_per_fsp_with_people_program(payment_plan, fsp, delivery_mechanisms, payments, user):
    payment_plan.status = PaymentPlan.Status.ACCEPTED
    payment_plan.save()
    export_service = XlsxPaymentPlanExportPerFspService(payment_plan)
    export_service.export_per_fsp(user)
    assert not payment_plan.program.is_social_worker_program

    delivery_mechanism = payment_plan.delivery_mechanism
    fsp_instance = payment_plan.financial_service_provider
    export_service.open_workbook(fsp_instance.name)
    fsp_xlsx_template = export_service.get_template(fsp_instance, delivery_mechanism)
    template_column_list = export_service.prepare_headers(fsp_xlsx_template)
    assert len(template_column_list) == len(FinancialServiceProviderXlsxTemplate.DEFAULT_COLUMNS) - 3
    assert "household_id" in template_column_list
    assert "household_size" in template_column_list
    assert "individual_id" not in template_column_list

    program_sw = ProgramFactory(
        business_area=payment_plan.business_area,
        data_collecting_type__type=DataCollectingType.Type.SOCIAL,
        beneficiary_group__master_detail=False,
    )
    program_sw_cycle = ProgramCycleFactory(program=program_sw)
    payment_plan.program_cycle = program_sw_cycle
    payment_plan.save()

    export_service = XlsxPaymentPlanExportPerFspService(payment_plan)
    export_service.export_per_fsp(user)

    payment_plan.refresh_from_db()
    assert payment_plan.has_export_file
    assert payment_plan.program.is_social_worker_program

    fsp_xlsx_template.core_fields = [
        "age",
        "zip_code",
        "household_unicef_id",
        "individual_unicef_id",
    ]
    fsp_xlsx_template.columns = fsp_xlsx_template.DEFAULT_COLUMNS
    fsp_xlsx_template.save()
    fsp_xlsx_template.refresh_from_db()

    export_service.open_workbook(fsp_instance.name)
    fsp_xlsx_template = export_service.get_template(fsp_instance, delivery_mechanism)

    template_column_list = export_service.prepare_headers(fsp_xlsx_template)
    fsp_xlsx_template.refresh_from_db()
    assert len(template_column_list) == 30
    assert "household_id" not in template_column_list
    assert "household_size" not in template_column_list
    assert "individual_id" in template_column_list
    assert fsp_xlsx_template.core_fields == [
        "age",
        "zip_code",
        "household_unicef_id",
        "individual_unicef_id",
    ]
    assert "age" in template_column_list
    assert "zip_code" in template_column_list
    assert "household_unicef_id" not in template_column_list
    assert "individual_unicef_id" in template_column_list

    assert (
        FspXlsxTemplatePerDeliveryMechanism.objects.filter(
            delivery_mechanism=delivery_mechanisms["atm_card"],
            financial_service_provider=fsp,
        ).count()
        == 0
    )
    export_service = XlsxPaymentPlanExportPerFspService(payment_plan)
    with pytest.raises(ValidationError) as excinfo:
        export_service.get_template(fsp, delivery_mechanisms["atm_card"])
    assert (
        f"Not possible to generate export file. There isn't any FSP XLSX Template assigned to Payment "
        f"Plan {payment_plan.unicef_id} for FSP {fsp.name} and delivery "
        f"mechanism {DeliveryMechanismChoices.DELIVERY_TYPE_ATM_CARD}." in str(excinfo.value)
    )


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
    export_service = XlsxPaymentPlanExportPerFspService(payment_plan)
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

    export_service = XlsxPaymentPlanExportPerFspService(payment_plan)
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
    export_service = XlsxPaymentPlanExportPerFspService(payment_plan)
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
