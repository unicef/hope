from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from hct_mis_api.api.models import APIToken, Grant
from hct_mis_api.api.tests.factories import APITokenFactory
from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    RoleFactory,
    UserFactory,
)
from hct_mis_api.apps.core.models import BusinessArea


class HOPEApiTestCase(APITestCase):
    databases = {"default", "registration_datahub"}
    user_permissions = [
        Grant.API_RDI_CREATE,
        Grant.API_RDI_UPLOAD,
    ]
    token: APIToken
    business_area: BusinessArea

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        user = UserFactory()
        cls.business_area = BusinessAreaFactory(name="Afghanistan")
        cls.role = RoleFactory(
            subsystem="API",
            name="c",
            permissions=[p.name for p in cls.user_permissions],
        )
        user.user_roles.create(role=cls.role, business_area=cls.business_area)

        cls.token = APITokenFactory(
            user=user,
            grants=[c.name for c in cls.user_permissions],
        )
        cls.token.valid_for.set([cls.business_area])

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)


class ConstanceSettingsAPITest(APITestCase):
    databases = {"default", "registration_datahub"}
    user_permissions = [
        Grant.API_READ_ONLY,
    ]
    token: APIToken

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory()  # Create a user
        cls.token: APIToken = APITokenFactory(
            user=cls.user,
            grants=[c.name for c in cls.user_permissions],
        )

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_constance_settings_api(self) -> None:
        url = reverse("api:constance-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("BANNER_MESSAGE", response.data)
        self.assertEqual(response.data["BANNER_MESSAGE"], "Default banner message")
