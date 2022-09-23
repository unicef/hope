from rest_framework.test import APITestCase

from hct_mis_api.api.models import APIToken
from hct_mis_api.api.tests.factories import APITokenFactory
from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, RoleFactory


class HOPEApiTestCase(APITestCase):
    databases = ["default", "registration_datahub"]
    user_permissions = []

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.token: APIToken = APITokenFactory()
        cls.business_area = BusinessAreaFactory(name="Afghanistan")

        cls.role = RoleFactory(subsystem="API", name="c", permissions=[p.name for p in cls.user_permissions])
        cls.token.user.user_roles.create(role=cls.role, business_area=cls.business_area)

    def setUp(self):
        # self.client.login(username=self.user.username, password="password")
        self.client.force_authenticate(user=self.token.user)
