from unittest.mock import MagicMock, patch

from hope.apps.utils.sentry import sentry_tags


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
