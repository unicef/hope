from extras.test_utils.factories.account import BusinessAreaFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from rest_framework import status
from rest_framework.reverse import reverse
from unit.api.base import HOPEApiTestCase, token_grant_permission

from hope.api.models import Grant


class APIAreaTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.url_list = reverse(
            "api:geo:areas-list",
            kwargs={
                "business_area_slug": cls.business_area.slug,
            },
        )

    def test_list_business_area(self) -> None:
        self.business_area_2 = BusinessAreaFactory(name="Afghanistan 2")
        self.country_1 = CountryFactory(name="Afghanistan")
        self.country_1.business_areas.set([self.business_area, self.business_area_2])
        self.country_2 = CountryFactory(
            name="Afghanistan 2",
            short_name="Afg2",
            iso_code2="A2",
            iso_code3="AF2",
            iso_num="2222",
        )
        self.country_2.business_areas.set([self.business_area])

        self.area_type_1_afg = AreaTypeFactory(name="Area Type in Afg", country=self.country_1, area_level=1)
        self.area_type_2_afg = AreaTypeFactory(name="Area Type 2 in Afg", country=self.country_1, area_level=2)
        self.area_type_afg_2 = AreaTypeFactory(name="Area Type in Afg 2", country=self.country_2, area_level=1)

        self.area_1_area_type_1 = AreaFactory(
            name="Area 1 Area Type 1",
            area_type=self.area_type_1_afg,
            p_code="AREA1-ARTYPE1",
        )
        self.area_2_area_type_1 = AreaFactory(
            name="Area 2 Area Type 1",
            area_type=self.area_type_1_afg,
            p_code="AREA2-ARTYPE1",
        )
        self.area_1_area_type_2 = AreaFactory(
            name="Area 1 Area Type 2",
            area_type=self.area_type_2_afg,
            p_code="AREA1-ARTYPE2",
        )
        self.area_2_area_type_2 = AreaFactory(
            name="Area 2 Area Type 2",
            area_type=self.area_type_2_afg,
            p_code="AREA2-ARTYPE2",
        )
        self.area_1_area_type_afg_2 = AreaFactory(
            name="Area 1 Area Type Afg 2",
            area_type=self.area_type_afg_2,
            p_code="AREA1-ARTYPE-AFG2",
        )
        self.area_2_area_type_afg_2 = AreaFactory(
            name="Area 2 Area Type Afg 2",
            area_type=self.area_type_afg_2,
            p_code="AREA2-ARTYPE-AFG2",
        )

        self.business_area_other = BusinessAreaFactory(name="Other")
        self.country_other = CountryFactory(
            name="Other Country",
            short_name="Oth",
            iso_code2="O",
            iso_code3="OTH",
            iso_num="111",
        )
        self.country_other.business_areas.set([self.business_area_other])
        self.area_type_other = AreaTypeFactory(name="Area Type Other", country=self.country_other)
        self.area_other = AreaFactory(name="Area Other", area_type=self.area_type_other, p_code="AREA-OTHER")

        response = self.client.get(self.url_list)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.url_list)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()["results"]
        assert len(response_json) == 6
        assert {
            "id": str(self.area_1_area_type_1.id),
            "name": self.area_1_area_type_1.name,
            "p_code": self.area_1_area_type_1.p_code,
            "area_type": str(self.area_type_1_afg.id),
            "updated_at": self.area_1_area_type_1.updated_at.isoformat(timespec="microseconds").replace("+00:00", "Z"),
        } in response_json
        assert {
            "id": str(self.area_2_area_type_1.id),
            "name": self.area_2_area_type_1.name,
            "p_code": self.area_2_area_type_1.p_code,
            "area_type": str(self.area_type_1_afg.id),
            "updated_at": self.area_2_area_type_1.updated_at.isoformat(timespec="microseconds").replace("+00:00", "Z"),
        } in response_json
        assert {
            "id": str(self.area_1_area_type_2.id),
            "name": self.area_1_area_type_2.name,
            "p_code": self.area_1_area_type_2.p_code,
            "area_type": str(self.area_type_2_afg.id),
            "updated_at": self.area_1_area_type_2.updated_at.isoformat(timespec="microseconds").replace("+00:00", "Z"),
        } in response_json
        assert {
            "id": str(self.area_2_area_type_2.id),
            "name": self.area_2_area_type_2.name,
            "p_code": self.area_2_area_type_2.p_code,
            "area_type": str(self.area_type_2_afg.id),
            "updated_at": self.area_2_area_type_2.updated_at.isoformat(timespec="microseconds").replace("+00:00", "Z"),
        } in response_json
        assert {
            "id": str(self.area_1_area_type_afg_2.id),
            "name": self.area_1_area_type_afg_2.name,
            "p_code": self.area_1_area_type_afg_2.p_code,
            "area_type": str(self.area_type_afg_2.id),
            "updated_at": self.area_1_area_type_afg_2.updated_at.isoformat(timespec="microseconds").replace(
                "+00:00", "Z"
            ),
        } in response_json
        assert {
            "id": str(self.area_2_area_type_afg_2.id),
            "name": self.area_2_area_type_afg_2.name,
            "p_code": self.area_2_area_type_afg_2.p_code,
            "area_type": str(self.area_type_afg_2.id),
            "updated_at": self.area_2_area_type_afg_2.updated_at.isoformat(timespec="microseconds").replace(
                "+00:00", "Z"
            ),
        } in response_json
        assert {
            "id": str(self.area_other.id),
            "name": self.area_other.name,
            "p_code": self.area_other.p_code,
            "area_type": str(self.area_type_other.id),
            "updated_at": self.area_other.updated_at.isoformat(timespec="microseconds").replace("+00:00", "Z"),
        } not in response_json
