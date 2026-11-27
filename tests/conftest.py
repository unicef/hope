import os
from typing import Any

from _pytest.config import Config
from django.apps import apps
from django.core.management import call_command
import freezegun
import pytest

COMMON_SETTINGS = {
    "DEBUG": True,
    "ALLOWED_HOSTS": [
        "localhost",
        "127.0.0.1",
        "10.0.2.2",
        os.getenv("DOMAIN", ""),
    ],
    "CELERY_TASK_ALWAYS_EAGER": True,
    "ELASTICSEARCH_INDEX_PREFIX": "test_",
    "EMAIL_BACKEND": "django.core.mail.backends.console.EmailBackend",
    "CATCH_ALL_EMAIL": [],
    "DEFAULT_EMAIL": "testemail@email.com",
    "EXCHANGE_RATE_CACHE_EXPIRY": 0,
    "USE_DUMMY_EXCHANGE_RATES": True,
    "SOCIAL_AUTH_REDIRECT_IS_HTTPS": True,
    "CSRF_COOKIE_SECURE": False,
    "CSRF_COOKIE_HTTPONLY": False,
    "SESSION_COOKIE_SECURE": False,
    "SESSION_COOKIE_HTTPONLY": True,
    "SECURE_HSTS_SECONDS": False,
    "SECURE_CONTENT_TYPE_NOSNIFF": True,
    "SECURE_REFERRER_POLICY": "same-origin",
    "CACHE_ENABLED": False,
    "TESTS_ROOT": os.getenv("TESTS_ROOT"),
    "CONSTANCE_BACKEND": "constance.backends.memory.MemoryBackend",
}


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        path = str(item.fspath)
        if "/e2e/" in path:
            item.add_marker(pytest.mark.selenium)
        elif "/unit/" in path:
            item.add_marker(pytest.mark.unit)


def pytest_configure(config: Config) -> None:
    from django.conf import settings  # noqa

    freezegun.configure(extend_ignore_list=["psycopg"])

    for setting_name, value in COMMON_SETTINGS.items():
        setattr(settings, setting_name, value)

    settings.LOGGING["loggers"].update(
        {
            "": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
            "registration_data.tasks.deduplicate": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": True,
            },
            "sanction_list.tasks.check_against_sanction_list_pre_merge": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": True,
            },
            "elasticsearch": {
                "handlers": ["default"],
                "level": "CRITICAL",
                "propagate": True,
            },
            "elasticsearch-dsl-django": {
                "handlers": ["default"],
                "level": "CRITICAL",
                "propagate": True,
            },
            "hope.apps.registration_data.tasks.deduplicate": {
                "handlers": ["default"],
                "level": "CRITICAL",
                "propagate": True,
            },
            "hope.apps.core.tasks.upload_new_template_and_update_flex_fields": {
                "handlers": ["default"],
                "level": "CRITICAL",
                "propagate": True,
            },
        }
    )


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup: None, django_db_blocker: Any) -> None:
    """Build the test database with ``migrate``, then empty every table once.

    A transactional test (and every e2e test) flushes the database when it ends, and rows inserted
    by migrations do not come back after that. Removing them up front gives every test the same
    starting point whatever ran before it on the worker: tests create their reference rows
    (currencies, payee types, beneficiary groups, ...) in fixtures and never rely on migration data.

    The flush recreates content types and permissions through ``post_migrate``, which skips apps
    without a models module. The models of a few ``hope`` apps live only in ``hope.models``, so
    those apps get that module assigned first. Otherwise their content types would be created
    lazily inside a test, rolled back with it and left in the ``ContentType`` cache with a dead
    primary key.
    """
    import hope.models

    for app_config in apps.get_app_configs():
        if app_config.models_module is None and app_config.name.startswith("hope."):
            app_config.models_module = hope.models
    with django_db_blocker.unblock():
        call_command("flush", verbosity=0, interactive=False)
