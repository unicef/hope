from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
import pytest
import requests

from extras.test_utils.factories.core import BusinessAreaFactory
from hope.apps.core.services.rapid_pro.api import RapidProAPI, TokenNotProvidedError


@pytest.fixture
def rapid_pro_api():
    """RapidProAPI with mocked __init__ to avoid DB access."""
    with patch.object(RapidProAPI, "__init__", lambda self, *args: None):
        api = RapidProAPI.__new__(RapidProAPI)
        api._client = MagicMock()
        api.url = "https://rapidpro.test"
        api._timeout = 30
        return api


def test_broadcast_message_batches_phone_numbers_into_chunks(rapid_pro_api):
    """Verifies that phone numbers are split into batches of MAX_URNS_PER_REQUEST."""
    rapid_pro_api.MAX_URNS_PER_REQUEST = 2
    phone_numbers = ["111", "222", "333", "444", "555"]

    with patch.object(rapid_pro_api, "_handle_post_request") as mock_post:
        rapid_pro_api.broadcast_message(phone_numbers, "Hello")

    assert mock_post.call_count == 3  # 5 numbers / 2 per batch = 3 batches


def test_broadcast_message_sends_single_batch_when_count_below_limit(rapid_pro_api):
    """No batching needed when phone numbers count is below limit."""
    rapid_pro_api.MAX_URNS_PER_REQUEST = 100
    phone_numbers = ["111", "222", "333"]

    with patch.object(rapid_pro_api, "_handle_post_request") as mock_post:
        rapid_pro_api.broadcast_message(phone_numbers, "Hello")

    assert mock_post.call_count == 1


def test_broadcast_message_skips_request_when_phone_list_empty(rapid_pro_api):
    """Empty phone list should not trigger any HTTP requests."""
    with patch.object(rapid_pro_api, "_handle_post_request") as mock_post:
        rapid_pro_api.broadcast_message([], "Hello")

    mock_post.assert_not_called()


def test_broadcast_message_sends_single_batch_when_count_equals_limit(rapid_pro_api):
    """When phone count equals batch size, only one batch is sent."""
    rapid_pro_api.MAX_URNS_PER_REQUEST = 3
    phone_numbers = ["111", "222", "333"]

    with patch.object(rapid_pro_api, "_handle_post_request") as mock_post:
        rapid_pro_api.broadcast_message(phone_numbers, "Hello")

    assert mock_post.call_count == 1


@patch("hope.apps.core.services.rapid_pro.api.config")
def test_broadcast_message_batch_formats_urns_with_tel_prefix(mock_config, rapid_pro_api):
    """Verifies URN format: {provider}:{phone_number}."""
    mock_config.RAPID_PRO_PROVIDER = "tel"

    with patch.object(rapid_pro_api, "_handle_post_request") as mock_post:
        rapid_pro_api._broadcast_message_batch(["111222333", "444555666"], "Test message")

    mock_post.assert_called_once_with(
        RapidProAPI.BROADCAST_START_ENDPOINT,
        {
            "urns": ["tel:111222333", "tel:444555666"],
            "text": "Test message",
        },
    )


@patch("hope.apps.core.services.rapid_pro.api.config")
def test_broadcast_message_batch_formats_urns_with_telegram_prefix(mock_config, rapid_pro_api):
    """Verifies URN format works with different providers (e.g., telegram)."""
    mock_config.RAPID_PRO_PROVIDER = "telegram"

    with patch.object(rapid_pro_api, "_handle_post_request") as mock_post:
        rapid_pro_api._broadcast_message_batch(["123456789"], "Hello Telegram")

    call_args = mock_post.call_args[0][1]
    assert call_args["urns"] == ["telegram:123456789"]
    assert call_args["text"] == "Hello Telegram"


@patch("hope.apps.core.services.rapid_pro.api.config")
def test_start_flow_raises_validation_error_on_urns_error(mock_config, rapid_pro_api):
    mock_config.RAPID_PRO_PROVIDER = "tel"
    rapid_pro_api.MAX_URNS_PER_REQUEST = 100

    http_error = requests.exceptions.HTTPError()
    http_error.response = MagicMock(status_code=400)
    http_error.response.json.return_value = {"urns": {"0": "invalid"}}

    with patch.object(rapid_pro_api, "_handle_post_request", side_effect=http_error):
        with patch.object(rapid_pro_api, "_parse_json_urns_error", return_value={"phone_numbers": ["111 - incorrect"]}):
            _, error = rapid_pro_api.start_flow("flow-uuid", ["111"])
            assert isinstance(error, ValidationError)


@patch("hope.apps.core.services.rapid_pro.api.config")
def test_start_flow_returns_responses_and_no_error_on_success(mock_config, rapid_pro_api):
    mock_config.RAPID_PRO_PROVIDER = "tel"
    rapid_pro_api.MAX_URNS_PER_REQUEST = 100

    with patch.object(rapid_pro_api, "_handle_post_request", return_value={"uuid": "start-1"}) as mock_post:
        flows, error = rapid_pro_api.start_flow("flow-uuid", ["111", "222"])

    assert error is None
    assert len(flows) == 1
    assert flows[0].response == {"uuid": "start-1"}
    assert flows[0].urns == ["tel:111", "tel:222"]
    mock_post.assert_called_once()


@patch("hope.apps.core.services.rapid_pro.api.config")
def test_start_flow_returns_http_error_when_not_a_urns_error(mock_config, rapid_pro_api):
    mock_config.RAPID_PRO_PROVIDER = "tel"
    rapid_pro_api.MAX_URNS_PER_REQUEST = 100
    http_error = requests.exceptions.HTTPError()
    http_error.response = MagicMock(status_code=500)

    with patch.object(rapid_pro_api, "_handle_post_request", side_effect=http_error):
        with patch.object(rapid_pro_api, "_parse_json_urns_error", return_value=None):
            flows, error = rapid_pro_api.start_flow("flow-uuid", ["111"])

    assert flows == []
    assert error is http_error


@patch("hope.apps.core.services.rapid_pro.api.config")
def test_broadcast_message_batch_raises_validation_error_on_urns_error(mock_config, rapid_pro_api):
    mock_config.RAPID_PRO_PROVIDER = "tel"

    http_error = requests.exceptions.HTTPError()
    http_error.response = MagicMock(status_code=400)
    http_error.response.json.return_value = {"urns": {"0": "invalid"}}

    with patch.object(rapid_pro_api, "_handle_post_request", side_effect=http_error):
        with patch.object(rapid_pro_api, "_parse_json_urns_error", return_value={"phone_numbers": ["111 - incorrect"]}):
            with pytest.raises(ValidationError):
                rapid_pro_api._broadcast_message_batch(["111"], "Hello")


@patch("hope.apps.core.services.rapid_pro.api.config")
def test_broadcast_message_batch_reraises_when_no_urns_errors(mock_config, rapid_pro_api):
    mock_config.RAPID_PRO_PROVIDER = "tel"
    http_error = requests.exceptions.HTTPError()
    http_error.response = MagicMock(status_code=500)

    with patch.object(rapid_pro_api, "_handle_post_request", side_effect=http_error):
        with patch.object(rapid_pro_api, "_parse_json_urns_error", return_value=None):
            with pytest.raises(requests.exceptions.HTTPError):
                rapid_pro_api._broadcast_message_batch(["111"], "Hello")


@pytest.mark.django_db
def test_init_token_sets_authorization_header_and_host():
    business_area = BusinessAreaFactory(
        rapid_pro_host="https://host.example",
        rapid_pro_payment_verification_token="secret-token",
    )
    api = RapidProAPI.__new__(RapidProAPI)
    api._client = requests.session()

    api._init_token(business_area.slug, RapidProAPI.MODE_VERIFICATION)

    assert api.url == "https://host.example"
    assert api._client.headers["Authorization"] == "Token secret-token"


@pytest.mark.django_db
def test_init_token_raises_when_token_missing():
    business_area = BusinessAreaFactory(rapid_pro_payment_verification_token="")
    api = RapidProAPI.__new__(RapidProAPI)
    api._client = requests.session()

    with pytest.raises(TokenNotProvidedError):
        api._init_token(business_area.slug, RapidProAPI.MODE_VERIFICATION)


def test_handle_get_request_absolute_url_returns_json(rapid_pro_api):
    response = MagicMock()
    response.json.return_value = {"ok": 1}
    rapid_pro_api._client.get.return_value = response

    result = rapid_pro_api._handle_get_request("https://abs/x", is_absolute_url=True)

    assert result == {"ok": 1}
    rapid_pro_api._client.get.assert_called_once_with("https://abs/x", timeout=30)


def test_handle_get_request_relative_url_prefixes_base(rapid_pro_api):
    response = MagicMock()
    response.json.return_value = {"results": []}
    rapid_pro_api._client.get.return_value = response

    rapid_pro_api._handle_get_request("/flows.json")

    rapid_pro_api._client.get.assert_called_once_with("https://rapidpro.test/api/v2/flows.json", timeout=30)


def test_handle_get_request_raises_on_http_error(rapid_pro_api):
    response = MagicMock()
    response.raise_for_status.side_effect = requests.exceptions.HTTPError("err")
    rapid_pro_api._client.get.return_value = response

    with pytest.raises(requests.exceptions.HTTPError):
        rapid_pro_api._handle_get_request("/flows.json")


def test_get_flows_returns_results(rapid_pro_api):
    with patch.object(rapid_pro_api, "_handle_get_request", return_value={"results": [{"name": "f"}]}):
        assert rapid_pro_api.get_flows() == [{"name": "f"}]


def test_get_flow_runs_follows_pagination(rapid_pro_api):
    pages = [
        {"results": [{"id": 1}], "next": "https://rapidpro.test/api/v2/runs.json?cursor=2"},
        {"results": [{"id": 2}], "next": None},
    ]
    with patch.object(rapid_pro_api, "_handle_get_request", side_effect=pages):
        assert rapid_pro_api.get_flow_runs() == [{"id": 1}, {"id": 2}]


def test_map_returns_none_fields_when_no_values(rapid_pro_api):
    run = {"contact": {"urn": "tel:111"}, "values": None}

    assert rapid_pro_api._map_to_internal_structure(run) == {
        "phone_number": "111",
        "received": None,
        "received_amount": None,
    }


def test_map_parses_received_and_amount(rapid_pro_api):
    run = {
        "contact": {"urn": "tel:222"},
        "values": {
            "cash_received_text": {"category": "yes"},
            "cash_received_amount": {"value": "100.50"},
        },
    }

    result = rapid_pro_api._map_to_internal_structure(run)

    assert result["received"] is True
    assert result["received_amount"] == Decimal("100.50")


def test_map_skips_missing_variables(rapid_pro_api):
    run = {"contact": {"urn": "tel:333"}, "values": {"unrelated": {}}}

    result = rapid_pro_api._map_to_internal_structure(run)

    assert result["received"] is None
    assert result["received_amount"] is None


def test_map_invalid_amount_defaults_to_zero(rapid_pro_api):
    run = {"contact": {"urn": "tel:444"}, "values": {"cash_received_amount": {"value": "not-a-number"}}}

    result = rapid_pro_api._map_to_internal_structure(run)

    assert result["received_amount"] == Decimal(0)


def test_get_mapped_flow_runs_filters_by_start_uuid(rapid_pro_api):
    runs = [
        {"start": {"uuid": "A"}, "contact": {"urn": "tel:1"}, "values": None},
        {"start": {"uuid": "B"}, "contact": {"urn": "tel:2"}, "values": None},
        {"start": None, "contact": {"urn": "tel:3"}, "values": None},
    ]
    with patch.object(rapid_pro_api, "get_flow_runs", return_value=runs):
        result = rapid_pro_api.get_mapped_flow_runs(["A"])

    assert [r["phone_number"] for r in result] == ["1"]


def test_test_connection_start_flow_success(rapid_pro_api):
    with patch.object(rapid_pro_api, "get_flows", return_value=[{"name": "f1", "uuid": "u1"}]):
        with patch.object(rapid_pro_api, "start_flow", return_value=(["resp"], None)) as mock_start:
            error, response = rapid_pro_api.test_connection_start_flow("f1", "111")

    assert error is None
    assert response == ["resp"]
    mock_start.assert_called_once_with("u1", ["111"])


def test_test_connection_start_flow_flow_not_found(rapid_pro_api):
    with patch.object(rapid_pro_api, "get_flows", return_value=[{"name": "other", "uuid": "x"}]):
        error, response = rapid_pro_api.test_connection_start_flow("missing", "111")

    assert "no flow with name 'missing'" in error
    assert response is None


def test_test_connection_start_flow_handles_http_error(rapid_pro_api):
    with patch.object(rapid_pro_api, "get_flows", side_effect=requests.exceptions.HTTPError("err")):
        error, response = rapid_pro_api.test_connection_start_flow("f", "111")

    assert error == "err"
    assert response is None
