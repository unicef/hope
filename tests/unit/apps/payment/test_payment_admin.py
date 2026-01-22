import os
from unittest.mock import patch

from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.models import FinancialServiceProvider, PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def mock_payment_gateway_env_vars() -> None:
    with patch.dict(
        os.environ,
        {"PAYMENT_GATEWAY_API_KEY": "TEST", "PAYMENT_GATEWAY_API_URL": "TEST"},
    ):
        yield


@pytest.fixture
def business_area():
    return BusinessAreaFactory()


@pytest.fixture
def admin_user():
    user = UserFactory(
        username="root",
        email="root@root.com",
        is_staff=True,
        is_superuser=True,
        is_active=True,
        status="ACTIVE",
    )
    user.set_password("password")
    user.save()
    return user


@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user, backend="django.contrib.auth.backends.ModelBackend")
    return client


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program_cycle(program):
    return ProgramCycleFactory(program=program)


@pytest.fixture
def delivery_mechanism():
    return DeliveryMechanismFactory()


@pytest.fixture
def financial_service_provider(delivery_mechanism):
    return FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
        payment_gateway_id="test123",
        delivery_mechanisms=[delivery_mechanism],
    )


@pytest.fixture
def payment_plan(business_area, program_cycle, financial_service_provider, delivery_mechanism):
    return PaymentPlanFactory(
        name="Test Plan",
        status=PaymentPlan.Status.ACCEPTED,
        business_area=business_area,
        program_cycle=program_cycle,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism,
    )


@pytest.fixture
def registration_data_import(business_area, program, admin_user):
    return RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        imported_by=admin_user,
    )


@pytest.fixture
def household(business_area, program, registration_data_import):
    return HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import,
    )


@pytest.fixture
def payment(payment_plan, business_area, program, household, delivery_mechanism, financial_service_provider):
    return PaymentFactory(
        parent=payment_plan,
        business_area=business_area,
        program=program,
        household=household,
        head_of_household=household.head_of_household,
        collector=household.head_of_household,
        delivery_type=delivery_mechanism,
        financial_service_provider=financial_service_provider,
    )


@patch("hope.apps.payment.services.payment_gateway.PaymentGatewayService.sync_record")
@patch("hope.admin.payment_plan.has_payment_pg_sync_permission", return_value=True)
def test_payment_post_sync_with_payment_gateway(mock_perm, mock_sync, admin_client, payment) -> None:
    url = reverse("admin:payment_payment_sync_with_payment_gateway", args=[payment.pk])
    response = admin_client.post(url)

    mock_sync.assert_called_once_with(payment)
    assert response.status_code == 302
    assert reverse("admin:payment_payment_change", args=[payment.pk]) in response["Location"]


@patch("hope.admin.payment_plan.has_payment_pg_sync_permission", return_value=True)
def test_payment_get_sync_with_payment_gateway_confirmation(mock_perm, admin_client, payment) -> None:
    url = reverse("admin:payment_payment_sync_with_payment_gateway", args=[payment.pk])
    response = admin_client.get(url)

    assert response.status_code == 200
    assert "Do you confirm to Sync with Payment Gateway?" in response.content.decode("utf-8")
