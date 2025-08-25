import contextlib
from typing import Iterator

from django.core.cache import cache
from django.urls import reverse
from extras.test_utils.factories.account import (
    BusinessAreaFactory,
    RoleFactory,
    UserFactory,
)
from rest_framework import status
from rest_framework.test import APITestCase
from unit.api.factories import APITokenFactory

from hope.api.models import APIToken, Grant
from models.core import BusinessArea


@contextlib.contextmanager
def token_grant_permission(token: APIToken, grant: Grant) -> Iterator:
    old = token.grants
    token.grants += [grant.name]
    token.save()
    yield
    token.grants = old
    token.save()


class HOPEApiTestCase(APITestCase):
    databases = {"default"}
    user_permissions = [
        Grant.API_RDI_CREATE,
        Grant.API_RDI_UPLOAD,
    ]
    token: APIToken
    business_area: BusinessArea

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory()
        cls.business_area = BusinessAreaFactory(name="Afghanistan")
        cls.role = RoleFactory(
            subsystem="API",
            name="c",
            permissions=[p.name for p in cls.user_permissions],
        )
        cls.user.role_assignments.create(role=cls.role, business_area=cls.business_area)

        cls.token = APITokenFactory(
            user=cls.user,
            grants=[c.name for c in cls.user_permissions],
        )
        cls.token.valid_for.set([cls.business_area])

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def tearDown(self) -> None:
        """
        Clears all cache keys after each test. This ensures no cached data interferes with subsequent tests.
        """
        cache.clear()
        super().tearDown()


class ConstanceSettingsAPITest(APITestCase):
    databases = {"default"}
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

        assert response.status_code == status.HTTP_200_OK

        assert "BANNER_MESSAGE" in response.data
        assert response.data["BANNER_MESSAGE"] == "Default banner message"
