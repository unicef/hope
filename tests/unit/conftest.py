import logging
from pathlib import Path
import sys
from time import sleep
from typing import Any

from _pytest.config import Config
from _pytest.config.argparsing import Parser
from constance import config as constance_config
from constance.backends.memory import MemoryBackend
from django.conf import settings
from django.core.cache import cache, caches
from django_elasticsearch_dsl.test import is_es_online
from elasticsearch import Elasticsearch
from elasticsearch.dsl import connections
import pytest

from extras.test_utils.factories import CurrencyFactory, FlagStateFactory
from extras.test_utils.fixtures import *  # noqa: F403, F401
from hope.apps.household.services.index_management import create_program_indexes, delete_program_indexes
from hope.models.currency import Currency


@pytest.fixture
def enable_is_root() -> None:
    FlagStateFactory.create(name="IS_ROOT", condition="boolean", value="True", required=False)


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


@pytest.fixture
def currency_pln(db: Any) -> Currency:
    return CurrencyFactory(code="PLN", name="Polish Zloty")


@pytest.fixture
def currency_usd(db: Any) -> Currency:
    return CurrencyFactory(code="USD", name="United States Dollar")


@pytest.fixture
def currency_usdc(db: Any) -> Currency:
    return CurrencyFactory(code="USDC", name="USD Coin", is_crypto=True)


@pytest.fixture
def currency_syp_deprecated(db: Any) -> Currency:
    return CurrencyFactory(code="SYP", name="Syrian Pound (old)", vision_code="SYP", active=False)


@pytest.fixture
def currency_syp(currency_syp_deprecated: Currency) -> Currency:
    """The active SYP after the redenomination, always beside the deprecated row sharing its ``code``.

    ``Meta.ordering`` sorts the deprecated row first, so a lookup relying on ``.first()`` picks it.
    ``SYP01`` is its ``vision_code``, which inputs accept as a transitional alias. Do not combine
    with ``all_currencies``: it seeds the pre-redenomination rows, which collide with these.
    """
    return CurrencyFactory(code="SYP", name="Syrian Pound", vision_code="SYP01", active=True)


@pytest.fixture
def currency_retired(db: Any) -> Currency:
    """A currency withdrawn without a successor: its code has only an inactive row."""
    return CurrencyFactory(code="VEF", name="Venezuelan Bolivar", vision_code="VEF", active=False)


@pytest.fixture
def all_currencies(db: Any) -> None:
    from hope.apps.core.currencies import CURRENCIES

    Currency.objects.bulk_create(
        [
            Currency(code=code, name=name, is_crypto=is_crypto, active=True, vision_code=code)
            for code, name, is_crypto in CURRENCIES
        ],
        ignore_conflicts=True,
    )


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


def pytest_configure(config: Config) -> None:
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
        },
        "sessions": {
            "BACKEND": "hope.apps.core.memcache.LocMemCache",
            "LOCATION": "sessions",
        },
    }
    settings.ELASTICSEARCH_DSL_AUTOSYNC = False
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
    logging.disable(logging.CRITICAL)

    constance_config._setup()
    object.__setattr__(constance_config._wrapped, "_backend", MemoryBackend())


def pytest_unconfigure(config: Config) -> None:
    import sys  # noqa

    del sys._called_from_pytest


@pytest.fixture
def mock_elasticsearch(mocker: Any) -> Any:
    """Mock ES functions for tests that don't need actual ES.

    Use this fixture instead of django_elasticsearch_setup for tests that
    call ES functions but don't verify search/deduplication results.
    """
    # Mock ES utility functions
    mocker.patch("hope.apps.utils.elasticsearch_utils.rebuild_search_index")
    mocker.patch("hope.apps.utils.elasticsearch_utils.populate_index")
    mocker.patch("hope.apps.utils.elasticsearch_utils.remove_elasticsearch_documents_by_matching_ids")
    mocker.patch("hope.apps.utils.elasticsearch_utils.ensure_index_ready")
    # Mock per-program index management
    mocker.patch("hope.apps.household.services.index_management.create_program_indexes")
    mocker.patch("hope.apps.household.services.index_management.delete_program_indexes")
    mocker.patch("hope.apps.household.services.index_management.populate_program_indexes")
    mocker.patch("hope.apps.household.services.index_management.rebuild_program_indexes")
    mocker.patch("hope.apps.household.services.index_management.ensure_program_indexes")
    # Also patch at usage locations (for modules that use `from X import Y`)
    mocker.patch(
        "hope.apps.grievance.services.needs_adjudication_ticket_services.remove_elasticsearch_documents_by_matching_ids"
    )
    # Mock deduplication that uses ES
    mocker.patch("hope.apps.registration_data.tasks.deduplicate.DeduplicateTask.deduplicate_pending_individuals")
    mocker.patch(
        "hope.apps.registration_data.tasks.deduplicate.DeduplicateTask.deduplicate_individuals_against_population"
    )
    mocker.patch(
        "hope.apps.registration_data.tasks.deduplicate.DeduplicateTask.deduplicate_individuals_from_other_source"
    )
    mocker.patch("hope.apps.grievance.services.data_change.utils.update_es")


@pytest.fixture
def django_elasticsearch_setup(request: pytest.FixtureRequest) -> None:
    xdist_suffix = getattr(request.config, "workerinput", {}).get("workerid")
    suffix = "_test"
    if xdist_suffix:
        suffix += f"_{xdist_suffix}"

    _setup_test_elasticsearch(suffix=suffix)
    yield
    _delete_program_es_indexes()


@pytest.fixture
def create_program_es_index():
    """Create and tear down per-program ES indexes for a test."""
    created = []

    def _create(program):
        create_program_indexes(str(program.id))
        created.append(str(program.id))

    yield _create

    for program_id in created:
        delete_program_indexes(program_id)


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


def _delete_program_es_indexes() -> None:
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    test_prefix = settings.ELASTICSEARCH_INDEX_PREFIX
    if test_prefix:
        all_indexes = list(es.indices.get_alias(index=f"{test_prefix}*", ignore_unavailable=True).keys())
        for index in all_indexes:
            es.indices.delete(index=index, ignore=[404, 400])


@pytest.fixture(autouse=True)
def clear_cache_before_each_test() -> None:
    cache.clear()
    caches["sessions"].clear()


@pytest.fixture(autouse=True)
def disable_activity_log(request, monkeypatch):
    if request.node.get_closest_marker("enable_activity_log"):
        yield  # do nothing, let real logging work
        return

    from hope.models import LogEntry

    class DummyPrograms:
        def add(self, *args, **kwargs):
            pass

    class DummyLog:
        def __init__(self):
            self.programs = DummyPrograms()

        def save(self, *args, **kwargs):
            pass

    monkeypatch.setattr(LogEntry.objects, "create", lambda *a, **kw: DummyLog())
    yield
