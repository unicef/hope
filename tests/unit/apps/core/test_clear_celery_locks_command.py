from io import StringIO

from django.core.cache import cache
from django.core.management import call_command
import pytest

from hope.apps.core.management.commands.clear_celery_locks import LOCK_KEY_PREFIXES
from hope.apps.payment.utils import generate_cache_key


@pytest.fixture
def lock_keys() -> list[str]:
    keys = [f"{prefix}1" for prefix in LOCK_KEY_PREFIXES] + [
        generate_cache_key({"task_name": "prepare_payment_plan_async_task", "payment_plan_id": "1"}),
    ]
    for key in keys:
        cache.set(key, True)
    yield keys
    cache.clear()


@pytest.fixture
def other_key() -> str:
    cache.set("count_afghanistan_HouseholdNodeConnection_1", 5)
    yield "count_afghanistan_HouseholdNodeConnection_1"
    cache.clear()


def test_removes_every_lock_key(lock_keys: list[str]) -> None:
    out = StringIO()

    call_command("clear_celery_locks", stdout=out)

    assert [key for key in lock_keys if cache.get(key) is not None] == []
    assert out.getvalue().strip() == f"Removed {len(lock_keys)} celery task locks"


def test_leaves_other_cache_keys(lock_keys: list[str], other_key: str) -> None:
    call_command("clear_celery_locks")

    assert cache.get(other_key) == 5
