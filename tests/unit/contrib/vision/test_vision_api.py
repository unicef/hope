from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from hope.apps.core.api.mixins import BaseAPI
from hope.contrib.vision.api import VisionAPI, VisionAPIError, VisionAPIMissingCredentialsError


@pytest.fixture(autouse=True)
def mock_vision_env_vars(settings) -> None:
    settings.VISION_API_URL = "https://test.example.com/"
    settings.VISION_CLIENT_ID = "test-client"
    settings.VISION_CLIENT_SECRET = "test-secret"
    settings.VISION_TOKEN_GRANT_TYPE = "client_credentials"
    settings.VISION_DEFAULT_TIMEOUT = 60


def test_missing_vision_url_raises_error(settings) -> None:
    settings.VISION_API_URL = ""
    with pytest.raises(VisionAPIMissingCredentialsError):
        VisionAPI()


def test_ensure_token_skips_when_valid() -> None:
    api = VisionAPI()
    api._token_expiry = datetime.now() + timedelta(hours=1)
    with patch.object(api, "_acquire_token") as mock_acquire:
        api._ensure_token()
        mock_acquire.assert_not_called()


def test_ensure_token_acquires_when_expired() -> None:
    api = VisionAPI()
    api._token_expiry = datetime.now() - timedelta(hours=1)
    with patch.object(api, "_acquire_token") as mock_acquire:
        api._ensure_token()
        mock_acquire.assert_called_once()


def test_no_auth_header_before_token() -> None:
    api = VisionAPI()
    assert api._client.headers.get("Authorization") is None or "None" not in api._client.headers.get(
        "Authorization", ""
    )


@patch("hope.contrib.vision.api.requests.post")
def test_acquire_token_sets_bearer(mock_post) -> None:
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "access_token": "oauth-token-123",
            "expires_in": "3600",
        },
    )
    api = VisionAPI()
    api._acquire_token()
    assert api._client.headers["Authorization"] == "Bearer oauth-token-123"
    assert api._token_expiry is not None


@patch("hope.contrib.vision.api.requests.post")
def test_acquire_token_401_raises_error(mock_post) -> None:
    mock_post.return_value = MagicMock(
        status_code=401,
        json=lambda: {"ErrorCode": "401", "Error": "Unauthorized"},
    )
    api = VisionAPI()
    with pytest.raises(VisionAPIError):
        api._acquire_token()


@patch("hope.contrib.vision.api.requests.post")
def test_acquire_token_missing_credentials_raises_error(mock_post, settings) -> None:
    settings.VISION_CLIENT_ID = ""
    api = VisionAPI()
    with pytest.raises(VisionAPIMissingCredentialsError):
        api._acquire_token()
    mock_post.assert_not_called()


def _make_mock_payment_plan(**overrides) -> MagicMock:
    defaults = {
        "unicef_id": "PP001",
        "name": "Monthly payment plan testing the content length",
        "status": "NEW",
        "business_area_id": "ba-1",
        "currency_id": "usd-1",
        "total_entitled_quantity": "10000.00",
        "total_entitled_quantity_usd": "10000.00",
        "created_at": datetime(2025, 1, 1),
    }
    fields = {**defaults, **overrides}
    pp = MagicMock()
    for k, v in fields.items():
        setattr(pp, k, v)
    pp.business_area.code = fields.get("_business_area_code", "FI01")
    pp.currency.code = fields.get("_currency_code", "USD")
    pp.financial_service_provider.name = fields.get("_fsp_name", "Head Vendor Name")
    pp.financial_service_provider.vision_vendor_number = fields.get("_vision_vendor_number", "V100004")
    pp.internal_data = {}
    return pp


@patch("hope.contrib.vision.api.VisionAPI._acquire_token")
@patch("hope.contrib.vision.api.VisionAPI._post")
def test_send_payment_plan(mock_post, mock_acquire_token) -> None:
    mock_post.return_value = ({"status": "ok"}, 200)
    api = VisionAPI()
    pp = _make_mock_payment_plan(unicef_id="PP001")
    result = api.send_payment_plan(pp)
    assert result == {"status": "ok"}
    mock_acquire_token.assert_called_once()
    mock_post.assert_called_once_with(
        "https://test.example.com/ps/ezcash/PaymentPlan",
        {
            "businessArea": "FI01",
            "vendorNumber": "V100004",
            "payplanSno": "PP001",
            "payplanDesc": "Monthly payment plan testing the content length",
            "currency": "USD",
            "authAmt": "10000.00",
            "authAmtUsd": "10000.00",
            "status": "NEW",
            "headVendor": "Head Vendor Name",
            "creationDate": "20250101",
        },
    )


@patch("hope.contrib.vision.api.VisionAPI._acquire_token")
@patch("hope.contrib.vision.api.VisionAPI._post")
def test_send_payment_plan_with_creation_date(mock_post, mock_acquire_token) -> None:
    mock_post.return_value = ({"status": "ok"}, 200)
    api = VisionAPI()
    pp = _make_mock_payment_plan(
        unicef_id="PP002",
        created_at=datetime(2025, 6, 15, 10, 30, 0),
    )
    result = api.send_payment_plan(pp)
    assert result == {"status": "ok"}
    mock_post.assert_called_once_with(
        "https://test.example.com/ps/ezcash/PaymentPlan",
        {
            "businessArea": "FI01",
            "vendorNumber": "V100004",
            "payplanSno": "PP002",
            "payplanDesc": "Monthly payment plan testing the content length",
            "currency": "USD",
            "authAmt": "10000.00",
            "authAmtUsd": "10000.00",
            "status": "NEW",
            "headVendor": "Head Vendor Name",
            "creationDate": "20250615",
        },
    )


@patch("hope.contrib.vision.api.VisionAPI._acquire_token")
@patch("hope.contrib.vision.api.VisionAPI._post")
def test_send_payment_plan_with_different_currency(mock_post, mock_acquire_token) -> None:
    mock_post.return_value = ({"status": "ok"}, 200)
    api = VisionAPI()
    pp = _make_mock_payment_plan(
        unicef_id="PP003",
        _currency_code="EUR",
        created_at=datetime(2025, 3, 1),
    )
    result = api.send_payment_plan(pp)
    assert result == {"status": "ok"}
    mock_post.assert_called_once_with(
        "https://test.example.com/ps/ezcash/PaymentPlan",
        {
            "businessArea": "FI01",
            "vendorNumber": "V100004",
            "payplanSno": "PP003",
            "payplanDesc": "Monthly payment plan testing the content length",
            "currency": "EUR",
            "authAmt": "10000.00",
            "authAmtUsd": "10000.00",
            "status": "NEW",
            "headVendor": "Head Vendor Name",
            "creationDate": "20250301",
        },
    )


def test_vision_api_error_is_raised() -> None:
    with patch("hope.contrib.vision.api.VisionAPI._acquire_token"):
        with patch("hope.contrib.vision.api.VisionAPI._post") as mock_post:
            mock_post.side_effect = BaseAPI.APIError("boom")
            api = VisionAPI()
            pp = _make_mock_payment_plan()
            with pytest.raises(VisionAPIError):
                api.send_payment_plan(pp)
            assert "vision" in pp.internal_data
            entry = pp.internal_data["vision"]["log"][0]
            assert entry["type"] == "api-call"
            assert datetime.fromisoformat(entry["timestamp"])
            assert entry["response"]["error"] == "boom"
            pp.save.assert_called_once_with(update_fields=["internal_data"])


def test_send_payment_plan_logs_4xx_error() -> None:
    with patch("hope.contrib.vision.api.VisionAPI._acquire_token"):
        with patch("hope.contrib.vision.api.VisionAPI._post") as mock_post:
            mock_post.side_effect = BaseAPI.APIError(
                'VisionAPI Invalid response: <Response [400]>, b\'{"error": "bad request"}\', https://test.example.com/ps/ezcash/PaymentPlan'
            )
            api = VisionAPI()
            pp = _make_mock_payment_plan()
            with pytest.raises(VisionAPIError):
                api.send_payment_plan(pp)
            assert "vision" in pp.internal_data
            assert len(pp.internal_data["vision"]["log"]) == 1
            entry = pp.internal_data["vision"]["log"][0]
            assert entry["type"] == "api-call"
            assert entry["payload"]["payplanSno"] == "PP001"
            assert "400" in entry["response"]["error"]
            pp.save.assert_called_once_with(update_fields=["internal_data"])


@patch("hope.contrib.vision.api.VisionAPI._acquire_token")
@patch("hope.contrib.vision.api.VisionAPI._post")
def test_send_payment_plan_logs_payload_and_response(mock_post, mock_acquire_token) -> None:
    mock_post.return_value = ({"status": "ok", "messageId": "msg-42"}, 200)
    api = VisionAPI()
    pp = _make_mock_payment_plan(unicef_id="PP042")
    pp.internal_data = {}
    result = api.send_payment_plan(pp)
    assert result == {"status": "ok", "messageId": "msg-42"}
    assert "vision" in pp.internal_data
    assert pp.internal_data["vision"]["sent"] is True
    assert set(pp.internal_data["vision"]) == {"log", "sent"}
    assert len(pp.internal_data["vision"]["log"]) == 1
    entry = pp.internal_data["vision"]["log"][0]
    assert entry["type"] == "api-call"
    assert datetime.fromisoformat(entry["timestamp"])
    assert entry["payload"]["payplanSno"] == "PP042"
    assert entry["response"]["messageId"] == "msg-42"
    pp.save.assert_called_once_with(update_fields=["internal_data"])


@patch("hope.contrib.vision.api.VisionAPI._acquire_token")
@patch("hope.contrib.vision.api.VisionAPI._post")
def test_send_payment_plan_already_sent_raises_error(mock_post, mock_acquire_token) -> None:
    api = VisionAPI()
    pp = _make_mock_payment_plan(unicef_id="PP042")
    pp.sent_to_vision = True
    with pytest.raises(VisionAPIError):
        api.send_payment_plan(pp)
    mock_acquire_token.assert_not_called()
    mock_post.assert_not_called()


@patch("hope.models.APILogEntry.objects.create")
@patch("hope.contrib.vision.views.PaymentPlan.objects.get")
def test_callback_view_success(mock_get, mock_log_entry) -> None:
    from rest_framework.test import APIRequestFactory, force_authenticate

    from hope.contrib.vision.views import PaymentPlanCallbackView

    mock_pp = _make_mock_payment_plan(unicef_id="PP043")
    mock_get.return_value = mock_pp
    mock_user = MagicMock()
    mock_token = MagicMock()
    mock_token.grants = ["API_VISION_PP_CREATE"]

    factory = APIRequestFactory()
    request = factory.post(
        "/api/rest/systems/vision/payment-plan-callback/",
        {
            "messageId": "AGoSIRjbhXM_6L58Q2zj3MevWx81",
            "payplanSno": "PP043",
            "vision_payplanSno": "00000062",
            "business_area": "0060",
            "status": "SUCCESS",
            "error_message": "",
            "fc_num": "",
            "timestamp": "20260525122706",
        },
        format="json",
    )
    force_authenticate(request, user=mock_user, token=mock_token)

    view = PaymentPlanCallbackView.as_view()
    response = view(request)

    assert response.status_code == 200
    mock_get.assert_called_once_with(unicef_id="PP043")
    mock_pp.save.assert_called_once_with(update_fields=["internal_data"])
    assert response.data == {
        "status": "OK",
        "messageId": "AGoSIRjbhXM_6L58Q2zj3MevWx81",
        "payplanSno": "PP043",
    }
    assert "vision" in mock_pp.internal_data
    entry = mock_pp.internal_data["vision"]["log"][0]
    assert entry["type"] == "push-notification"
    assert datetime.fromisoformat(entry["timestamp"])
    assert entry["payload"]["payplanSno"] == "PP043"
    assert entry["response"]["status"] == "OK"
    assert mock_pp.internal_data["vision"]["vision_id"] == "00000062"


@patch("hope.models.APILogEntry.objects.create")
@patch("hope.contrib.vision.views.PaymentPlan.objects.get")
def test_callback_view_success_with_fc_num(mock_get, mock_log_entry) -> None:
    from rest_framework.test import APIRequestFactory, force_authenticate

    from hope.contrib.vision.views import PaymentPlanCallbackView

    mock_pp = _make_mock_payment_plan(unicef_id="PP044")
    mock_get.return_value = mock_pp
    mock_user = MagicMock()
    mock_token = MagicMock()
    mock_token.grants = ["API_VISION_PP_CREATE"]

    factory = APIRequestFactory()
    request = factory.post(
        "/api/rest/systems/vision/payment-plan-callback/",
        {
            "messageId": "msg-002",
            "payplanSno": "PP044",
            "vision_payplanSno": "00000063",
            "business_area": "0060",
            "status": "SUCCESS",
            "error_message": "",
            "fc_num": "FC123",
            "timestamp": "20260525122706",
        },
        format="json",
    )
    force_authenticate(request, user=mock_user, token=mock_token)

    view = PaymentPlanCallbackView.as_view()
    response = view(request)

    assert response.status_code == 200
    assert response.data == {
        "status": "OK",
        "messageId": "msg-002",
        "payplanSno": "PP044",
    }
    assert mock_pp.internal_data["vision"]["vision_id"] == "00000063"
    assert mock_pp.internal_data["vision"]["fc_num"] == "FC123"
    mock_pp.save.assert_called_once_with(update_fields=["internal_data"])


@patch("hope.models.APILogEntry.objects.create")
@patch("hope.contrib.vision.views.PaymentPlan.objects.get")
def test_callback_view_success_missing_vision_payplan_sno(mock_get, mock_log_entry) -> None:
    from rest_framework.test import APIRequestFactory, force_authenticate

    from hope.contrib.vision.views import PaymentPlanCallbackView

    mock_pp = _make_mock_payment_plan(unicef_id="PP045")
    mock_get.return_value = mock_pp
    mock_user = MagicMock()
    mock_token = MagicMock()
    mock_token.grants = ["API_VISION_PP_CREATE"]

    factory = APIRequestFactory()
    request = factory.post(
        "/api/rest/systems/vision/payment-plan-callback/",
        {
            "messageId": "msg-003",
            "payplanSno": "PP045",
            "status": "SUCCESS",
        },
        format="json",
    )
    force_authenticate(request, user=mock_user, token=mock_token)

    view = PaymentPlanCallbackView.as_view()
    response = view(request)

    assert response.status_code == 400
    assert response.data == {
        "status": "KO",
        "messageId": "msg-003",
        "payplanSno": "PP045",
    }
    mock_get.assert_called_once_with(unicef_id="PP045")
    mock_pp.save.assert_called_once_with(update_fields=["internal_data"])
    entry = mock_pp.internal_data["vision"]["log"][0]
    assert entry["type"] == "push-notification"
    assert entry["payload"]["payplanSno"] == "PP045"
    assert entry["response"]["status"] == "KO"


@patch("hope.models.APILogEntry.objects.create")
@patch("hope.contrib.vision.views.PaymentPlan.objects.get")
def test_callback_view_not_found_returns_400(mock_get, mock_log_entry) -> None:
    from rest_framework.test import APIRequestFactory, force_authenticate

    from hope.contrib.vision.views import PaymentPlanCallbackView
    from hope.models import PaymentPlan

    mock_get.side_effect = PaymentPlan.DoesNotExist
    mock_user = MagicMock()
    mock_token = MagicMock()
    mock_token.grants = ["API_VISION_PP_CREATE"]

    factory = APIRequestFactory()
    request = factory.post(
        "/api/rest/systems/vision/payment-plan-callback/",
        {"payplanSno": "UNKNOWN", "messageId": "abc123"},
        format="json",
    )
    force_authenticate(request, user=mock_user, token=mock_token)

    view = PaymentPlanCallbackView.as_view()
    response = view(request)

    assert response.status_code == 400
    assert response.data == {
        "status": "KO",
        "messageId": "abc123",
        "payplanSno": "UNKNOWN",
    }


@patch("hope.models.APILogEntry.objects.create")
@patch("hope.contrib.vision.views.PaymentPlan.objects.get")
def test_callback_view_non_success_status(mock_get, mock_log_entry) -> None:
    from rest_framework.test import APIRequestFactory, force_authenticate

    from hope.contrib.vision.views import PaymentPlanCallbackView

    mock_pp = _make_mock_payment_plan(unicef_id="PP043")
    mock_get.return_value = mock_pp
    mock_user = MagicMock()
    mock_token = MagicMock()
    mock_token.grants = ["API_VISION_PP_CREATE"]

    factory = APIRequestFactory()
    request = factory.post(
        "/api/rest/systems/vision/payment-plan-callback/",
        {
            "messageId": "msg-001",
            "payplanSno": "PP043",
            "vision_payplanSno": "00000062",
            "status": "ERROR",
            "error_message": "something went wrong",
        },
        format="json",
    )
    force_authenticate(request, user=mock_user, token=mock_token)

    view = PaymentPlanCallbackView.as_view()
    response = view(request)

    assert response.status_code == 200
    mock_get.assert_called_once_with(unicef_id="PP043")
    mock_pp.save.assert_called_once_with(update_fields=["internal_data"])
    assert response.data == {
        "status": "OK",
        "messageId": "msg-001",
        "payplanSno": "PP043",
    }
    assert "vision" in mock_pp.internal_data
    entry = mock_pp.internal_data["vision"]["log"][0]
    assert entry["type"] == "push-notification"
    assert entry["payload"]["payplanSno"] == "PP043"
    assert entry["response"]["status"] == "OK"
    assert "vision_id" not in mock_pp.internal_data["vision"]
    assert "fc_num" not in mock_pp.internal_data["vision"]


@patch("hope.models.APILogEntry.objects.create")
@patch("hope.contrib.vision.views.PaymentPlan.objects.get")
def test_callback_view_unauthenticated(mock_get, mock_log_entry) -> None:
    from rest_framework.test import APIRequestFactory

    from hope.contrib.vision.views import PaymentPlanCallbackView

    factory = APIRequestFactory()
    request = factory.post(
        "/api/rest/systems/vision/payment-plan-callback/",
        {"payplanSno": "PP043"},
        format="json",
    )

    view = PaymentPlanCallbackView.as_view()
    response = view(request)

    assert response.status_code in (401, 403)
    mock_get.assert_not_called()


@patch("hope.models.APILogEntry.objects.create")
@patch("hope.contrib.vision.views.PaymentPlan.objects.get")
def test_callback_view_missing_payplan_sno(mock_get, mock_log_entry) -> None:
    from rest_framework.test import APIRequestFactory, force_authenticate

    from hope.contrib.vision.views import PaymentPlanCallbackView

    mock_user = MagicMock()
    mock_token = MagicMock()
    mock_token.grants = ["API_VISION_PP_CREATE"]

    factory = APIRequestFactory()
    request = factory.post(
        "/api/rest/systems/vision/payment-plan-callback/",
        {"messageId": "msg-001"},
        format="json",
    )
    force_authenticate(request, user=mock_user, token=mock_token)

    view = PaymentPlanCallbackView.as_view()
    response = view(request)

    assert response.status_code == 400
    assert response.data == {
        "status": "KO",
        "messageId": "msg-001",
        "payplanSno": "",
    }
    mock_get.assert_not_called()
