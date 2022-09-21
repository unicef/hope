from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    RoleFactory,
    UserFactory,
)
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase


class HOPEApiTestCase(APITestCase):
    databases = ["default", "registration_datahub"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.business_area = BusinessAreaFactory(name="Afghanistan")
        cls.user: User = UserFactory()
        cls.role = RoleFactory(subsystem="API", name="c", permissions=[Permissions.API_CREATE_RDI])
        cls.user.user_roles.create(role=cls.role, business_area=cls.business_area)

    def setUp(self):
        self.client.login(username=self.user.username, password="password")
