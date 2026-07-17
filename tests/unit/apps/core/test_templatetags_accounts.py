from typing import Any

from django.test import RequestFactory
import pytest

from extras.test_utils.factories import RoleAssignmentFactory, StorageFileFactory, UserFactory
from hope.apps.core.templatetags.accounts import _is_root, get_admin_link, get_related
from hope.models import RoleAssignment, StorageFile, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def superuser() -> User:
    return UserFactory(is_superuser=True)


@pytest.fixture
def role_assignment(user: User) -> RoleAssignment:
    return RoleAssignmentFactory(user=user)


@pytest.fixture
def storage_file(user: User) -> StorageFile:
    return StorageFileFactory(created_by=user)


def test_get_related_uses_explicit_related_name_accessor(user: User, role_assignment: RoleAssignment) -> None:
    field = User._meta.get_field("role_assignments")

    info = get_related(user, field)

    assert info["to"] == "user"
    assert info["field_name"] == "role_assignments"
    assert str(info["related_name"]) == "role assignment"
    assert list(info["data"]) == [role_assignment]


def test_get_related_falls_back_to_default_set_accessor(user: User, storage_file: StorageFile) -> None:
    field = User._meta.get_field("storagefile")

    info = get_related(user, field)

    assert info["to"] == "user"
    assert info["field_name"] == "storagefile"
    assert str(info["related_name"]) == "storage file"
    assert list(info["data"]) == [storage_file]


def test_get_admin_link_returns_admin_change_url(user: User) -> None:
    assert get_admin_link(user) == f"/api/unicorn/account/user/{user.pk}/change/"


def test_is_root_true_for_superuser_with_valid_token(superuser: User, settings: Any) -> None:
    settings.ROOT_TOKEN = "root-token"
    request = RequestFactory().get("/", headers={"x-root-token": "root-token"})
    request.user = superuser

    assert _is_root(request) is True


def test_is_root_false_for_superuser_with_wrong_token(superuser: User, settings: Any) -> None:
    settings.ROOT_TOKEN = "root-token"
    request = RequestFactory().get("/", headers={"x-root-token": "wrong-token"})
    request.user = superuser

    assert _is_root(request) is False


def test_is_root_false_for_non_superuser_with_valid_token(user: User, settings: Any) -> None:
    settings.ROOT_TOKEN = "root-token"
    request = RequestFactory().get("/", headers={"x-root-token": "root-token"})
    request.user = user

    assert _is_root(request) is False
