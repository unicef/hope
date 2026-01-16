from unittest.mock import MagicMock, patch

import pytest

from hope.apps.core.services.rapid_pro.api import RapidProAPI


@pytest.fixture
def rapid_pro_api():
    """RapidProAPI with mocked __init__ to avoid DB access."""
    with patch.object(RapidProAPI, "__init__", lambda self, *args: None):
        api = RapidProAPI.__new__(RapidProAPI)
        api._client = MagicMock()
        api.url = "https://rapidpro.test"
        api._timeout = 30
        return api


class TestBroadcastMessage:
    def test_batches_phone_numbers_correctly(self, rapid_pro_api):
        """Verifies that phone numbers are split into batches of MAX_URNS_PER_REQUEST."""
        rapid_pro_api.MAX_URNS_PER_REQUEST = 2
        phone_numbers = ["111", "222", "333", "444", "555"]

        with patch.object(rapid_pro_api, "_handle_post_request") as mock_post:
            rapid_pro_api.broadcast_message(phone_numbers, "Hello")

        assert mock_post.call_count == 3  # 5 numbers / 2 per batch = 3 batches

    def test_single_batch_when_under_limit(self, rapid_pro_api):
        """No batching needed when phone numbers count is below limit."""
        rapid_pro_api.MAX_URNS_PER_REQUEST = 100
        phone_numbers = ["111", "222", "333"]

        with patch.object(rapid_pro_api, "_handle_post_request") as mock_post:
            rapid_pro_api.broadcast_message(phone_numbers, "Hello")

        assert mock_post.call_count == 1

    def test_empty_phone_numbers_no_request(self, rapid_pro_api):
        """Empty phone list should not trigger any HTTP requests."""
        with patch.object(rapid_pro_api, "_handle_post_request") as mock_post:
            rapid_pro_api.broadcast_message([], "Hello")

        mock_post.assert_not_called()

    def test_exact_batch_size(self, rapid_pro_api):
        """When phone count equals batch size, only one batch is sent."""
        rapid_pro_api.MAX_URNS_PER_REQUEST = 3
        phone_numbers = ["111", "222", "333"]

        with patch.object(rapid_pro_api, "_handle_post_request") as mock_post:
            rapid_pro_api.broadcast_message(phone_numbers, "Hello")

        assert mock_post.call_count == 1


class TestBroadcastMessageBatch:
    @patch("hope.apps.core.services.rapid_pro.api.config")
    def test_formats_urns_with_tel_provider(self, mock_config, rapid_pro_api):
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
    def test_formats_urns_with_telegram_provider(self, mock_config, rapid_pro_api):
        """Verifies URN format works with different providers (e.g., telegram)."""
        mock_config.RAPID_PRO_PROVIDER = "telegram"

        with patch.object(rapid_pro_api, "_handle_post_request") as mock_post:
            rapid_pro_api._broadcast_message_batch(["123456789"], "Hello Telegram")

        call_args = mock_post.call_args[0][1]
        assert call_args["urns"] == ["telegram:123456789"]
        assert call_args["text"] == "Hello Telegram"
