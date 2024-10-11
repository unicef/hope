import json
from typing import Callable

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory

pytestmark = pytest.mark.django_db


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
            name="Area 1 Area Type 1", area_type=self.area_type_1_afg, p_code="AREA1-ARTYPE1"
        )
        self.area_2_area_type_1 = AreaFactory(
            name="Area 2 Area Type 1", area_type=self.area_type_1_afg, p_code="AREA2-ARTYPE1"
        )
        self.area_1_area_type_2 = AreaFactory(
            name="Area 1 Area Type 2", area_type=self.area_type_2_afg, p_code="AREA1-ARTYPE2"
        )
        self.area_2_area_type_2 = AreaFactory(
            name="Area 2 Area Type 2", area_type=self.area_type_2_afg, p_code="AREA2-ARTYPE2"
        )
        self.area_1_area_type_afg_2 = AreaFactory(
            name="Area 1 Area Type Afg 2", area_type=self.area_type_afg_2, p_code="AREA1-ARTYPE-AFG2"
        )
        self.area_2_area_type_afg_2 = AreaFactory(
            name="Area 2 Area Type Afg 2", area_type=self.area_type_afg_2, p_code="AREA2-ARTYPE-AFG2"
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
                "business_area": self.afghanistan.slug,
            },
        )

    @pytest.mark.parametrize(
        "permissions, partner_permissions, expected_status",
        [
            ([], [], status.HTTP_403_FORBIDDEN),
            ([Permissions.GEO_VIEW_LIST], [], status.HTTP_200_OK),
            ([], [Permissions.GEO_VIEW_LIST], status.HTTP_200_OK),
            ([Permissions.GEO_VIEW_LIST], [Permissions.GEO_VIEW_LIST], status.HTTP_200_OK),
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
        id_to_base64: Callable,
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
            "id": id_to_base64(self.area_1_area_type_1.id, "Area"),
            "name": self.area_1_area_type_1.name,
            "p_code": self.area_1_area_type_1.p_code,
        } in response_json
        assert {
            "id": id_to_base64(self.area_2_area_type_1.id, "Area"),
            "name": self.area_2_area_type_1.name,
            "p_code": self.area_2_area_type_1.p_code,
        } in response_json
        assert {
            "id": id_to_base64(self.area_1_area_type_2.id, "Area"),
            "name": self.area_1_area_type_2.name,
            "p_code": self.area_1_area_type_2.p_code,
        } in response_json
        assert {
            "id": id_to_base64(self.area_2_area_type_2.id, "Area"),
            "name": self.area_2_area_type_2.name,
            "p_code": self.area_2_area_type_2.p_code,
        } in response_json
        assert {
            "id": id_to_base64(self.area_1_area_type_afg_2.id, "Area"),
            "name": self.area_1_area_type_afg_2.name,
            "p_code": self.area_1_area_type_afg_2.p_code,
        } in response_json
        assert {
            "id": id_to_base64(self.area_2_area_type_afg_2.id, "Area"),
            "name": self.area_2_area_type_afg_2.name,
            "p_code": self.area_2_area_type_afg_2.p_code,
        } in response_json
        assert {
            "id": id_to_base64(self.area_other.id, "Area"),
            "name": self.area_other.name,
            "p_code": self.area_other.p_code,
        } not in response_json

    def test_list_areas_filter(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        id_to_base64: Callable,
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
            "id": id_to_base64(self.area_1_area_type_1.id, "Area"),
            "name": self.area_1_area_type_1.name,
            "p_code": self.area_1_area_type_1.p_code,
        } in response_json_1
        assert {
            "id": id_to_base64(self.area_2_area_type_1.id, "Area"),
            "name": self.area_2_area_type_1.name,
            "p_code": self.area_2_area_type_1.p_code,
        } in response_json_1
        assert {
            "id": id_to_base64(self.area_1_area_type_afg_2.id, "Area"),
            "name": self.area_1_area_type_afg_2.name,
            "p_code": self.area_1_area_type_afg_2.p_code,
        } in response_json_1
        assert {
            "id": id_to_base64(self.area_2_area_type_afg_2.id, "Area"),
            "name": self.area_2_area_type_afg_2.name,
            "p_code": self.area_2_area_type_afg_2.p_code,
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
        id_to_base64: Callable,
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
            assert len(ctx.captured_queries) == 4

            assert etag_second_call == etag

        # After update of area, it does not use the cached data
        self.area_1_area_type_1.name = "Updated Area 1 Area Type 1"
        self.area_1_area_type_1.save()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 7

            assert etag_call_after_update != etag

        # After removing area_type, it does not use the cached data
        self.area_type_1_afg.delete()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update_2 = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 7

            assert etag_call_after_update_2 != etag_call_after_update

        # After removing country, it does not use the cached data
        self.country_2_afg.delete()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update_3 = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 7

            assert etag_call_after_update_3 != etag_call_after_update_2

        # Cached data again
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 4

            assert etag_call_after_update_second_call == etag_call_after_update_3

        # Different filter - does not use cached data
        with CaptureQueriesContext(connection):
            response = self.client.get(self.url_list, {"level": 1})
            assert response.status_code == status.HTTP_200_OK

            etag_call_with_filter = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert etag_call_with_filter != etag_call_after_update_second_call
