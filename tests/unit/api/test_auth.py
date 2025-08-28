from unittest.mock import MagicMock, Mock

from django.test import TestCase
from django.urls import reverse
from extras.test_utils.factories.account import (
    BusinessAreaFactory,
    RoleFactory,
    UserFactory,
)
import pytest
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed

from hope.api.auth import HOPEAuthentication, HOPEPermission
from hope.api.models import APIToken, Grant
from unit.api.base import HOPEApiTestCase
from unit.api.factories import APITokenFactory


class HOPEPermissionTest(TestCase):
    def setUp(self) -> None:
        super().setUpTestData()
        user = UserFactory()
        self.business_area = BusinessAreaFactory(name="Afghanistan")
        self.role = RoleFactory(subsystem="API", name="c")
        user.role_assignments.create(role=self.role, business_area=self.business_area)

        self.token: APIToken = APITokenFactory(
            user=user,
            grants=[
                Grant.API_RDI_CREATE.name,
                Grant.API_RDI_UPLOAD.name,
                Grant.API_RDI_UPLOAD.name,
            ],
        )
        self.token.valid_for.set([self.business_area])

    def test_permissions(self) -> None:
        p = HOPEPermission()

        assert p.has_permission(
            Mock(auth=self.token),
            Mock(
                selected_business_area=self.business_area,
                permission=Grant.API_RDI_UPLOAD,
            ),
        )


class HOPEAuthenticationTest(HOPEApiTestCase):
    def test_auth_success(self) -> None:
        p = HOPEAuthentication()
        request = MagicMock(META={"HTTP_AUTHORIZATION": f"Token {self.token.key}"})
        p.authenticate(request)

    def test_auth_fails(self) -> None:
        p = HOPEAuthentication()
        request = MagicMock(META={"HTTP_AUTHORIZATION": "Token 123"})
        with pytest.raises(AuthenticationFailed):
            p.authenticate(request)


class ViewAuthView(HOPEApiTestCase):
    user_permissions = [Grant.API_RDI_UPLOAD]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

    def test_no_auth(self) -> None:
        self.client.logout()
        url = reverse("api:rdi-upload", args=[self.business_area.slug])
        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, str(response.json())

    def test_no_perm(self) -> None:
        url = reverse("api:rdi-create", args=[self.business_area.slug])
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN, str(response.json())
        data = response.json()
        assert data == {"detail": "You do not have permission to perform this action. API_RDI_CREATE"}
