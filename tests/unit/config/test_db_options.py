import pytest

from hope.config import db_options
from hope.config.process_role import ProcessRole


@pytest.mark.parametrize(
    "role",
    [
        pytest.param(ProcessRole.WEB, id="web"),
        pytest.param(ProcessRole.RUNSERVER, id="runserver"),
    ],
)
def test_postgres_options_uses_the_web_timeout_for_request_serving_roles(role: ProcessRole) -> None:
    options = db_options.postgres_options(role)

    assert f"-c statement_timeout={db_options.WEB_TIMEOUT_MS}" in options
    assert f"-c idle_in_transaction_session_timeout={db_options.WEB_TIMEOUT_MS}" in options


@pytest.mark.parametrize(
    "role",
    [
        pytest.param(ProcessRole.CELERY, id="celery"),
        pytest.param(ProcessRole.MIGRATE, id="migrate"),
        pytest.param(ProcessRole.SHELL, id="shell"),
        pytest.param(ProcessRole.MANAGE, id="manage"),
        pytest.param(ProcessRole.UNKNOWN, id="unknown"),
    ],
)
def test_postgres_options_uses_the_zombie_timeout_for_non_request_roles(role: ProcessRole) -> None:
    options = db_options.postgres_options(role)

    assert f"-c statement_timeout={db_options.ZOMBIE_TIMEOUT_MS}" in options
    assert f"-c idle_in_transaction_session_timeout={db_options.ZOMBIE_TIMEOUT_MS}" in options


def test_postgres_options_uses_the_role_as_application_name() -> None:
    options = db_options.postgres_options(ProcessRole.CELERY)

    assert "-c application_name=hope-celery" in options


def test_postgres_options_marks_the_application_name_of_a_read_only_connection() -> None:
    options = db_options.postgres_options(ProcessRole.WEB, read_only=True)

    assert "-c application_name=hope-web-ro" in options


def test_postgres_options_makes_transactions_read_only_when_read_only() -> None:
    options = db_options.postgres_options(ProcessRole.WEB, read_only=True)

    assert "-c default_transaction_read_only=on" in options


def test_postgres_options_leaves_transactions_writable_by_default() -> None:
    options = db_options.postgres_options(ProcessRole.WEB)

    assert "default_transaction_read_only" not in options


def test_postgres_options_renders_every_parameter_as_a_libpq_flag() -> None:
    options = db_options.postgres_options(ProcessRole.MIGRATE)

    assert options == (
        f"-c application_name=hope-migrate "
        f"-c statement_timeout={db_options.ZOMBIE_TIMEOUT_MS} "
        f"-c idle_in_transaction_session_timeout={db_options.ZOMBIE_TIMEOUT_MS} "
        f"-c client_connection_check_interval=0"
    )


@pytest.mark.parametrize(
    "role",
    [
        pytest.param(ProcessRole.WEB, id="web"),
        pytest.param(ProcessRole.RUNSERVER, id="runserver"),
        pytest.param(ProcessRole.CELERY, id="celery"),
    ],
)
def test_postgres_options_uses_the_client_connection_check_interval_for_long_lived_roles(role: ProcessRole) -> None:
    options = db_options.postgres_options(role)

    assert f"-c client_connection_check_interval={db_options.CLIENT_DISCONNECT_CHECK_MS}" in options


def test_postgres_options_disables_the_client_connection_check_for_roles_without_one() -> None:
    options = db_options.postgres_options(ProcessRole.MIGRATE)

    assert "-c client_connection_check_interval=0" in options
