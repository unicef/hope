from django.contrib.admin.models import DELETION, LogEntry
from django.core.cache import cache
from django.test import Client
from django.urls import reverse
import pytest

from extras.test_utils.factories import UserFactory
from hope.apps.core.celery_lock import lock_key
from hope.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def root_user(enable_is_root: None) -> User:
    return UserFactory(is_staff=True, is_superuser=True)


@pytest.fixture
def root_client(client: Client, root_user: User) -> Client:
    client.force_login(root_user, "django.contrib.auth.backends.ModelBackend")
    return client


@pytest.fixture
def superuser_client(client: Client) -> Client:
    client.force_login(UserFactory(is_staff=True, is_superuser=True), "django.contrib.auth.backends.ModelBackend")
    return client


@pytest.fixture
def held_locks() -> list[str]:
    keys = [
        lock_key("payment_plan_full_rebuild", "pp-1"),
        lock_key("payment_plan_full_rebuild", "pp-2"),
        lock_key("dedup"),
    ]
    for key in keys:
        cache.lock(key).acquire()
    return keys


def test_celery_locks_view_forbidden_for_superuser_without_is_root(superuser_client: Client) -> None:
    response = superuser_client.get(reverse("admin:celery_locks"))

    assert response.status_code == 403


def test_celery_locks_view_lists_locks_grouped_by_task(root_client: Client, held_locks: list[str]) -> None:
    response = root_client.get(reverse("admin:celery_locks"))

    assert response.status_code == 200
    assert response.context["groups"] == {
        "dedup": [held_locks[2]],
        "payment_plan_full_rebuild": [held_locks[0], held_locks[1]],
    }


def test_celery_locks_view_shows_empty_state(root_client: Client) -> None:
    response = root_client.get(reverse("admin:celery_locks"))

    assert response.context["groups"] == {}
    assert b"No celery locks are currently held" in response.content


def test_celery_locks_view_rejects_wrong_confirmation(root_client: Client, held_locks: list[str]) -> None:
    response = root_client.post(reverse("admin:celery_locks"), {"key": held_locks[0], "confirmation": "yes"})

    assert response.status_code == 200
    assert response.context["form"].errors["confirmation"] == ['You must type "I confirm" exactly.']
    assert cache.celery_lock_keys() == sorted(held_locks)
    assert not LogEntry.objects.exists()


def test_celery_locks_view_removes_lock_and_logs_it(
    root_client: Client, root_user: User, held_locks: list[str], django_assert_num_queries
) -> None:
    root_client.get(reverse("admin:celery_locks"))

    with django_assert_num_queries(3):
        response = root_client.post(reverse("admin:celery_locks"), {"key": held_locks[0], "confirmation": "I confirm"})

    assert response.status_code == 302
    assert response.url == reverse("admin:celery_locks")
    assert cache.celery_lock_keys() == sorted(held_locks[1:])
    entry = LogEntry.objects.get()
    assert entry.user == root_user
    assert entry.object_repr == held_locks[0]
    assert entry.action_flag == DELETION
    assert entry.change_message == "Celery lock removed"
    assert (entry.content_type, entry.object_id) == (None, None)
