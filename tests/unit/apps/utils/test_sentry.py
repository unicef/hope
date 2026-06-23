import logging
from unittest.mock import MagicMock, patch

from hope.apps.utils.sentry import SentryFilter, sentry_tags, set_sentry_business_area_tag


@patch("hope.apps.utils.sentry.sentry_sdk")
def test_sentry_tags_sets_celery_scope_tags_and_preserves_return_value(
    mocked_sentry: MagicMock,
) -> None:
    scope = MagicMock()
    mocked_sentry.get_isolation_scope.return_value = scope

    @sentry_tags
    def my_task(value: int) -> int:
        return value * 2

    result = my_task(21)

    assert result == 42
    assert my_task.__name__ == "my_task"
    mocked_sentry.get_isolation_scope.assert_called_once_with()
    scope.set_tag.assert_any_call("celery", True)
    scope.set_tag.assert_any_call("celery_task", "my_task")


@patch("hope.apps.utils.sentry.set_tag")
def test_set_sentry_business_area_tag_uses_given_name(mocked_set_tag: MagicMock) -> None:
    set_sentry_business_area_tag("Afghanistan")

    mocked_set_tag.assert_called_once_with("business_area", "Afghanistan")


@patch("hope.apps.utils.sentry.set_tag")
def test_set_sentry_business_area_tag_defaults_to_no_ba(mocked_set_tag: MagicMock) -> None:
    set_sentry_business_area_tag()

    mocked_set_tag.assert_called_once_with("business_area", "NO_BA")


def test_filter_exception_returns_false_for_non_matching_type() -> None:
    exc = ValueError("test")

    assert SentryFilter.filter_exception((type(exc), exc, None), KeyError) is False


def test_filter_exception_returns_true_for_matching_type_without_message_filter() -> None:
    exc = ValueError("test")

    assert SentryFilter.filter_exception((type(exc), exc, None), ValueError) is True


def test_filter_exception_returns_false_when_message_not_in_exception() -> None:
    exc = ValueError("test")

    assert SentryFilter.filter_exception((type(exc), exc, None), ValueError, "absent") is False


def test_filter_exception_returns_true_when_message_in_exception() -> None:
    exc = ValueError("test happened")

    assert SentryFilter.filter_exception((type(exc), exc, None), ValueError, "test") is True


def test_filter_log_returns_false_when_logger_name_differs() -> None:
    record = logging.LogRecord("other.logger", logging.ERROR, "", 1, "test happened", None, None)

    assert SentryFilter.filter_log(record, "my.logger") is False


def test_filter_log_returns_false_when_severity_differs() -> None:
    record = logging.LogRecord("my.logger", logging.ERROR, "", 1, "test happened", None, None)

    assert SentryFilter.filter_log(record, "my.logger", severity="WARNING") is False


def test_filter_log_returns_false_when_message_not_in_record() -> None:
    record = logging.LogRecord("my.logger", logging.ERROR, "", 1, "test happened", None, None)

    assert SentryFilter.filter_log(record, "my.logger", msg_to_filter="absent") is False


def test_filter_log_returns_false_when_exc_text_present() -> None:
    record = logging.LogRecord("my.logger", logging.ERROR, "", 1, "test happened", None, None)

    assert SentryFilter.filter_log(record, "my.logger", exc_text="traceback") is False


def test_filter_log_returns_false_when_exc_text_empty() -> None:
    record = logging.LogRecord("my.logger", logging.ERROR, "", 1, "test happened", None, None)
    record.exc_text = "stored traceback"

    assert SentryFilter.filter_log(record, "my.logger", exc_text="") is False


def test_before_send_returns_none_for_ignorable_transaction() -> None:
    sentry_filter = SentryFilter()
    sentry_filter.IGNORABLE_URLS = {"/health"}

    assert sentry_filter.before_send({"transaction": "/health"}, {}) is None


def test_before_send_returns_event_for_non_ignorable_transaction() -> None:
    sentry_filter = SentryFilter()
    sentry_filter.IGNORABLE_URLS = {"/health"}
    event = {"transaction": "/api/rest/"}

    assert sentry_filter.before_send(event, {}) is event


def test_before_send_returns_event_when_no_transaction() -> None:
    sentry_filter = SentryFilter()
    event: dict = {}

    assert sentry_filter.before_send(event, {}) is event
