import contextlib
from typing import Iterator

from rest_framework.reverse import reverse

from hct_mis_api.api.models import APIToken, Grant
from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.core.models import BusinessArea
from tests.unit.api.base import HOPEApiTestCase


@contextlib.contextmanager
def token_grant_permission(token: APIToken, grant: Grant) -> Iterator:
    old = token.grants
    token.grants += [grant.name]
    token.save()
    yield
    token.grants = old
    token.save()


class APIBusinessAreaTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.list_url = reverse("api:business-area-list")

    def test_list_business_area(self) -> None:
        business_area1: BusinessArea = BusinessAreaFactory(
            slug="ukraine11",
            code="1234",
            name="Ukraine",
            long_name="the long name of Ukraine",
            active=True,
        )
        business_area2: BusinessArea = BusinessAreaFactory(
            slug="BA 2",
            code="5678",
            name="Bus Area 2",
            long_name="Business Area 2",
            active=False,
            parent=self.business_area,
        )
        self.business_area.refresh_from_db()
        business_area1.refresh_from_db()
        business_area2.refresh_from_db()
        response = self.client.get(self.list_url)
        assert response.status_code == 403
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 3)
        self.assertIn(
            {
                "id": str(self.business_area.id),
                "name": self.business_area.name,
                "code": self.business_area.code,
                "long_name": self.business_area.long_name,
                "slug": self.business_area.slug,
                "parent": None,
                "is_split": self.business_area.is_split,
                "active": self.business_area.active,
            },
            response.json()["results"],
        )
        self.assertIn(
            {
                "id": str(business_area1.id),
                "name": business_area1.name,
                "code": business_area1.code,
                "long_name": business_area1.long_name,
                "slug": business_area1.slug,
                "parent": None,
                "is_split": business_area1.is_split,
                "active": business_area1.active,
            },
            response.json()["results"],
        )
        self.assertIn(
            {
                "id": str(business_area2.id),
                "name": business_area2.name,
                "code": business_area2.code,
                "long_name": business_area2.long_name,
                "slug": business_area2.slug,
                "parent": str(business_area2.parent.id),
                "is_split": business_area2.is_split,
                "active": business_area2.active,
            },
            response.json()["results"],
        )
