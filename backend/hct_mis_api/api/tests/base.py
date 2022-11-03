from rest_framework.test import APITestCase

from hct_mis_api.api.models import APIToken, Grant
from hct_mis_api.api.tests.factories import APITokenFactory
from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    RoleFactory,
    UserFactory,
)


class HOPEApiTestCase(APITestCase):
    databases = ["default", "registration_datahub"]
    user_permissions = [
        Grant.API_RDI_CREATE,
        Grant.API_RDI_UPLOAD,
    ]
    token = None

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        user = UserFactory()
        cls.business_area = BusinessAreaFactory(name="Afghanistan")
        cls.role = RoleFactory(subsystem="API", name="c", permissions=[p.name for p in cls.user_permissions])
        user.user_roles.create(role=cls.role, business_area=cls.business_area)

        cls.token: APIToken = APITokenFactory(
            user=user,
            grants=[c.name for c in cls.user_permissions],
        )
        cls.token.valid_for.set([cls.business_area])

    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
