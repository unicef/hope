import pytest

from extras.test_utils.factories.household import (
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualRoleInHouseholdFactory,
)
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from hope.apps.household.const import ROLE_PRIMARY
from hope.apps.payment.services.payment_household_snapshot_service import create_payment_plan_snapshot_data
from hope.models import (
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    MergeStatusModel,
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
def household():
    household = HouseholdFactory(size=1)
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
def payment_with_snapshot_and_document(payment_plan, payment, registration_token_document):
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
