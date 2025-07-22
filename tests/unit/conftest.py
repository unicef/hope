import logging
import os
import re
import sys
from pathlib import Path
from time import sleep
from typing import Any

from django.conf import settings

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.test import is_es_online
from elasticsearch_dsl import connections
from extras.test_utils.fixtures import *  # noqa: ABS101, F403, F401


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--localhost",
        action="store_true",
        default=False,
        help="Tests running locally, no ES",
    )


@pytest.fixture(autouse=True)
def clear_default_cache() -> None:
    from django.core.cache import cache

    cache.clear()


def pytest_configure(config: Config) -> None:
    pytest.localhost = True if config.getoption("--localhost") else False
    here = Path(__file__).parent
    utils = here.parent / "extras"
    sys.path.append(str(utils))

    sys._called_from_pytest = True
    from django.conf import settings

    settings.DEBUG = True
    settings.ALLOWED_HOSTS = ["localhost", "127.0.0.1", "10.0.2.2", os.getenv("DOMAIN", "")]
    settings.CELERY_TASK_ALWAYS_EAGER = True

    settings.ELASTICSEARCH_INDEX_PREFIX = "test_"
    settings.EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    settings.CATCH_ALL_EMAIL = []
    settings.DEFAULT_EMAIL = "testemail@email.com"

    settings.EXCHANGE_RATE_CACHE_EXPIRY = 0
    settings.USE_DUMMY_EXCHANGE_RATES = True

    settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS = False
    settings.CSRF_COOKIE_SECURE = False
    settings.CSRF_COOKIE_HTTPONLY = False
    settings.SESSION_COOKIE_SECURE = False
    settings.SESSION_COOKIE_HTTPONLY = True
    settings.SECURE_HSTS_SECONDS = False
    settings.SECURE_CONTENT_TYPE_NOSNIFF = True
    settings.SECURE_REFERRER_POLICY = "same-origin"
    settings.DATABASES["read_only"]["TEST"] = {"MIRROR": "default"}
    settings.CACHE_ENABLED = False
    settings.TESTS_ROOT = os.getenv("TESTS_ROOT")
    settings.PROJECT_ROOT = os.getenv("PROJECT_ROOT")
    settings.CACHES = {
        "default": {
            "BACKEND": "hct_mis_api.apps.core.memcache.LocMemCache",
            "TIMEOUT": 1800,
        }
    }

    settings.LOGGING["loggers"].update(
        {
            "": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
            "registration_datahub.tasks.deduplicate": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": True,
            },
            "sanction_list.tasks.check_against_sanction_list_pre_merge": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": True,
            },
            "graphql": {"handlers": ["default"], "level": "CRITICAL", "propagate": True},
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
            "hct_mis_api.apps.registration_datahub.tasks.deduplicate": {
                "handlers": ["default"],
                "level": "CRITICAL",
                "propagate": True,
            },
            "hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields": {
                "handlers": ["default"],
                "level": "CRITICAL",
                "propagate": True,
            },
        }
    )

    logging.disable(logging.CRITICAL)


def pytest_unconfigure(config: Config) -> None:
    import sys

    del sys._called_from_pytest


disabled_locally_test = pytest.mark.skip(
    reason="Elasticsearch error - to investigate",
)


@pytest.fixture(scope="session")
def django_elasticsearch_setup(request: pytest.FixtureRequest) -> None:
    xdist_suffix = getattr(request.config, "workerinput", {}).get("workerid")
    suffix = "_test"
    if xdist_suffix:
        # Put a suffix like _gw0, _gw1 etc on xdist processes
        suffix += f"_{xdist_suffix}"

    _setup_test_elasticsearch(suffix=suffix)
    yield
    _teardown_test_elasticsearch(suffix=suffix)


def _wait_for_es(connection_alias: str) -> None:
    max_tries = 12
    sleep_time = 5

    for _ in range(max_tries):
        if is_es_online(connection_alias):
            break
        sleep(sleep_time)
    else:
        raise Exception("Elasticsearch not available")


def _setup_test_elasticsearch(suffix: str) -> None:
    worker_connection_postfix = f"default_worker_{suffix}"
    connections.create_connection(alias=worker_connection_postfix, **settings.ELASTICSEARCH_DSL["default"])

    _wait_for_es(connection_alias=worker_connection_postfix)

    # Update index names and connections
    for doc in registry.get_documents():
        doc._index._name += suffix
        # Use the worker-specific connection
        doc._index._using = worker_connection_postfix
        doc._index.delete(ignore=[404, 400])
        doc._index.create()


def _teardown_test_elasticsearch(suffix: str) -> None:
    pattern = re.compile(f"{suffix}$")

    for index in registry.get_indices():
        index.delete(ignore=[404, 400])
        index._name = pattern.sub("", index._name)

    for doc in registry.get_documents():
        doc._index._name = pattern.sub("", doc._index._name)


@pytest.fixture(scope="session", autouse=True)
def register_custom_sql_signal() -> None:
    from django.db import connections
    from django.db.migrations.loader import MigrationLoader
    from django.db.models.signals import post_migrate, pre_migrate

    orig = getattr(settings, "MIGRATION_MODULES", None)
    settings.MIGRATION_MODULES = {}

    loader = MigrationLoader(None, load=False)
    loader.load_disk()
    all_migrations = loader.disk_migrations
    if orig is not None:
        settings.MIGRATION_MODULES = orig
    apps = set()
    all_sqls = []
    for (app_label, _), migration in all_migrations.items():
        apps.add(app_label)

        for operation in migration.operations:
            from django.db.migrations.operations.special import RunSQL

            if isinstance(operation, RunSQL):
                sql_statements = operation.sql if isinstance(operation.sql, (list, tuple)) else [operation.sql]
                for stmt in sql_statements:
                    all_sqls.append(stmt)

    def pre_migration_custom_sql(
        sender: Any, app_config: Any, verbosity: Any, interactive: Any, using: Any, **kwargs: Any
    ) -> None:
        filename = settings.TESTS_ROOT + "/../../development_tools/db/premigrations.sql"
        with open(filename, "r") as file:
            pre_sql = file.read()
        conn = connections[using]
        conn.cursor().execute(pre_sql)

    def post_migration_custom_sql(
        sender: Any, app_config: Any, verbosity: Any, interactive: Any, using: Any, **kwargs: Any
    ) -> None:
        app_label = app_config.label
        if app_label not in apps:
            return
        apps.remove(app_label)
        if apps:
            return
        conn = connections[using]
        for stmt in all_sqls:
            conn.cursor().execute(stmt)

    pre_migrate.connect(pre_migration_custom_sql, dispatch_uid="tests.pre_migrationc_custom_sql", weak=False)
    post_migrate.connect(post_migration_custom_sql, dispatch_uid="tests.post_migration_custom_sql", weak=False)
