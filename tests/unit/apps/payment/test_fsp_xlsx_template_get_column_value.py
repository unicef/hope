from datetime import datetime

import pytest

from extras.test_utils.factories import AreaFactory, CountryFactory
from extras.test_utils.factories.household import (
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
)
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from hope.apps.core.field_attributes.fields_types import _HOUSEHOLD, _INDIVIDUAL
from hope.apps.household.const import ROLE_ALTERNATE, ROLE_PRIMARY
from hope.apps.payment.services.payment_household_snapshot_service import create_payment_plan_snapshot_data
from hope.models import (
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    MergeStatusModel,
    Payment,
    PaymentPlan,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def payment_plan():
    return PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
    )


@pytest.fixture
def delivery_mechanism():
    return DeliveryMechanismFactory(code="cash", name="Cash", payment_gateway_id="dm-cash")


@pytest.fixture
def fsp():
    return FinancialServiceProviderFactory(
        name="Test FSP 1",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        vision_vendor_number="123456789",
    )


@pytest.fixture
def admin2_area():
    return AreaFactory(name="Admin2 Area")


@pytest.fixture
def household(admin2_area):
    household = HouseholdFactory(size=1, admin2=admin2_area)
    if household.size is None:
        household.size = 1
        household.save(update_fields=["size"])
    if not household.individuals_and_roles.filter(role=ROLE_PRIMARY).exists():
        IndividualRoleInHouseholdFactory(
            household=household,
            individual=household.head_of_household,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
    return household


@pytest.fixture
def payment(payment_plan, household, fsp, delivery_mechanism):
    return PaymentFactory(
        parent=payment_plan,
        household=household,
        collector=household.head_of_household,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
        delivered_quantity=16.69,
    )


@pytest.fixture
def admin_areas_dict():
    return FinancialServiceProviderXlsxTemplate.get_areas_dict()


@pytest.fixture
def registration_token_document_type():
    return DocumentTypeFactory(label="Registration Token", key="registration_token")


@pytest.fixture
def registration_token_document(registration_token_document_type, household):
    return DocumentFactory(
        individual=household.head_of_household,
        program=household.program,
        document_number="REG-001",
        type=registration_token_document_type,
        rdi_merge_status=MergeStatusModel.MERGED,
    )


@pytest.fixture
def alternate_collector(household):
    alternate = IndividualFactory(
        household=household,
        business_area=household.business_area,
        program=household.program,
        registration_data_import=household.registration_data_import,
    )
    IndividualRoleInHouseholdFactory(
        household=household,
        individual=alternate,
        role=ROLE_ALTERNATE,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    return alternate


@pytest.fixture
def alternate_collector_documents(alternate_collector, household):
    doc_type_1 = DocumentTypeFactory(label="Alt Doc 1", key="alt_doc_1")
    doc_type_2 = DocumentTypeFactory(label="Alt Doc 2", key="alt_doc_2")
    DocumentFactory(
        individual=alternate_collector,
        program=household.program,
        document_number="ALT-001",
        type=doc_type_1,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    DocumentFactory(
        individual=alternate_collector,
        program=household.program,
        document_number="ALT-002",
        type=doc_type_2,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    return ["ALT-001", "ALT-002"]


@pytest.fixture
def payment_with_snapshot_and_document(payment_plan, payment, registration_token_document):
    create_payment_plan_snapshot_data(payment_plan)
    payment.refresh_from_db()
    return payment


@pytest.fixture
def payment_with_snapshot_and_alternate(payment_plan, payment, alternate_collector_documents):
    create_payment_plan_snapshot_data(payment_plan)
    payment.refresh_from_db()
    return payment


@pytest.mark.parametrize(
    ("field_name", "expected_value"),
    [
        ("payment_id", lambda payment, document: payment.unicef_id),
        ("household_id", lambda payment, document: payment.household.unicef_id),
        ("household_size", lambda payment, document: 1),
        ("collector_name", lambda payment, document: payment.collector.full_name),
        ("currency", lambda payment, document: "PLN"),
        ("registration_token", lambda payment, document: document.document_number),
        ("invalid_column_name", lambda payment, document: "wrong_column_name"),
        ("delivered_quantity", lambda payment, document: payment.delivered_quantity),
    ],
)
def test_get_column_value_from_payment(
    field_name,
    expected_value,
    payment_with_snapshot_and_document,
    admin_areas_dict,
    registration_token_document,
):
    payment = payment_with_snapshot_and_document
    value = FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(
        payment,
        field_name,
        admin_areas_dict,
    )

    assert value == expected_value(payment, registration_token_document)


def test_get_column_value_admin_level_2(
    payment_with_snapshot_and_document,
    admin_areas_dict,
    admin2_area,
):
    value = FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(
        payment_with_snapshot_and_document,
        "admin_level_2",
        admin_areas_dict,
    )

    assert value == admin2_area.name


def test_get_column_value_alternate_collector_document_numbers(
    payment_with_snapshot_and_alternate,
    admin_areas_dict,
    alternate_collector_documents,
):
    value = FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(
        payment_with_snapshot_and_alternate,
        "alternate_collector_document_numbers",
        admin_areas_dict,
    )

    assert value == ", ".join(alternate_collector_documents)


def test_get_column_value_delivered_quantity_error(payment_with_snapshot_and_document, admin_areas_dict):
    payment_with_snapshot_and_document.status = Payment.STATUS_ERROR
    payment_with_snapshot_and_document.save(update_fields=["status"])
    value = FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(
        payment_with_snapshot_and_document,
        "delivered_quantity",
        admin_areas_dict,
    )

    assert value == -1.0


def test_get_column_value_delivery_date_string(payment_with_snapshot_and_document, admin_areas_dict):
    payment_with_snapshot_and_document.delivery_date = datetime(2023, 5, 5).date()
    payment_with_snapshot_and_document.save(update_fields=["delivery_date"])
    value = FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(
        payment_with_snapshot_and_document,
        "delivery_date",
        admin_areas_dict,
    )

    assert value == str(payment_with_snapshot_and_document.delivery_date)


def test_get_column_value_no_snapshot(payment_plan, household, fsp, delivery_mechanism, admin_areas_dict):
    payment = PaymentFactory(
        parent=payment_plan,
        household=household,
        collector=household.head_of_household,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
        delivered_quantity=16.69,
    )
    value = FinancialServiceProviderXlsxTemplate.get_column_value_from_payment(
        payment,
        "payment_id",
        admin_areas_dict,
    )

    assert value is None


def test_get_data_from_payment_snapshot_country_present():
    country = CountryFactory(iso_code3="TST")
    household_data = {
        "country_id": str(country.pk),
        "primary_collector": {},
        "alternate_collector": {},
    }
    core_field = {"lookup": "country", "snapshot_field": "country_id__iso_code3"}
    result = FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(
        household_data,
        core_field,
        {},
        {str(country.pk): {"iso_code3": country.iso_code3}},
    )

    assert result == "TST"


def test_get_data_from_payment_snapshot_country_missing():
    household_data = {
        "country_id": "missing",
        "primary_collector": {},
        "alternate_collector": {},
    }
    core_field = {"lookup": "country", "snapshot_field": "country_id__iso_code3"}
    result = FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(
        household_data,
        core_field,
        {},
        {},
    )

    assert result is None


def test_get_data_from_payment_snapshot_area_present(admin2_area):
    household_data = {
        "admin2_id": str(admin2_area.pk),
        "primary_collector": {},
        "alternate_collector": {},
    }
    core_field = {"lookup": "admin2", "snapshot_field": "admin2_id__name"}
    result = FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(
        household_data,
        core_field,
        {str(admin2_area.pk): {"p_code": admin2_area.p_code, "name": admin2_area.name}},
        {},
    )

    assert result == f"{admin2_area.p_code} - {admin2_area.name}"


def test_get_data_from_payment_snapshot_area_missing():
    household_data = {
        "admin2_id": "missing",
        "primary_collector": {},
        "alternate_collector": {},
    }
    core_field = {"lookup": "admin2", "snapshot_field": "admin2_id__name"}
    result = FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(
        household_data,
        core_field,
        {},
        {},
    )

    assert result is None


def test_get_data_from_payment_snapshot_roles_match(payment_with_snapshot_and_alternate):
    household_data = payment_with_snapshot_and_alternate.household_snapshot.snapshot_data
    core_field = {"lookup": "role", "snapshot_field": "roles__role"}
    result = FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(
        household_data,
        core_field,
        {},
        {},
    )

    assert result == ROLE_PRIMARY


def test_get_data_from_payment_snapshot_roles_no_lookup_id():
    household_data = {"roles": [{"role": ROLE_PRIMARY, "individual": {"id": "id-1"}}]}
    core_field = {"lookup": "role", "snapshot_field": "roles__role"}
    result = FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(
        household_data,
        core_field,
        {},
        {},
    )

    assert result is None


def test_get_data_from_payment_snapshot_primary_collector_id():
    household_data = {"primary_collector": {"id": "ind-1"}}
    core_field = {"lookup": "id", "snapshot_field": "primary_collector__id"}
    result = FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(
        household_data,
        core_field,
        {},
        {},
    )

    assert result == "ind-1"


def test_get_data_from_payment_snapshot_documents_found(
    payment_with_snapshot_and_document,
):
    household_data = payment_with_snapshot_and_document.household_snapshot.snapshot_data
    core_field = {"lookup": "document_number", "snapshot_field": "documents__registration_token__document_number"}
    result = FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(
        household_data,
        core_field,
        {},
        {},
    )

    assert result == "REG-001"


def test_get_data_from_payment_snapshot_documents_missing(payment_with_snapshot_and_document):
    household_data = payment_with_snapshot_and_document.household_snapshot.snapshot_data
    core_field = {"lookup": "document_number", "snapshot_field": "documents__missing_doc__document_number"}
    result = FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(
        household_data,
        core_field,
        {},
        {},
    )

    assert result is None


def test_get_data_from_payment_snapshot_associated_individual():
    household_data = {"primary_collector": {"given_name": "Anna"}}
    core_field = {"lookup": "given_name", "associated_with": _INDIVIDUAL}
    result = FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(
        household_data,
        core_field,
        {},
        {},
    )

    assert result == "Anna"


def test_get_data_from_payment_snapshot_associated_household():
    household_data = {"unicef_id": "HH-123"}
    core_field = {"lookup": "unicef_id", "associated_with": _HOUSEHOLD}
    result = FinancialServiceProviderXlsxTemplate.get_data_from_payment_snapshot(
        household_data,
        core_field,
        {},
        {},
    )

    assert result == "HH-123"


def test_get_column_from_core_field_missing_core_field(payment_with_snapshot_and_document):
    value = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment_with_snapshot_and_document,
        "unknown_core_field",
        {},
        {},
    )

    assert value is None


def test_get_column_from_core_field_no_snapshot(payment_plan, household, fsp, delivery_mechanism):
    payment = PaymentFactory(
        parent=payment_plan,
        household=household,
        collector=household.head_of_household,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
        delivered_quantity=16.69,
    )
    value = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment,
        "country_origin",
        {},
        {},
    )

    assert value is None


def test_get_column_from_core_field_country_origin(
    payment_plan,
    fsp,
    delivery_mechanism,
):
    country = CountryFactory(iso_code3="TST")
    household = HouseholdFactory(country_origin=country)
    payment = PaymentFactory(
        parent=payment_plan,
        household=household,
        collector=household.head_of_household,
        financial_service_provider=fsp,
        delivery_type=delivery_mechanism,
    )
    create_payment_plan_snapshot_data(payment_plan)
    payment.refresh_from_db()
    value = FinancialServiceProviderXlsxTemplate.get_column_from_core_field(
        payment,
        "country_origin",
        {},
        {str(country.pk): {"iso_code3": country.iso_code3}},
    )

    assert value == "TST"
