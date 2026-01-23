import os
from unittest.mock import patch

from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    PaymentFactory,
    UserFactory,
)

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
def payment():
    return PaymentFactory()


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
