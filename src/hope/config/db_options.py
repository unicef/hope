from hope.config.env import env
from hope.config.process_role import ProcessRole

ZOMBIE_TIMEOUT_MS = 4 * 60 * 60 * 1000  # 4h
WEB_TIMEOUT_MS = 230 * 1000  # 230s
CLIENT_DISCONNECT_CHECK_MS = env("DB_CLIENT_CONNECTION_CHECK_INTERVAL_MS")

TIMEOUT_BY_ROLE = {
    ProcessRole.WEB: WEB_TIMEOUT_MS,
    ProcessRole.RUNSERVER: WEB_TIMEOUT_MS,
}


CHECK_INTERVAL_BY_ROLE = {
    ProcessRole.WEB: CLIENT_DISCONNECT_CHECK_MS,
    ProcessRole.RUNSERVER: CLIENT_DISCONNECT_CHECK_MS,
    ProcessRole.CELERY: CLIENT_DISCONNECT_CHECK_MS,
}


def postgres_options(role: ProcessRole, *, read_only: bool = False) -> str:
    timeout_ms = TIMEOUT_BY_ROLE.get(role, ZOMBIE_TIMEOUT_MS)

    parameters: dict[str, object] = {
        "application_name": f"{role}-ro" if read_only else role,
        "statement_timeout": timeout_ms,
        "idle_in_transaction_session_timeout": timeout_ms,
        "client_connection_check_interval": CHECK_INTERVAL_BY_ROLE.get(role, 0),
    }
    if read_only:
        parameters["default_transaction_read_only"] = "on"

    return " ".join(f"-c {name}={value}" for name, value in parameters.items())
