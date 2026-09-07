from collections.abc import Callable

from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models import Model
from django.test import Client
from django.urls import reverse
import pytest

from extras.test_utils.factories import UserFactory
from extras.test_utils.factories.aurora import RegistrationFactory
from extras.test_utils.factories.core import UniversalUpdateFactory
from extras.test_utils.factories.payment import (
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    WesternUnionPaymentPlanReportFactory,
)
from extras.test_utils.factories.periodic_data_update import PDUOnlineEditFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.core.celery_lock import lock_key
from hope.models import User

pytestmark = pytest.mark.django_db

FACTORIES: list[Callable[[], Model]] = [
    RegistrationDataImportFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    ProgramFactory,
    WesternUnionPaymentPlanReportFactory,
    PDUOnlineEditFactory,
    UniversalUpdateFactory,
    RegistrationFactory,
]


def button_url(obj: Model) -> str:
    return reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_remove_task_locks", args=[obj.pk])


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
def rdi() -> Model:
    return RegistrationDataImportFactory()


@pytest.fixture
def rdi_locks(rdi: Model) -> list[str]:
    keys = [lock_key("registration_xlsx_import", rdi.pk), lock_key("merge_registration_data_import", rdi.pk)]
    for key in [*keys, lock_key("registration_xlsx_import", "other-rdi")]:
        cache.lock(key).acquire()
    return keys


@pytest.mark.parametrize("factory", FACTORIES)
def test_remove_task_locks_button_forbidden_without_is_root(
    superuser_client: Client, factory: Callable[[], Model]
) -> None:
    response = superuser_client.get(button_url(factory()))

    assert response.status_code == 403


@pytest.mark.parametrize("factory", FACTORIES)
def test_remove_task_locks_button_renders_confirmation(root_client: Client, factory: Callable[[], Model]) -> None:
    obj = factory()
    cache.lock(lock_key("some_task", obj.pk)).acquire()

    response = root_client.get(button_url(obj))

    assert response.status_code == 200
    assert response.context["locks"] == [lock_key("some_task", obj.pk)]
    assert b"I confirm" in response.content


def test_remove_task_locks_button_rejects_wrong_confirmation(
    root_client: Client, rdi: Model, rdi_locks: list[str]
) -> None:
    response = root_client.post(button_url(rdi), {"confirmation": "confirm"})

    assert response.status_code == 200
    assert response.context["form"].errors["confirmation"] == ['You must type "I confirm" exactly.']
    assert len(cache.celery_lock_keys()) == 3
    assert not LogEntry.objects.exists()


def test_remove_task_locks_button_removes_only_object_locks_and_logs(
    root_client: Client, root_user: User, rdi: Model, rdi_locks: list[str], django_assert_num_queries
) -> None:
    root_client.get(button_url(rdi))

    with django_assert_num_queries(7):
        response = root_client.post(button_url(rdi), {"confirmation": "I confirm"})

    assert response.status_code == 302
    assert response.url == reverse("admin:registration_data_registrationdataimport_change", args=[rdi.pk])
    assert cache.celery_lock_keys() == [lock_key("registration_xlsx_import", "other-rdi")]
    entries = LogEntry.objects.order_by("object_repr")
    assert [(e.user, e.object_repr, e.action_flag, e.content_type, e.object_id, e.change_message) for e in entries] == [
        (root_user, key, DELETION, ContentType.objects.get_for_model(rdi), str(rdi.pk), "Celery lock removed")
        for key in sorted(rdi_locks)
    ]
