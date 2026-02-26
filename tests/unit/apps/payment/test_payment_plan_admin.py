from decimal import Decimal
import os
from unittest.mock import PropertyMock, patch

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    DeliveryMechanismFactory,
    FileTempFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    PaymentFactory,
    PaymentPlanFactory,
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
def staff_user():
    user = UserFactory(
        username="staff_user",
        email="staff@root.com",
        is_staff=True,
        is_superuser=False,
        is_active=True,
        status="ACTIVE",
    )
    user.set_password("password")
    user.save()
    return user


@pytest.fixture
def staff_client(client, staff_user):
    client.force_login(staff_user, backend="django.contrib.auth.backends.ModelBackend")
    return client


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
def payment_plan(financial_service_provider, delivery_mechanism):
    return PaymentPlanFactory(
        name="Test Plan",
        status=PaymentPlan.Status.ACCEPTED,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism,
    )


@pytest.fixture
def payment(payment_plan, delivery_mechanism, financial_service_provider):
    return PaymentFactory(
        parent=payment_plan,
        delivery_type=delivery_mechanism,
        financial_service_provider=financial_service_provider,
    )


@pytest.fixture
def file_temp():
    return FileTempFactory()


@pytest.fixture
def fsp_template(payment_plan):
    template = FinancialServiceProviderXlsxTemplateFactory(name="Test Template AAA")
    fsp = FinancialServiceProviderFactory()
    fsp.allowed_business_areas.add(payment_plan.business_area)
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


def test_payment_plan_get_recalculate_exchange_rate_confirmation(admin_client, payment_plan) -> None:
    payment_plan.exchange_rate = Decimal("2.00")
    payment_plan.save(update_fields=["exchange_rate"])
    url = reverse(
        "admin:payment_paymentplan_recalculate_exchange_rate",
        args=[payment_plan.pk],
    )
    response = admin_client.get(url)

    assert response.status_code == 200
    assert "Do you confirm to recalculate USD values based on provided exchange rate?" in response.content.decode(
        "utf-8"
    )


@patch("hope.admin.payment_plan.PaymentPlan.update_money_fields")
def test_payment_plan_post_recalculate_exchange_rate_with_permission(
    mock_update_money_fields,
    staff_user,
    staff_client,
    payment_plan,
    delivery_mechanism,
    financial_service_provider,
) -> None:
    content_type = ContentType.objects.get_for_model(PaymentPlan)
    permission, _ = Permission.objects.get_or_create(
        content_type=content_type,
        codename="can_recalculate_exchange_rate",
        defaults={"name": "Can recalculate USD values based on exchange rate"},
    )
    base_permissions = Permission.objects.filter(
        content_type=content_type,
        codename__in=["view_paymentplan", "change_paymentplan"],
    )
    staff_user.user_permissions.set([*base_permissions, permission])

    payment_plan.currency = "PLN"
    payment_plan.exchange_rate = Decimal("2.00")
    payment_plan.save(update_fields=["currency", "exchange_rate"])
    payment = PaymentFactory(
        parent=payment_plan,
        delivery_type=delivery_mechanism,
        financial_service_provider=financial_service_provider,
        entitlement_quantity=Decimal("100.00"),
        delivered_quantity=Decimal("40.00"),
        entitlement_quantity_usd=Decimal("1.00"),
        delivered_quantity_usd=Decimal("1.00"),
        currency="PLN",
    )
    url = reverse(
        "admin:payment_paymentplan_recalculate_exchange_rate",
        args=[payment_plan.pk],
    )

    response = staff_client.post(url)
    payment.refresh_from_db()

    mock_update_money_fields.assert_called_once()
    assert payment.entitlement_quantity_usd == Decimal("50.00")
    assert payment.delivered_quantity_usd == Decimal("20.00")
    assert response.status_code == 302
    assert reverse("admin:payment_paymentplan_change", args=[payment_plan.pk]) in response["Location"]


@patch("hope.admin.payment_plan.PaymentPlan.update_money_fields")
def test_payment_plan_post_recalculate_exchange_rate_without_permission(
    mock_update_money_fields,
    staff_user,
    staff_client,
    payment_plan,
    delivery_mechanism,
    financial_service_provider,
) -> None:
    content_type = ContentType.objects.get_for_model(PaymentPlan)
    base_permissions = Permission.objects.filter(
        content_type=content_type,
        codename__in=["view_paymentplan", "change_paymentplan"],
    )
    staff_user.user_permissions.set(base_permissions)

    payment_plan.currency = "PLN"
    payment_plan.exchange_rate = Decimal("2.00")
    payment_plan.save(update_fields=["currency", "exchange_rate"])
    payment = PaymentFactory(
        parent=payment_plan,
        delivery_type=delivery_mechanism,
        financial_service_provider=financial_service_provider,
        entitlement_quantity=Decimal("100.00"),
        delivered_quantity=Decimal("40.00"),
        entitlement_quantity_usd=Decimal("1.00"),
        delivered_quantity_usd=Decimal("1.00"),
        currency="PLN",
    )
    url = reverse(
        "admin:payment_paymentplan_recalculate_exchange_rate",
        args=[payment_plan.pk],
    )

    response = staff_client.post(url)
    payment.refresh_from_db()

    mock_update_money_fields.assert_not_called()
    assert payment.entitlement_quantity_usd == Decimal("1.00")
    assert payment.delivered_quantity_usd == Decimal("1.00")
    assert response.status_code == 403


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
