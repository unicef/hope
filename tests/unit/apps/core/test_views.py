from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, RequestFactory
from django.urls import reverse
import pytest

from extras.test_utils.factories import BusinessAreaFactory, UserFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.views import homepage, trigger_error
from hope.models import BusinessArea, StorageFile, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def user_with_upload_permission(
    user: User, business_area: BusinessArea, create_user_role_with_permissions: Any
) -> User:
    create_user_role_with_permissions(
        user, [Permissions.UPLOAD_STORAGE_FILE], business_area, whole_business_area_access=True
    )
    return user


@pytest.fixture
def logged_in_client(client: Client, user_with_upload_permission: User) -> Client:
    client.force_login(user_with_upload_permission, "django.contrib.auth.backends.ModelBackend")
    return client


def test_homepage_returns_empty_200_response() -> None:
    request = RequestFactory().get("/_health")
    request.user = AnonymousUser()

    response = homepage(request)

    assert response.status_code == 200
    assert response.content == b""


def test_logout_view_logs_user_out_and_redirects_to_login(client: Client, user: User) -> None:
    client.force_login(user, "django.contrib.auth.backends.ModelBackend")

    response = client.get(reverse("logout"))

    assert response.status_code == 302
    assert response.url == "/login"
    assert "_auth_user_id" not in client.session


def test_trigger_error_raises_zero_division_error() -> None:
    request = RequestFactory().get("/sentry-debug/")

    with pytest.raises(ZeroDivisionError):
        trigger_error(request)


def test_upload_file_get_redirects_anonymous_user_to_login(client: Client) -> None:
    response = client.get(reverse("upload-file"))

    assert response.status_code == 302
    assert response.url == f"/login?next={reverse('upload-file')}"


def test_upload_file_get_returns_403_without_permission(client: Client, user: User) -> None:
    client.force_login(user, "django.contrib.auth.backends.ModelBackend")

    response = client.get(reverse("upload-file"))

    assert response.status_code == 403


def test_upload_file_get_renders_upload_form(logged_in_client: Client, django_assert_num_queries: Any) -> None:
    with django_assert_num_queries(8):
        response = logged_in_client.get(reverse("upload-file"))

    assert response.status_code == 200
    assert "core/upload_file.html" in [t.name for t in response.templates]
    assert "form" in response.context


def test_upload_file_post_creates_storage_file_and_redirects(
    logged_in_client: Client,
    user_with_upload_permission: User,
    business_area: BusinessArea,
    django_assert_num_queries: Any,
) -> None:
    data = {
        "business_area": business_area.pk,
        "file": SimpleUploadedFile("upload.txt", b"file content"),
    }

    with django_assert_num_queries(9):
        response = logged_in_client.post(reverse("upload-file"), data)

    assert response.status_code == 302
    assert response.url == reverse("upload-file")
    storage_file = StorageFile.objects.get()
    assert storage_file.created_by == user_with_upload_permission
    assert storage_file.business_area == business_area
    messages = [str(message) for message in get_messages(response.wsgi_request)]
    assert messages == [f"File {storage_file.file.name} has been successfully uploaded."]


def test_upload_file_post_with_too_large_file_shows_error(
    logged_in_client: Client, business_area: BusinessArea, settings: Any
) -> None:
    settings.MAX_STORAGE_FILE_SIZE = 0
    data = {
        "business_area": business_area.pk,
        "file": SimpleUploadedFile("upload.txt", b"file content"),
    }

    response = logged_in_client.post(reverse("upload-file"), data)

    assert response.status_code == 200
    assert StorageFile.objects.count() == 0
    messages = [str(message) for message in get_messages(response.wsgi_request)]
    assert messages == ["File too large. Size should not exceed 0 MiB."]
