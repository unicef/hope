import json
from typing import Any

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
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.fixtures import ProgramFactory

pytestmark = pytest.mark.django_db


class TestBusinessAreaList:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        api_client: Any,
        create_user_role_with_permissions: Any,
        create_partner_role_with_permissions: Any,
    ) -> None:
        self.afghanistan = BusinessAreaFactory(slug="afghanistan", active=True)
        self.ukraine = BusinessAreaFactory(slug="ukraine", active=True)
        self.syria = BusinessAreaFactory(slug="syria", active=True)
        self.croatia = BusinessAreaFactory(slug="croatia", active=True)
        self.sudan = BusinessAreaFactory(slug="sudan", active=True)
        self.somalia = BusinessAreaFactory(slug="somalia", active=False)
        self.list_url = reverse(
            "api:core:business-areas-list",
        )
        self.count_url = reverse(
            "api:core:business-areas-count",
        )
        self.partner = PartnerFactory(name="TestPartner")

        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.afghanistan,
            whole_business_area_access=True,
        )
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.ukraine,
            program=ProgramFactory(
                business_area=self.ukraine,
            ),
        )
        create_partner_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.syria,
            whole_business_area_access=True,
        )
        create_partner_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.croatia,
            program=ProgramFactory(
                business_area=self.croatia,
            ),
        )
        create_partner_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.somalia,
            whole_business_area_access=True,
        )

    def test_business_area_list(
        self,
    ) -> None:
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 5
        business_area_ids = {ba["id"] for ba in response_data}
        assert self.afghanistan.id in business_area_ids
        assert self.ukraine.id in business_area_ids
        assert self.syria.id in business_area_ids
        assert self.croatia.id in business_area_ids
        assert self.somalia.id in business_area_ids
        assert self.sudan.id not in business_area_ids

        available_business_areas = BusinessArea.objects.filter(id__in=business_area_ids).order_by("id")
        for i, business_area in enumerate(available_business_areas):
            assert response_data[i]["id"] == business_area.id
            assert response_data[i]["name"] == business_area.name
            assert response_data[i]["code"] == business_area.code
            assert response_data[i]["long_name"] == business_area.long_name
            assert response_data[i]["slug"] == business_area.slug
            assert response_data[i]["parent"] == business_area.parent
            assert response_data[i]["is_split"] == business_area.is_split
            assert response_data[i]["active"] == business_area.active

    def test_business_area_count(
        self,
        create_user_role_with_permissions: Any,
    ) -> None:
        response = self.client.get(self.count_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 5

    def test_business_area_list_caching(self, create_user_role_with_permissions: Any) -> None:
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(response.json()["results"]) == 5
            assert len(ctx.captured_queries) == 10

        # no change - use cache
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_second_call = response.headers["etag"]
            assert etag == etag_second_call
            assert len(ctx.captured_queries) == 10

        self.afghanistan.active = False
        self.afghanistan.save()
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_third_call = response.headers["etag"]
            assert json.loads(cache.get(etag_third_call)[0].decode("utf8")) == response.json()
            assert etag_third_call not in [etag, etag_second_call]
            # 4 queries are saved because of cached permissions calculations
            assert len(ctx.captured_queries) == 18

        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.sudan,
            whole_business_area_access=True,
        )
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_fourth_call = response.headers["etag"]
            assert json.loads(cache.get(etag_fourth_call)[0].decode("utf8")) == response.json()
            assert etag_fourth_call not in [etag, etag_second_call, etag_third_call]
            assert len(response.json()["results"]) == 6
            assert len(ctx.captured_queries) == 18

        # no change - use cache
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_fifth_call = response.headers["etag"]
            assert etag_fifth_call == etag_fourth_call
            assert len(ctx.captured_queries) == 10


class TestBusinessAreaDetail:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        api_client: Any,
        create_user_role_with_permissions: Any,
    ) -> None:
        self.afghanistan = BusinessAreaFactory(slug="afghanistan")
        self.detail_url_name = "api:core:business-areas-detail"
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.afghanistan,
            whole_business_area_access=True,
        )

    def test_business_area_detail(
        self,
    ) -> None:
        response = self.client.get(reverse(self.detail_url_name, kwargs={"business_area_slug": self.afghanistan.slug}))
        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()

        assert response_data["id"] == str(self.afghanistan.id)
        assert response_data["name"] == self.afghanistan.name
        assert response_data["code"] == self.afghanistan.code
        assert response_data["long_name"] == self.afghanistan.long_name
        assert response_data["slug"] == self.afghanistan.slug
        assert response_data["parent"] == self.afghanistan.parent
        assert response_data["is_split"] == self.afghanistan.is_split
        assert response_data["active"] == self.afghanistan.active
