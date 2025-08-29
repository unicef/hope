import json
from typing import Any, Callable

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from extras.test_utils.factories.core import create_ukraine
from extras.test_utils.factories.geo import (
    AreaFactory,
    AreaTypeFactory,
    CountryFactory,
    generate_area_types,
)
from hope.apps.account.permissions import Permissions
from hope.models.country import Country
from hope.models.area import Area
from hope.models.area_type import AreaType

pytestmark = pytest.mark.django_db()


class TestAreaViews:
    def set_up(self, api_client: Callable, afghanistan: BusinessAreaFactory) -> None:
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)
        self.afghanistan = afghanistan
        self.afghanistan2 = BusinessAreaFactory(name="Afghanistan 2")

        self.country_1_afg = CountryFactory(name="Afghanistan")
        self.country_1_afg.business_areas.set([self.afghanistan, self.afghanistan2])
        self.country_2_afg = CountryFactory(
            name="Afghanistan 2",
            short_name="Afg2",
            iso_code2="A2",
            iso_code3="AF2",
            iso_num="2222",
        )
        self.country_2_afg.business_areas.set([self.afghanistan])

        self.area_type_1_afg = AreaTypeFactory(name="Area Type in Afg", country=self.country_1_afg, area_level=1)
        self.area_type_2_afg = AreaTypeFactory(name="Area Type 2 in Afg", country=self.country_1_afg, area_level=2)
        self.area_type_afg_2 = AreaTypeFactory(name="Area Type in Afg 2", country=self.country_2_afg, area_level=1)

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

        self.url_list = reverse(
            "api:geo:areas-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
            },
        )

    @pytest.mark.parametrize(
        ("permissions", "partner_permissions", "expected_status"),
        [
            ([], [], status.HTTP_403_FORBIDDEN),
            ([Permissions.GEO_VIEW_LIST], [], status.HTTP_200_OK),
            ([], [Permissions.GEO_VIEW_LIST], status.HTTP_200_OK),
            (
                [Permissions.GEO_VIEW_LIST],
                [Permissions.GEO_VIEW_LIST],
                status.HTTP_200_OK,
            ),
        ],
    )
    def test_areas_permission(
        self,
        permissions: list,
        partner_permissions: list,
        expected_status: str,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        create_partner_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            permissions,
            self.afghanistan,
        )
        create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan)

        response = self.client.get(self.url_list)
        assert response.status_code == expected_status

    def test_list_areas(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.GEO_VIEW_LIST],
            self.afghanistan,
        )
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

    def test_list_areas_filter(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.GEO_VIEW_LIST],
            self.afghanistan,
        )

        response_level_1 = self.client.get(self.url_list, {"level": 1})
        assert response_level_1.status_code == status.HTTP_200_OK

        response_json_1 = response_level_1.json()["results"]
        assert len(response_json_1) == 4
        assert {
            "id": str(self.area_1_area_type_1.id),
            "name": self.area_1_area_type_1.name,
            "p_code": self.area_1_area_type_1.p_code,
            "area_type": str(self.area_type_1_afg.id),
            "updated_at": self.area_1_area_type_1.updated_at.isoformat(timespec="microseconds").replace("+00:00", "Z"),
        } in response_json_1
        assert {
            "id": str(self.area_2_area_type_1.id),
            "name": self.area_2_area_type_1.name,
            "p_code": self.area_2_area_type_1.p_code,
            "area_type": str(self.area_type_1_afg.id),
            "updated_at": self.area_2_area_type_1.updated_at.isoformat(timespec="microseconds").replace("+00:00", "Z"),
        } in response_json_1
        assert {
            "id": str(self.area_1_area_type_afg_2.id),
            "name": self.area_1_area_type_afg_2.name,
            "p_code": self.area_1_area_type_afg_2.p_code,
            "area_type": str(self.area_type_afg_2.id),
            "updated_at": self.area_1_area_type_afg_2.updated_at.isoformat(timespec="microseconds").replace(
                "+00:00", "Z"
            ),
        } in response_json_1
        assert {
            "id": str(self.area_2_area_type_afg_2.id),
            "name": self.area_2_area_type_afg_2.name,
            "p_code": self.area_2_area_type_afg_2.p_code,
            "area_type": str(self.area_type_afg_2.id),
            "updated_at": self.area_2_area_type_afg_2.updated_at.isoformat(timespec="microseconds").replace(
                "+00:00", "Z"
            ),
        } in response_json_1

        response_level_2 = self.client.get(self.url_list, {"level": 2})
        assert response_level_2.status_code == status.HTTP_200_OK
        response_json_2 = response_level_2.json()["results"]
        assert len(response_json_2) == 2

    def test_list_areas_search_by_name(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.GEO_VIEW_LIST],
            self.afghanistan,
        )

        response = self.client.get(self.url_list, {"name": "Area 1"})
        assert response.status_code == status.HTTP_200_OK

        response_json_1 = response.json()["results"]
        assert len(response_json_1) == 3

    def test_list_areas_caching(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
        create_user_role_with_permissions(
            self.user,
            [Permissions.GEO_VIEW_LIST],
            self.afghanistan,
        )
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 7

        # Test that reoccurring requests use cached data
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 2

            assert etag_second_call == etag

        # After update of area, it does not use the cached data
        self.area_1_area_type_1.name = "Updated Area 1 Area Type 1"
        self.area_1_area_type_1.save()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 3  # fewer queries than the initial call because of cached permissions

            assert etag_call_after_update != etag

        # After removing area_type, it does not use the cached data
        self.area_type_1_afg.delete()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update_2 = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 3  # fewer queries than the initial call because of cached permissions

            assert etag_call_after_update_2 != etag_call_after_update

        # After removing country, it does not use the cached data
        self.country_2_afg.delete()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update_3 = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 3  # fewer queries than the initial call because of cached permissions

            assert etag_call_after_update_3 != etag_call_after_update_2

        # Cached data again
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 2

            assert etag_call_after_update_second_call == etag_call_after_update_3

        # Different filter - does not use cached data
        with CaptureQueriesContext(connection):
            response = self.client.get(self.url_list, {"level": 1})
            assert response.status_code == status.HTTP_200_OK

            etag_call_with_filter = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert etag_call_with_filter != etag_call_after_update_second_call

    def test_areas_tree(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Any,
    ) -> None:
        self.set_up(api_client, afghanistan)
        # call_command("init-geo-fixtures")
        business_area = create_ukraine()
        country, _ = Country.objects.get_or_create(name="Ukraine")
        business_area.countries.add(country)
        generate_area_types()

        create_user_role_with_permissions(
            self.user,
            [Permissions.GEO_VIEW_LIST],
            business_area,
        )

        p_code_prefix = country.iso_code2
        area_type_level_1 = AreaType.objects.get(country=country, area_level=1)
        area_type_level_2 = area_type_level_1.get_children().first()
        area_type_level_3 = area_type_level_2.get_children().first()
        area_type_level_4 = area_type_level_3.get_children().first()
        area_type_level_5 = area_type_level_4.get_children().first()
        # 1 level
        area_l_1 = AreaFactory(area_type=area_type_level_1, p_code=f"{p_code_prefix}11", name="City1")
        area_l_2 = AreaFactory(
            area_type=area_type_level_2,
            p_code=f"{p_code_prefix}1122",
            parent=area_l_1,
            name="City2",
        )
        area_l_3 = AreaFactory(
            area_type=area_type_level_3,
            p_code=f"{p_code_prefix}112233",
            parent=area_l_2,
            name="City3",
        )
        area_l_4 = AreaFactory(
            area_type=area_type_level_4,
            p_code=f"{p_code_prefix}11223344",
            parent=area_l_3,
            name="City4",
        )
        AreaFactory(
            area_type=area_type_level_5,
            p_code=f"{p_code_prefix}1122334455",
            parent=area_l_4,
            name="City5",
        )

        Area.objects.rebuild()
        AreaType.objects.rebuild()
        Country.objects.rebuild()

        # check api
        response = self.client.get(reverse("api:geo:areas-all-areas-tree", kwargs={"business_area_slug": "ukraine"}))
        assert response.status_code == status.HTTP_200_OK
        response_results = response.json()
        assert len(response_results) == 1
        assert response_results[0]["name"] == "City1"
        assert response_results[0]["areas"][0]["name"] == "City2"
        assert response_results[0]["areas"][0]["areas"][0]["name"] == "City3"
        assert len(response_results[0]["areas"][0]["areas"][0]["areas"]) == 0
