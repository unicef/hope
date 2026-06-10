from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory
from django.views.generic import View
import pytest

from extras.test_utils.factories import BusinessAreaFactory, UserFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.permissions_views_mixins import UploadFilePermissionMixin, ViewPermissionsMixinBase
from hope.models import BusinessArea, User

pytestmark = pytest.mark.django_db


class _AllowedProbeView(ViewPermissionsMixinBase, View):
    login_url = "/login"

    def has_permissions(self) -> bool:
        return True

    def get(self, request: HttpRequest) -> HttpResponse:
        return HttpResponse("ok")


class _DeniedProbeView(_AllowedProbeView):
    def has_permissions(self) -> bool:
        return False


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def upload_mixin_with_request(user: User) -> UploadFilePermissionMixin:
    request = RequestFactory().get("/upload-file/")
    request.user = user
    mixin = UploadFilePermissionMixin()
    mixin.request = request
    return mixin


def test_has_permissions_raises_not_implemented_error() -> None:
    mixin = ViewPermissionsMixinBase()

    with pytest.raises(NotImplementedError):
        mixin.has_permissions()


def test_dispatch_redirects_unauthenticated_user_to_login() -> None:
    request = RequestFactory().get("/some-page")
    request.user = AnonymousUser()

    response = _AllowedProbeView.as_view()(request)

    assert response.status_code == 302
    assert response.url == "/login?next=/some-page"


def test_dispatch_raises_permission_denied_for_user_without_permissions(user: User) -> None:
    request = RequestFactory().get("/some-page")
    request.user = user

    with pytest.raises(PermissionDenied):
        _DeniedProbeView.as_view()(request)


def test_dispatch_returns_view_response_for_user_with_permissions(user: User) -> None:
    request = RequestFactory().get("/some-page")
    request.user = user

    response = _AllowedProbeView.as_view()(request)

    assert response.status_code == 200
    assert response.content == b"ok"


def test_upload_mixin_has_permissions_with_upload_storage_file_permission(
    upload_mixin_with_request: UploadFilePermissionMixin,
    create_user_role_with_permissions: Any,
    user: User,
    business_area: BusinessArea,
    django_assert_num_queries: Any,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.UPLOAD_STORAGE_FILE], business_area, whole_business_area_access=True
    )

    with django_assert_num_queries(1):
        has_permissions = upload_mixin_with_request.has_permissions()

    assert has_permissions is True


def test_upload_mixin_has_no_permissions_with_unrelated_permission(
    upload_mixin_with_request: UploadFilePermissionMixin,
    create_user_role_with_permissions: Any,
    user: User,
    business_area: BusinessArea,
) -> None:
    create_user_role_with_permissions(
        user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], business_area, whole_business_area_access=True
    )

    assert upload_mixin_with_request.has_permissions() is False


def test_upload_mixin_has_no_permissions_without_role_assignments(
    upload_mixin_with_request: UploadFilePermissionMixin,
) -> None:
    assert upload_mixin_with_request.has_permissions() is False
