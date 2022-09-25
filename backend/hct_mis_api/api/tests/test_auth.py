from unittest.mock import MagicMock, Mock

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed

from hct_mis_api.api.auth import HOPEAuthentication, HOPEPermission
from hct_mis_api.api.models import APIToken, Grant
from hct_mis_api.api.tests.base import HOPEApiTestCase
from hct_mis_api.api.tests.factories import APITokenFactory
from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    RoleFactory,
    UserFactory,
)


class HOPEPermissionTest(TestCase):
    def setUp(self):
        super().setUpTestData()
        user = UserFactory()
        self.business_area = BusinessAreaFactory(name="Afghanistan")
        self.role = RoleFactory(subsystem="API", name="c")
        user.user_roles.create(role=self.role, business_area=self.business_area)

        self.token: APIToken = APITokenFactory(
            user=user,
            grants=[
                Grant.API_CREATE_RDI.name,
                Grant.API_UPLOAD_RDI.name,
                Grant.API_UPLOAD_RDI.name,
            ],
        )
        self.token.valid_for.set([self.business_area])

    def test_permissions(self):
        p = HOPEPermission()

        assert p.has_permission(
            Mock(auth=self.token),
            Mock(selected_business_area=self.business_area, permission=Grant.API_UPLOAD_RDI),
        )


class HOPEAuthenticationTest(HOPEApiTestCase):
    def test_auth_success(self):
        p = HOPEAuthentication()
        request = MagicMock(META={"HTTP_AUTHORIZATION": f"Token {self.token.key}"})
        p.authenticate(request)

    def test_auth_fails(self):
        p = HOPEAuthentication()
        request = MagicMock(META={"HTTP_AUTHORIZATION": "Token 123"})
        with self.assertRaises(AuthenticationFailed):
            p.authenticate(request)


class ViewAuthView(HOPEApiTestCase):
    user_permissions = [Grant.API_UPLOAD_RDI]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_no_auth(self):
        self.client.logout()
        url = reverse("api:rdi-upload", args=[self.business_area.slug])
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, str(response.json()))

    def test_no_perm(self):
        url = reverse("api:rdi-create", args=[self.business_area.slug])
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, str(response.json()))
        data = response.json()
        self.assertDictEqual(data, {"detail": "You do not have permission to perform this action. API_CREATE_RDI"})
