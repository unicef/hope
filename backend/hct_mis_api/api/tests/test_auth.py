from unittest import TestCase
from unittest.mock import MagicMock, Mock

from rest_framework.exceptions import AuthenticationFailed

from hct_mis_api.api.auth import HOPEAuthentication, HOPEPermission
from hct_mis_api.api.tests.base import HOPEApiTestCase
from hct_mis_api.apps.account.export_users_xlsx import User
from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, RoleFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions


class HOPEPermissionTest(TestCase):
    def setUp(self):
        self.user: User = UserFactory()
        self.business_area = BusinessAreaFactory(name="Afghanistan")
        self.role = RoleFactory(subsystem="API", permissions=[Permissions.API_UPLOAD_RDI])
        self.user.user_roles.create(role=self.role, business_area=self.business_area)

    def test_permissions(self):
        p = HOPEPermission()

        assert p.has_permission(
            Mock(user=self.user), Mock(selected_business_area=self.business_area, permission=Permissions.API_UPLOAD_RDI)
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
