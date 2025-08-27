from extras.test_utils.factories.account import BusinessAreaFactory
from rest_framework import status
from rest_framework.reverse import reverse

from hope.api.models import Grant
from unit.api.base import HOPEApiTestCase, token_grant_permission


class APIBusinessAreaTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.list_url = reverse("api:core:business-areas-list")

    def test_list_business_area(self) -> None:
        business_area1 = BusinessAreaFactory(
            slug="ukraine11",
            code="1234",
            name="Ukraine",
            long_name="the long name of Ukraine",
            active=True,
        )
        business_area2 = BusinessAreaFactory(
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
        assert response.status_code == status.HTTP_403_FORBIDDEN
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            self.client.force_authenticate(self.user)
            response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 3
        assert {
            "id": str(self.business_area.id),
            "name": self.business_area.name,
            "code": self.business_area.code,
            "long_name": self.business_area.long_name,
            "slug": self.business_area.slug,
            "parent": None,
            "is_split": self.business_area.is_split,
            "active": self.business_area.active,
            "is_accountability_applicable": self.business_area.is_accountability_applicable,
        } in response.json()["results"]
        assert {
            "id": str(business_area1.id),
            "name": business_area1.name,
            "code": business_area1.code,
            "long_name": business_area1.long_name,
            "slug": business_area1.slug,
            "parent": None,
            "is_split": business_area1.is_split,
            "active": business_area1.active,
            "is_accountability_applicable": business_area1.is_accountability_applicable,
        } in response.json()["results"]
        assert {
            "id": str(business_area2.id),
            "name": business_area2.name,
            "code": business_area2.code,
            "long_name": business_area2.long_name,
            "slug": business_area2.slug,
            "parent": str(business_area2.parent.id),
            "is_split": business_area2.is_split,
            "active": business_area2.active,
            "is_accountability_applicable": business_area2.is_accountability_applicable,
        } in response.json()["results"]
