import logging
from pathlib import Path
import re
import sys
from time import sleep
from typing import Any

from _pytest.config import Config
from _pytest.config.argparsing import Parser
from django.conf import settings
from django.core.cache import cache
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.test import is_es_online
from elasticsearch_dsl import connections
import pytest

from extras.test_utils.fixtures import *  # noqa: F403, F401


@pytest.fixture(autouse=True)
def create_unicef_partner(db: Any) -> None:
    from hope.models import Partner

    unicef, _ = Partner.objects.get_or_create(name="UNICEF")
    return Partner.objects.get_or_create(name=settings.UNICEF_HQ_PARTNER, parent=unicef)


@pytest.fixture(scope="class", autouse=True)
def create_unicef_partner_session(django_db_setup: Any, django_db_blocker: Any) -> None:
    with django_db_blocker.unblock():
        from hope.models import Partner

        unicef, _ = Partner.objects.get_or_create(name="UNICEF")
        Partner.objects.get_or_create(name=settings.UNICEF_HQ_PARTNER, parent=unicef)


@pytest.fixture(autouse=True)
def create_role_with_all_permissions(db: Any) -> None:
    from hope.models import Role

    return Role.objects.get_or_create(name="Role with all permissions")


@pytest.fixture(scope="class", autouse=True)
def create_role_with_all_permissions_session(django_db_setup: Any, django_db_blocker: Any) -> None:
    with django_db_blocker.unblock():
        from hope.models import Role

        Role.objects.get_or_create(name="Role with all permissions")


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--localhost",
        action="store_true",
        default=False,
        help="Tests running locally, no ES",
    )


@pytest.fixture(autouse=True)
def clear_default_cache() -> None:
    from django.core.cache import cache  # noqa

    cache.clear()


def _patch_sync_apps_for_no_migrations() -> None:
    """Patch Django's sync_apps to not skip apps without models_module.

    This is needed for --no-migrations to work correctly when models are
    defined in hope.models instead of hope.apps.*.models.

    Django's sync_apps() skips apps where models_module is None, but our
    models are in hope.models with app_label pointing to hope.apps.*.
    """
    from django.core.management.commands import migrate

    original_sync_apps = migrate.Command.sync_apps

    def patched_sync_apps(self, connection, app_labels):
        # Import hope.models to register all models before sync
        from django.apps import apps as django_apps

        import hope.models

        # Set models_module for hope.* apps that don't have their own models.py
        for app_config in django_apps.get_app_configs():
            if app_config.models_module is None and "hope" in app_config.name:
                app_config.models_module = hope.models

        return original_sync_apps(self, connection, app_labels)

    migrate.Command.sync_apps = patched_sync_apps


def pytest_configure(config: Config) -> None:
    # Patch sync_apps before tests run
    _patch_sync_apps_for_no_migrations()

    pytest.localhost = bool(config.getoption("--localhost"))
    here = Path(__file__).parent
    utils = here.parent / "extras"
    sys.path.append(str(utils))

    sys._called_from_pytest = True
    from django.conf import settings  # noqa

    settings.DATABASES["read_only"]["TEST"] = {"MIRROR": "default"}
    settings.DATABASES["default"]["CONN_MAX_AGE"] = 0
    settings.CACHES = {
        "default": {
            "BACKEND": "hope.apps.core.memcache.LocMemCache",
            "TIMEOUT": 1800,
        }
    }
    settings.ELASTICSEARCH_DSL_AUTOSYNC = False
    logging.disable(logging.CRITICAL)


def pytest_unconfigure(config: Config) -> None:
    import sys  # noqa

    del sys._called_from_pytest


disabled_locally_test = pytest.mark.skip(
    reason="Elasticsearch error - to investigate",
)


@pytest.fixture
def mock_elasticsearch(mocker: Any) -> None:
    """Mock ES functions for tests that don't need actual ES.

    Use this fixture instead of django_elasticsearch_setup for tests that
    call ES functions but don't verify search/deduplication results.
    """
    # Mock ES utility functions
    mocker.patch("hope.apps.utils.elasticsearch_utils.rebuild_search_index")
    mocker.patch("hope.apps.utils.elasticsearch_utils.populate_index")
    mocker.patch("hope.apps.utils.elasticsearch_utils.remove_elasticsearch_documents_by_matching_ids")
    mocker.patch("hope.apps.utils.elasticsearch_utils.ensure_index_ready")
    # Also patch at usage locations (for modules that use `from X import Y`)
    mocker.patch(
        "hope.apps.grievance.services.needs_adjudication_ticket_services.remove_elasticsearch_documents_by_matching_ids"
    )
    # Mock deduplication that uses ES
    mocker.patch("hope.apps.registration_datahub.tasks.deduplicate.DeduplicateTask.deduplicate_pending_individuals")
    mocker.patch(
        "hope.apps.registration_datahub.tasks.deduplicate.DeduplicateTask.deduplicate_individuals_against_population"
    )
    mocker.patch(
        "hope.apps.registration_datahub.tasks.deduplicate.DeduplicateTask.deduplicate_individuals_from_other_source"
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
    from django.db import connections  # noqa
    from django.db.migrations.loader import MigrationLoader  # noqa
    from django.db.models.signals import post_migrate, pre_migrate  # noqa

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
            from django.db.migrations.operations.special import RunSQL  # noqa

            if isinstance(operation, RunSQL):
                sql_statements = operation.sql if isinstance(operation.sql, (list, tuple)) else [operation.sql]
                for stmt in sql_statements:
                    all_sqls.append(stmt)  # noqa

    def pre_migration_custom_sql(
        sender: Any,
        app_config: Any,
        verbosity: Any,
        interactive: Any,
        using: Any,
        **kwargs: Any,
    ) -> None:
        if not settings.TESTS_ROOT:
            return
        filename = settings.TESTS_ROOT + "/../../development_tools/db/premigrations.sql"
        with open(filename, "r") as file:
            pre_sql = file.read()
        conn = connections[using]
        conn.cursor().execute(pre_sql)

    def post_migration_custom_sql(
        sender: Any,
        app_config: Any,
        verbosity: Any,
        interactive: Any,
        using: Any,
        **kwargs: Any,
    ) -> None:
        from django.db.utils import ProgrammingError

        app_label = app_config.label
        if app_label not in apps:
            return
        apps.remove(app_label)
        if apps:
            return
        conn = connections[using]
        for stmt in all_sqls:
            try:
                conn.cursor().execute(stmt)
            except ProgrammingError as e:
                # Ignore "already exists" errors for indexes/tables when using existing test DB
                if "already exists" in str(e):
                    continue
                raise

    pre_migrate.connect(
        pre_migration_custom_sql,
        dispatch_uid="tests.pre_migrationc_custom_sql",
        weak=False,
    )
    post_migrate.connect(
        post_migration_custom_sql,
        dispatch_uid="tests.post_migration_custom_sql",
        weak=False,
    )


@pytest.fixture(autouse=True)
def clear_cache_before_each_test() -> None:
    cache.clear()


# @pytest.fixture(autouse=True)
# def ensure_contenttypes_and_permissions(db):
#     ContentType.objects.clear_cache()
#     for app_config in apps.get_app_configs():
#         create_permissions(app_config, verbosity=0)


# @pytest.fixture(scope="session", autouse=True)
# def prevent_contenttype_flush(django_db_setup, django_db_blocker):
#     with django_db_blocker.unblock():
#         call_command("migrate", interactive=False, run_syncdb=True)
