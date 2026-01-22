import os
from unittest.mock import PropertyMock, patch

from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DeliveryMechanismFactory,
    FileTempFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.admin.payment_plan import can_regenerate_export_file_per_fsp, can_sync_with_payment_gateway
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


@pytest.fixture
def file_temp():
    return FileTempFactory()


@pytest.fixture
def fsp_template(business_area):
    template = FinancialServiceProviderXlsxTemplateFactory(name="Test Template AAA")
    fsp = FinancialServiceProviderFactory()
    fsp.allowed_business_areas.add(business_area)
    fsp.xlsx_templates.add(template)
    return template


@pytest.fixture
def payment_gateway_fsp(delivery_mechanism):
    return FinancialServiceProviderFactory(
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        payment_gateway_id="pg-1",
        delivery_mechanisms=[delivery_mechanism],
    )


@patch("hope.apps.payment.services.payment_gateway.PaymentGatewayService.sync_payment_plan")
@patch("hope.admin.payment_plan.has_payment_plan_pg_sync_permission", return_value=True)
def test_payment_plan_post_sync_with_payment_gateway(mock_perm, mock_sync, admin_client, payment_plan) -> None:
    url = reverse(
        "admin:payment_paymentplan_sync_with_payment_gateway",
        args=[payment_plan.pk],
    )
    response = admin_client.post(url)

    mock_sync.assert_called_once_with(payment_plan)
    assert response.status_code == 302
    assert reverse("admin:payment_paymentplan_change", args=[payment_plan.pk]) in response["Location"]


@patch("hope.admin.payment_plan.has_payment_plan_pg_sync_permission", return_value=True)
def test_payment_plan_get_sync_with_payment_gateway_confirmation(mock_perm, admin_client, payment_plan) -> None:
    url = reverse(
        "admin:payment_paymentplan_sync_with_payment_gateway",
        args=[payment_plan.pk],
    )
    response = admin_client.get(url)

    assert response.status_code == 200
    assert "Do you confirm to Sync with Payment Gateway?" in response.content.decode("utf-8")


def test_payment_plan_related_configs_button(admin_client, payment_plan) -> None:
    url = reverse("admin:payment_paymentplan_related_configs", args=[payment_plan.pk])
    response = admin_client.get(url)
    assert response.status_code == 302
    assert reverse("admin:payment_deliverymechanismconfig_changelist") in response["Location"]


@patch("hope.apps.payment.services.payment_gateway.PaymentGatewayService.add_missing_records_to_payment_instructions")
@patch("hope.admin.payment_plan.has_payment_plan_pg_sync_permission", return_value=True)
def test_payment_post_sync_missing_records_with_payment_gateway(
    mock_perm, mock_sync, admin_client, payment_plan
) -> None:
    url = reverse(
        "admin:payment_paymentplan_sync_missing_records_with_payment_gateway",
        args=[payment_plan.pk],
    )
    response = admin_client.post(url)

    mock_sync.assert_called_once_with(payment_plan)
    assert response.status_code == 302
    assert reverse("admin:payment_paymentplan_change", args=[payment_plan.pk]) in response["Location"]


@patch("hope.admin.payment_plan.has_payment_plan_pg_sync_permission", return_value=True)
def test_payment_get_sync_missing_records_with_payment_gateway(mock_perm, admin_client, payment_plan) -> None:
    url = reverse(
        "admin:payment_paymentplan_sync_missing_records_with_payment_gateway",
        args=[payment_plan.pk],
    )
    response = admin_client.get(url)

    assert response.status_code == 200
    assert "Do you confirm to Sync with Payment Gateway missing Records?" in response.content.decode("utf-8")


@patch("hope.admin.payment_plan.has_payment_plan_export_per_fsp_permission", return_value=True)
def test_get_regenerate_export_xlsx_form(mock_perm, admin_client, payment_plan) -> None:
    url = reverse("admin:payment_paymentplan_regenerate_export_xlsx", args=[payment_plan.pk])
    response = admin_client.get(url)
    assert response.status_code == 200
    assert "Select a template if you want the export to include the FSP Auth Code" in response.content.decode("utf-8")
    assert "form" in response.context


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.export_xlsx_per_fsp")
@patch("hope.admin.payment_plan.has_payment_plan_export_per_fsp_permission", return_value=True)
def test_post_regenerate_export_xlsx_without_template(
    mock_perm, mock_export, admin_client, admin_user, payment_plan
) -> None:
    url = reverse("admin:payment_paymentplan_regenerate_export_xlsx", args=[payment_plan.pk])
    response = admin_client.post(url, {"template": ""})

    mock_export.assert_called_once_with(admin_user.pk, None)
    assert response.status_code == 302
    assert reverse("admin:payment_paymentplan_change", args=[payment_plan.pk]) in response["Location"]


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.export_xlsx_per_fsp")
@patch("hope.admin.payment_plan.has_payment_plan_export_per_fsp_permission", return_value=True)
def test_post_regenerate_export_xlsx_with_template(
    mock_perm, mock_export, admin_client, admin_user, payment_plan, fsp_template
) -> None:
    url = reverse("admin:payment_paymentplan_regenerate_export_xlsx", args=[payment_plan.pk])
    response = admin_client.post(url, {"template": fsp_template.id})

    mock_export.assert_called_once_with(admin_user.pk, str(fsp_template.id))
    assert response.status_code == 302
    assert reverse("admin:payment_paymentplan_change", args=[payment_plan.pk]) in response["Location"]


@pytest.mark.parametrize(
    ("pp_status", "fsp_is_payment_gateway", "expected"),
    [
        (PaymentPlan.Status.ACCEPTED, True, True),
        (PaymentPlan.Status.ACCEPTED, False, False),
        (PaymentPlan.Status.OPEN, True, False),
        (PaymentPlan.Status.OPEN, False, False),
    ],
)
def test_can_sync_with_payment_gateway(payment_plan, pp_status, fsp_is_payment_gateway, expected) -> None:
    payment_plan.status = pp_status
    payment_plan.save(update_fields=["status"])
    with patch.object(
        FinancialServiceProvider,
        "is_payment_gateway",
        new_callable=PropertyMock,
        return_value=fsp_is_payment_gateway,
    ):
        assert can_sync_with_payment_gateway(payment_plan) is expected


@pytest.mark.parametrize(
    ("status", "background_action_status", "has_export_file_per_fsp", "expected"),
    [
        (PaymentPlan.Status.ACCEPTED, None, True, True),
        (PaymentPlan.Status.ACCEPTED, PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING, True, False),
        (PaymentPlan.Status.ACCEPTED, None, False, False),
        (
            PaymentPlan.Status.ACCEPTED,
            PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
            False,
            False,
        ),
        (PaymentPlan.Status.FINISHED, None, True, True),
        (PaymentPlan.Status.FINISHED, PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING, True, False),
        (PaymentPlan.Status.FINISHED, None, False, False),
        (
            PaymentPlan.Status.FINISHED,
            PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
            False,
            False,
        ),
        (PaymentPlan.Status.OPEN, None, True, False),
        (PaymentPlan.Status.OPEN, PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING, True, False),
        (PaymentPlan.Status.OPEN, None, False, False),
        (
            PaymentPlan.Status.OPEN,
            PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING,
            False,
            False,
        ),
    ],
)
def test_can_regenerate_export_file_per_fsp(
    payment_plan, file_temp, status, background_action_status, has_export_file_per_fsp, expected
) -> None:
    payment_plan.status = status
    payment_plan.export_file_per_fsp = file_temp if has_export_file_per_fsp else None
    payment_plan.background_action_status = background_action_status
    assert can_regenerate_export_file_per_fsp(payment_plan) is expected
