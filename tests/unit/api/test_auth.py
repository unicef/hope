from unittest.mock import MagicMock, Mock

from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    BusinessAreaFactory,
    RoleFactory,
    UserFactory,
)
from extras.test_utils.factories.api import APITokenFactory
from hope.api.auth import HOPEAuthentication, HOPEPermission
from hope.models import APIToken, BusinessArea
from hope.models.grant import Grant

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan")


@pytest.fixture
def token(business_area: BusinessArea) -> APIToken:
    user = UserFactory()
    role = RoleFactory(name="test_role")
    user.role_assignments.create(role=role, business_area=business_area)
    token = APITokenFactory(
        user=user,
        grants=[Grant.API_RDI_CREATE.name, Grant.API_RDI_UPLOAD.name],
    )
    token.valid_for.set([business_area])
    return token


def test_permission_granted(token: APIToken, business_area: BusinessArea) -> None:
    permission = HOPEPermission()
    request = Mock(auth=token)
    view = Mock(selected_business_area=business_area, permission=Grant.API_RDI_UPLOAD)

    assert permission.has_permission(request, view)


def test_permission_denied_missing_grant(token: APIToken, business_area: BusinessArea) -> None:
    permission = HOPEPermission()
    request = Mock(auth=token)
    view = Mock(selected_business_area=business_area, permission=Grant.API_READ_ONLY)

    assert not permission.has_permission(request, view)


def test_authentication_success(token: APIToken) -> None:
    auth = HOPEAuthentication()
    request = MagicMock(META={"HTTP_AUTHORIZATION": f"Token {token.key}"})

    user, returned_token = auth.authenticate(request)

    assert user == token.user
    assert returned_token == token


def test_authentication_invalid_token() -> None:
    auth = HOPEAuthentication()
    request = MagicMock(META={"HTTP_AUTHORIZATION": "Token invalid_key"})

    with pytest.raises(AuthenticationFailed):
        auth.authenticate(request)


def test_no_auth_returns_401(business_area: BusinessArea) -> None:
    client = APIClient()
    url = reverse("api:rdi-upload", args=[business_area.slug])
    response = client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.fixture
def read_only_client(business_area: BusinessArea) -> APIClient:
    user = UserFactory()
    role = RoleFactory(name="test_role_no_grant")
    user.role_assignments.create(role=role, business_area=business_area)
    token = APITokenFactory(user=user, grants=[Grant.API_READ_ONLY.name])
    token.valid_for.set([business_area])
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


def test_missing_grant_returns_403(read_only_client: APIClient, business_area: BusinessArea) -> None:
    url = reverse("api:rdi-create", args=[business_area.slug])
    response = read_only_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You do not have permission to perform this action. API_RDI_CREATE"}
