from collections.abc import Callable
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CurrencyFactory,
    FinancialServiceProviderFactory,
    PaymentPlanFactory,
)
from hope.apps.core.api.mixins import BaseAPI
from hope.contrib.vision.api import VisionAPI, VisionAPIError, VisionAPIMissingCredentialsError
from hope.contrib.vision.choices import VisionLogEntryType, VisionStatus
from hope.contrib.vision.services import VisionService
from hope.models import PaymentPlan


@pytest.fixture(autouse=True)
def mock_vision_env_vars(settings) -> None:
    settings.VISION_API_URL = "https://test.example.com/"
    settings.VISION_CLIENT_ID = "test-client"
    settings.VISION_CLIENT_SECRET = "test-secret"
    settings.VISION_TOKEN_GRANT_TYPE = "client_credentials"
    settings.VISION_DEFAULT_TIMEOUT = 60


@pytest.fixture
def vision_api_payment_plan_factory(db) -> Callable[..., PaymentPlan]:
    def create_payment_plan(
        *,
        unicef_id: str = "PP001",
        currency_code: str = "USD",
        created_at: datetime = datetime(2025, 1, 1),
    ) -> PaymentPlan:
        business_area = BusinessAreaFactory(code="FI01")
        currency = CurrencyFactory(code=currency_code)
        financial_service_provider = FinancialServiceProviderFactory(
            name="Head Vendor Name",
            vision_vendor_number="V100004",
        )
        payment_plan = PaymentPlanFactory(
            unicef_id=unicef_id,
            name="Monthly payment plan testing the content length",
            status=PaymentPlan.Status.IN_REVIEW,
            business_area=business_area,
            program_cycle__program__business_area=business_area,
            currency=currency,
            financial_service_provider=financial_service_provider,
            total_entitled_quantity="10000.00",
            total_entitled_quantity_usd="10000.00",
        )
        PaymentPlan.objects.filter(pk=payment_plan.pk).update(created_at=created_at)
        payment_plan.created_at = created_at
        return payment_plan

    return create_payment_plan


def test_missing_vision_url_raises_error(settings) -> None:
    settings.VISION_API_URL = ""
    with pytest.raises(VisionAPIMissingCredentialsError):
        VisionAPI()


def test_urls_are_built_from_a_base_with_a_trailing_slash() -> None:
    api = VisionAPI()

    assert api.token_url == "https://test.example.com/v1/OAuthService/GenerateToken"
    assert api.payment_plan_creation_url == "https://test.example.com/ps/ezcash/PaymentPlan"


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
        "status": PaymentPlan.Status.IN_REVIEW,
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
    pp.vision_status = "WAITING_FOR_CALLBACK"
    return pp


@patch("hope.contrib.vision.api.VisionAPI._acquire_token")
@patch("hope.contrib.vision.api.VisionAPI._post")
def test_send_payment_plan(mock_post, mock_acquire_token, vision_api_payment_plan_factory) -> None:
    mock_post.return_value = ({"status": "ok"}, 200)
    api = VisionAPI()
    pp = vision_api_payment_plan_factory(unicef_id="PP001")
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
            "status": PaymentPlan.Status.IN_REVIEW,
            "headVendor": "Head Vendor Name",
            "creationDate": "20250101",
        },
    )


@patch("hope.contrib.vision.api.VisionAPI._acquire_token")
@patch("hope.contrib.vision.api.VisionAPI._post")
def test_send_payment_plan_with_creation_date(
    mock_post,
    mock_acquire_token,
    vision_api_payment_plan_factory,
) -> None:
    mock_post.return_value = ({"status": "ok"}, 200)
    api = VisionAPI()
    pp = vision_api_payment_plan_factory(
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
            "status": PaymentPlan.Status.IN_REVIEW,
            "headVendor": "Head Vendor Name",
            "creationDate": "20250615",
        },
    )


@patch("hope.contrib.vision.api.VisionAPI._acquire_token")
@patch("hope.contrib.vision.api.VisionAPI._post")
def test_send_payment_plan_with_different_currency(
    mock_post,
    mock_acquire_token,
    vision_api_payment_plan_factory,
) -> None:
    mock_post.return_value = ({"status": "ok"}, 200)
    api = VisionAPI()
    pp = vision_api_payment_plan_factory(
        unicef_id="PP003",
        currency_code="EUR",
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
            "status": PaymentPlan.Status.IN_REVIEW,
            "headVendor": "Head Vendor Name",
            "creationDate": "20250301",
        },
    )


def test_vision_api_error_is_raised(vision_api_payment_plan_factory) -> None:
    with patch("hope.contrib.vision.api.VisionAPI._acquire_token"):
        with patch("hope.contrib.vision.api.VisionAPI._post") as mock_post:
            mock_post.side_effect = BaseAPI.APIError("boom")
            api = VisionAPI()
            pp = vision_api_payment_plan_factory()
            with pytest.raises(VisionAPIError):
                api.send_payment_plan(pp)
            pp.refresh_from_db(fields=["internal_data"])
            assert "vision" in pp.internal_data
            entry = pp.internal_data["vision"]["log"][0]
            assert entry["type"] == VisionLogEntryType.API_CALL.value
            assert datetime.fromisoformat(entry["timestamp"])
            assert entry["response"]["error"] == "boom"
            assert pp.vision_status == "SEND_FAILED"


def test_send_payment_plan_logs_4xx_error(vision_api_payment_plan_factory) -> None:
    with patch("hope.contrib.vision.api.VisionAPI._acquire_token"):
        with patch("hope.contrib.vision.api.VisionAPI._post") as mock_post:
            mock_post.side_effect = BaseAPI.APIError(
                'VisionAPI Invalid response: <Response [400]>, b\'{"error": "bad request"}\', https://test.example.com/ps/ezcash/PaymentPlan'
            )
            api = VisionAPI()
            pp = vision_api_payment_plan_factory()
            with pytest.raises(VisionAPIError):
                api.send_payment_plan(pp)
            pp.refresh_from_db(fields=["internal_data"])
            assert "vision" in pp.internal_data
            assert len(pp.internal_data["vision"]["log"]) == 1
            entry = pp.internal_data["vision"]["log"][0]
            assert entry["type"] == VisionLogEntryType.API_CALL.value
            assert entry["payload"]["payplanSno"] == "PP001"
            assert "400" in entry["response"]["error"]
            assert pp.vision_status == "SEND_FAILED"


def test_send_payment_plan_persists_missing_credentials_failure(
    settings,
    vision_api_payment_plan_factory,
    django_assert_num_queries,
) -> None:
    settings.VISION_CLIENT_ID = ""
    api = VisionAPI()
    payment_plan = vision_api_payment_plan_factory()

    with django_assert_num_queries(4), pytest.raises(VisionAPIMissingCredentialsError):
        api.send_payment_plan(payment_plan)

    payment_plan.refresh_from_db(fields=["internal_data"])
    assert payment_plan.vision_status == VisionStatus.SEND_FAILED.value
    assert payment_plan.vision_data["log"][0]["response"] == {"error": "Vision API credentials are not configured"}


@patch("hope.contrib.vision.api.VisionAPI._acquire_token")
@patch("hope.contrib.vision.api.VisionAPI._post")
def test_send_payment_plan_logs_payload_and_response(
    mock_post,
    mock_acquire_token,
    vision_api_payment_plan_factory,
) -> None:
    mock_post.return_value = ({"status": "ok", "messageId": "msg-42"}, 200)
    api = VisionAPI()
    pp = vision_api_payment_plan_factory(unicef_id="PP042")
    VisionService.set_status(pp, VisionStatus.WAITING_FOR_CALLBACK)
    pp.save(update_fields=["internal_data"])
    result = api.send_payment_plan(pp)
    pp.refresh_from_db(fields=["internal_data"])
    assert result == {"status": "ok", "messageId": "msg-42"}
    assert "vision" in pp.internal_data
    assert pp.internal_data["vision"]["sent"] is True
    assert set(pp.internal_data["vision"]) == {"log", "sent", "status"}
    assert pp.internal_data["vision"]["status"] == "WAITING_FOR_CALLBACK"
    assert len(pp.internal_data["vision"]["log"]) == 1
    entry = pp.internal_data["vision"]["log"][0]
    assert entry["type"] == VisionLogEntryType.API_CALL.value
    assert datetime.fromisoformat(entry["timestamp"])
    assert entry["payload"]["payplanSno"] == "PP042"
    assert entry["response"]["messageId"] == "msg-42"


@patch("hope.contrib.vision.api.VisionAPI._acquire_token")
@patch("hope.contrib.vision.api.VisionAPI._post")
def test_notify_payment_plan_status_uses_payment_plan_endpoint_without_changing_workflow_state(
    mock_post,
    mock_acquire_token,
    vision_api_payment_plan_factory,
    django_assert_num_queries,
) -> None:
    mock_post.return_value = ({"status": "ok"}, 200)
    payment_plan = vision_api_payment_plan_factory(unicef_id="PP-STATUS")
    payment_plan.internal_data = {
        "vision": {
            "status": VisionStatus.NOT_SENT.value,
            "log": [],
        }
    }
    payment_plan.save(update_fields=["internal_data"])

    with django_assert_num_queries(4):
        response = VisionAPI().notify_payment_plan_status(payment_plan, "REJECTED")

    payment_plan.refresh_from_db(fields=["internal_data"])
    assert response == {"status": "ok"}
    payload = mock_post.call_args.args[1]
    assert mock_post.call_args.args[0] == "https://test.example.com/ps/ezcash/PaymentPlan"
    assert payload["payplanSno"] == "PP-STATUS"
    assert payload["status"] == "REJECTED"
    assert payment_plan.vision_status == VisionStatus.NOT_SENT.value
    assert payment_plan.vision_data["log"][0]["type"] == VisionLogEntryType.STATUS_NOTIFICATION.value


def test_notify_payment_plan_status_logs_missing_credentials_without_changing_workflow_state(
    settings,
    vision_api_payment_plan_factory,
    django_assert_num_queries,
) -> None:
    settings.VISION_CLIENT_ID = ""
    payment_plan = vision_api_payment_plan_factory()

    with django_assert_num_queries(4), pytest.raises(VisionAPIMissingCredentialsError):
        VisionAPI().notify_payment_plan_status(payment_plan, "ABORTED")

    payment_plan.refresh_from_db(fields=["internal_data"])
    assert payment_plan.vision_status == VisionStatus.NOT_SENT.value
    entry = payment_plan.vision_data["log"][0]
    assert entry["type"] == VisionLogEntryType.STATUS_NOTIFICATION.value
    assert entry["response"] == {"error": "Vision API credentials are not configured"}


@patch("hope.contrib.vision.api.VisionAPI._acquire_token")
@patch("hope.contrib.vision.api.VisionAPI._post")
def test_notify_payment_plan_status_logs_api_error(
    mock_post,
    mock_acquire_token,
    vision_api_payment_plan_factory,
    django_assert_num_queries,
) -> None:
    mock_post.side_effect = BaseAPI.APIError("status update failed")
    payment_plan = vision_api_payment_plan_factory()

    with django_assert_num_queries(4), pytest.raises(VisionAPIError, match="status update failed"):
        VisionAPI().notify_payment_plan_status(payment_plan, "REJECTED")

    payment_plan.refresh_from_db(fields=["internal_data"])
    assert payment_plan.vision_status == VisionStatus.NOT_SENT.value
    assert payment_plan.vision_data["log"][0]["response"] == {"error": "status update failed"}


@patch("hope.contrib.vision.api.VisionAPI._acquire_token")
@patch("hope.contrib.vision.api.VisionAPI._post")
def test_send_payment_plan_already_sent_raises_error(
    mock_post,
    mock_acquire_token,
    vision_api_payment_plan_factory,
) -> None:
    api = VisionAPI()
    pp = vision_api_payment_plan_factory(unicef_id="PP042")
    pp.internal_data = {"vision": {"sent": True}}
    with pytest.raises(VisionAPIError):
        api.send_payment_plan(pp)
    mock_acquire_token.assert_not_called()
    mock_post.assert_not_called()


def test_callback_view_gets_payment_plan_with_related_data(
    vision_api_payment_plan_factory,
    django_assert_num_queries,
) -> None:
    from hope.contrib.vision.views import PaymentPlanCallbackView

    payment_plan = vision_api_payment_plan_factory(unicef_id="PP-LOOKUP")

    with django_assert_num_queries(1):
        selected_payment_plan = PaymentPlanCallbackView._get_payment_plan("PP-LOOKUP")

    assert selected_payment_plan.pk == payment_plan.pk
    assert selected_payment_plan.business_area_id == payment_plan.business_area_id
    assert selected_payment_plan.created_by_id == payment_plan.created_by_id
    assert "business_area" in selected_payment_plan._state.fields_cache
    assert "created_by" in selected_payment_plan._state.fields_cache


@patch("hope.models.APILogEntry.objects.create")
@patch("hope.contrib.vision.views.PaymentPlanCallbackView._get_payment_plan")
def test_callback_view_missing_fc_returns_ko(mock_get, mock_log_entry) -> None:
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

    assert response.status_code == 400
    mock_get.assert_called_once_with("PP043")
    mock_pp.save.assert_called_once_with(update_fields=["internal_data"])
    assert response.data == {
        "status": "KO",
        "messageId": "AGoSIRjbhXM_6L58Q2zj3MevWx81",
        "payplanSno": "PP043",
        "message": "FC not found",
    }
    assert "vision" in mock_pp.internal_data
    entry = mock_pp.internal_data["vision"]["log"][0]
    assert entry["type"] == VisionLogEntryType.PUSH_NOTIFICATION.value
    assert datetime.fromisoformat(entry["timestamp"])
    assert entry["payload"]["payplanSno"] == "PP043"
    assert entry["response"]["status"] == "KO"
    assert entry["response"]["message"] == "FC not found"
    assert mock_pp.internal_data["vision"]["vision_id"] == "00000062"
    assert mock_pp.internal_data["vision"]["status"] == "FC_MISSING"


@patch("hope.models.APILogEntry.objects.create")
@patch("hope.contrib.vision.views.PaymentPlanCallbackView._get_payment_plan")
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
    with patch("hope.contrib.vision.views.VisionService.process_callback") as mock_process_callback:
        mock_process_callback.return_value = False
        response = view(request)

    assert response.status_code == 200
    assert response.data == {
        "status": "OK",
        "messageId": "msg-002",
        "payplanSno": "PP044",
    }
    mock_process_callback.assert_called_once_with(
        mock_pp,
        vision_payment_plan_id="00000063",
        vision_result="SUCCESS",
        fc_num="FC123",
    )
    mock_pp.save.assert_called_once_with(update_fields=["internal_data"])


@patch("hope.models.APILogEntry.objects.create")
@patch("hope.contrib.vision.views.PaymentPlanCallbackView._get_payment_plan")
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
    mock_get.assert_called_once_with("PP045")
    mock_pp.save.assert_called_once_with(update_fields=["internal_data"])
    entry = mock_pp.internal_data["vision"]["log"][0]
    assert entry["type"] == VisionLogEntryType.PUSH_NOTIFICATION.value
    assert entry["payload"]["payplanSno"] == "PP045"
    assert entry["response"]["status"] == "KO"
    assert mock_pp.internal_data["vision"]["status"] == "CALLBACK_FAILED"


@patch("hope.models.APILogEntry.objects.create")
@patch("hope.contrib.vision.views.PaymentPlanCallbackView._get_payment_plan")
def test_callback_view_missing_vision_id_preserves_released_state(mock_get, mock_log_entry) -> None:
    from rest_framework.test import APIRequestFactory, force_authenticate

    from hope.contrib.vision.views import PaymentPlanCallbackView

    mock_pp = _make_mock_payment_plan(unicef_id="PP045")
    mock_pp.internal_data = {"vision": {"status": "RELEASED"}}
    mock_pp.vision_status = "RELEASED"
    mock_get.return_value = mock_pp
    mock_user = MagicMock()
    mock_token = MagicMock()
    mock_token.grants = ["API_VISION_PP_CREATE"]
    request = APIRequestFactory().post(
        "/api/rest/systems/vision/payment-plan-callback/",
        {
            "messageId": "msg-released-duplicate",
            "payplanSno": "PP045",
            "status": "SUCCESS",
        },
        format="json",
    )
    force_authenticate(request, user=mock_user, token=mock_token)

    response = PaymentPlanCallbackView.as_view()(request)

    assert response.status_code == 400
    assert mock_pp.internal_data["vision"]["status"] == "RELEASED"
    assert len(mock_pp.internal_data["vision"]["log"]) == 1
    mock_pp.save.assert_called_once_with(update_fields=["internal_data"])


@patch("hope.models.APILogEntry.objects.create")
@patch("hope.contrib.vision.views.PaymentPlanCallbackView._get_payment_plan")
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
@patch("hope.contrib.vision.views.PaymentPlanCallbackView._get_payment_plan")
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
    mock_get.assert_called_once_with("PP043")
    mock_pp.save.assert_called_once_with(update_fields=["internal_data"])
    assert response.data == {
        "status": "OK",
        "messageId": "msg-001",
        "payplanSno": "PP043",
    }
    assert "vision" in mock_pp.internal_data
    entry = mock_pp.internal_data["vision"]["log"][0]
    assert entry["type"] == VisionLogEntryType.PUSH_NOTIFICATION.value
    assert entry["payload"]["payplanSno"] == "PP043"
    assert entry["response"]["status"] == "OK"
    assert mock_pp.internal_data["vision"]["vision_id"] == "00000062"
    assert mock_pp.internal_data["vision"]["status"] == "CALLBACK_FAILED"
    assert mock_pp.internal_data["vision"]["error_code"] == "VISION_STATUS_FAILED"
    assert "fc_num" not in mock_pp.internal_data["vision"]


@patch("hope.models.APILogEntry.objects.create")
@patch("hope.contrib.vision.views.PaymentPlanCallbackView._get_payment_plan")
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
@patch("hope.contrib.vision.views.PaymentPlanCallbackView._get_payment_plan")
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
