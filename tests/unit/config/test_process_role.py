import pytest

from hope.config.process_role import ProcessRole, get_process_role


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        pytest.param(
            ["/usr/local/bin/gunicorn", "hope.wsgi", "-c", "/conf/gunicorn_config.py"], ProcessRole.WEB, id="web"
        ),
        pytest.param(
            ["/usr/local/bin/celery", "-A", "hope.apps.core.celery", "worker"], ProcessRole.CELERY, id="worker"
        ),
        pytest.param(["/usr/local/bin/celery", "-A", "hope.apps.core.celery", "beat"], ProcessRole.CELERY, id="beat"),
        pytest.param(["manage.py", "migrate", "--noinput"], ProcessRole.MIGRATE, id="migrate"),
        pytest.param(["./manage.py", "runserver", "0.0.0.0:8080"], ProcessRole.RUNSERVER, id="runserver"),
        pytest.param(["/usr/local/bin/django-admin", "shell"], ProcessRole.SHELL, id="shell"),
        pytest.param(["manage.py", "shell_plus"], ProcessRole.SHELL, id="shell-plus"),
        pytest.param(["/usr/local/bin/django-admin", "initdemo"], ProcessRole.MANAGE, id="other-command"),
        pytest.param(["manage.py"], ProcessRole.MANAGE, id="manage-without-command"),
        pytest.param(["pytest", "tests/unit"], ProcessRole.UNKNOWN, id="unrecognised"),
        pytest.param([], ProcessRole.UNKNOWN, id="embedded-interpreter-without-argv"),
    ],
)
def test_get_process_role_returns_expected_role(
    monkeypatch: pytest.MonkeyPatch, argv: list[str], expected: ProcessRole
) -> None:
    monkeypatch.setattr("sys.argv", argv)

    assert get_process_role() == expected


def test_process_role_renders_as_its_plain_value_in_the_connection_options() -> None:
    assert f"-c application_name={ProcessRole.WEB}" == "-c application_name=hope-web"
