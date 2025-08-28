import json
from typing import Any
from unittest.mock import patch

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from extras.test_utils.factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from extras.test_utils.factories.program import ProgramFactory
import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from test_utils.factories.core import PeriodicFieldDataFactory

from hope.apps.account.permissions import Permissions
from hope.apps.core.models import (
    BusinessArea,
    FlexibleAttribute,
    FlexibleAttributeChoice,
    PeriodicFieldData,
)
from hope.apps.core.utils import get_fields_attr_generators

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
            self.partner,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.syria,
            whole_business_area_access=True,
        )
        create_partner_role_with_permissions(
            self.partner,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.croatia,
            program=ProgramFactory(
                business_area=self.croatia,
            ),
        )
        create_partner_role_with_permissions(
            self.partner,
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
        assert str(self.afghanistan.id) in business_area_ids
        assert str(self.ukraine.id) in business_area_ids
        assert str(self.syria.id) in business_area_ids
        assert str(self.croatia.id) in business_area_ids
        assert str(self.somalia.id) in business_area_ids
        assert str(self.sudan.id) not in business_area_ids

        available_business_areas = BusinessArea.objects.filter(id__in=business_area_ids).order_by("id")
        for i, business_area in enumerate(available_business_areas):
            assert response_data[i]["id"] == str(business_area.id)
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
            response = self.client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(response.json()["results"]) == 5
            assert len(ctx.captured_queries) == 6

        # no change - use cache
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_second_call = response.headers["etag"]
            assert etag == etag_second_call
            assert len(ctx.captured_queries) == 5

        self.afghanistan.active = False
        self.afghanistan.save()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_third_call = response.headers["etag"]
            assert json.loads(cache.get(etag_third_call)[0].decode("utf8")) == response.json()
            assert etag_third_call not in [etag, etag_second_call]
            # 4 queries are saved because of cached permissions calculations
            assert len(ctx.captured_queries) == 6

        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.sudan,
            whole_business_area_access=True,
        )
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_fourth_call = response.headers["etag"]
            assert json.loads(cache.get(etag_fourth_call)[0].decode("utf8")) == response.json()
            assert etag_fourth_call not in [etag, etag_second_call, etag_third_call]
            assert len(response.json()["results"]) == 6
            assert len(ctx.captured_queries) == 6

        # no change - use cache
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_fifth_call = response.headers["etag"]
            assert etag_fifth_call == etag_fourth_call
            assert len(ctx.captured_queries) == 5


class TestBusinessAreaDetail:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        api_client: Any,
        create_user_role_with_permissions: Any,
    ) -> None:
        self.afghanistan = BusinessAreaFactory(name="Afghanistan", slug="afghanistan", kobo_token="123")
        self.detail_url_name = "api:core:business-areas-detail"
        self.user = UserFactory()
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
        response = self.client.get(reverse(self.detail_url_name, kwargs={"slug": self.afghanistan.slug}))
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


class TestBusinessAreaFilter:
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
            self.partner,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.syria,
            whole_business_area_access=True,
        )
        create_partner_role_with_permissions(
            self.partner,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.croatia,
            program=ProgramFactory(
                business_area=self.croatia,
            ),
        )
        create_partner_role_with_permissions(
            self.partner,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.somalia,
            whole_business_area_access=True,
        )

    def test_filter_by_active(self) -> None:
        response_active = self.client.get(self.list_url, {"active": True})
        assert response_active.status_code == status.HTTP_200_OK
        response_data_active = response_active.json()["results"]
        assert len(response_data_active) == 4
        business_area_ids = {ba["id"] for ba in response_data_active}
        assert str(self.afghanistan.id) in business_area_ids
        assert str(self.ukraine.id) in business_area_ids
        assert str(self.syria.id) in business_area_ids
        assert str(self.croatia.id) in business_area_ids
        assert str(self.sudan.id) not in business_area_ids
        assert str(self.somalia.id) not in business_area_ids

        response_inactive = self.client.get(self.list_url, {"active": False})
        assert response_inactive.status_code == status.HTTP_200_OK
        response_data_inactive = response_inactive.json()["results"]
        assert len(response_data_inactive) == 1
        business_area_ids = {ba["id"] for ba in response_data_inactive}
        assert str(self.somalia.id) in business_area_ids
        assert str(self.afghanistan.id) not in business_area_ids
        assert str(self.ukraine.id) not in business_area_ids
        assert str(self.syria.id) not in business_area_ids
        assert str(self.croatia.id) not in business_area_ids
        assert str(self.sudan.id) not in business_area_ids


class TestKoboAssetList:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        api_client: Any,
        create_user_role_with_permissions: Any,
    ) -> None:
        self.afghanistan = BusinessAreaFactory(name="Afghanistan", slug="afghanistan", kobo_token="123")
        self.detail_url_name = "api:core:business-areas-detail"
        self.user = UserFactory()
        self.client = api_client(self.user)

        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
            self.afghanistan,
            whole_business_area_access=True,
        )

    @patch("hope.apps.core.kobo.api.KoboAPI.__init__")
    @patch("hope.apps.core.kobo.api.KoboAPI.get_all_projects_data")
    def test_get_kobo_asset_list(self, mock_get_all_projects_data: Any, mock_kobo_init: Any) -> None:
        mock_kobo_init.return_value = None
        mock_get_all_projects_data.return_value = [
            {
                "name": "Registration 2025",
                "uid": "123",
                "has_deployment": True,
                "asset_type": "Type",
                "deployment__active": True,
                "downloads": [{"format": "xls", "url": "xlsx_url"}],
                "settings": {
                    "sector": {"label": "Sector 123"},
                    "country": {"label": "Country Test"},
                },
                "date_modified": "2022-02-22",
            },
            {
                "name": "Campain 123",
                "uid": "222",
                "has_deployment": True,
                "asset_type": "Type",
                "deployment__active": True,
                "downloads": [{"format": "xls", "url": "xlsx_url"}],
                "settings": {
                    "sector": {"label": "Sector 123"},
                    "country": {"label": "Country Test"},
                },
                "date_modified": "2022-02-22",
            },
        ]

        response = self.client.post(
            reverse(
                "api:core:business-areas-all-kobo-projects",
                kwargs={"slug": self.afghanistan.slug},
            ),
            {"only_deployed": True},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2


class TestAllFieldsAttributes:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.user = UserFactory()
        self.client = api_client(self.user)
        self.afghanistan = BusinessAreaFactory(slug="afghanistan", active=True)
        self.all_fields_attributes_url = reverse(
            "api:core:business-areas-all-fields-attributes",
            kwargs={
                "slug": self.afghanistan.slug,
            },
        )

        flex_field_1 = FlexibleAttribute.objects.create(
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            label={"English(EN)": "Flex Field 1"},
            name="flex_field_1",
        )
        flex_field_2 = FlexibleAttribute.objects.create(
            type=FlexibleAttribute.INTEGER,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            label={"English(EN)": "Muac"},
            name="muac",
        )
        choice_1 = FlexibleAttributeChoice.objects.create(
            label={"English(EN)": "Choice 1"},
            name="option_1",
            list_name="Option 1",
        )
        choice_2 = FlexibleAttributeChoice.objects.create(
            label={"English(EN)": "Choice 2"},
            name="option_2",
            list_name="Option 2",
        )
        choice_1.flex_attributes.add(flex_field_1)
        choice_2.flex_attributes.add(flex_field_2)

        self.program = ProgramFactory(business_area=self.afghanistan)

        # pdu
        pdu_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=1,
            rounds_names=["January"],
        )
        FlexibleAttribute.objects.create(
            label={"English(EN)": "PDU Field 1"},
            name="pdu_field_1",
            type=FlexibleAttribute.PDU,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            program=self.program,
            pdu_data=pdu_data,
        )

    def test_all_fields_attributes(self) -> None:
        response = self.client.get(self.all_fields_attributes_url)
        assert response.status_code == status.HTTP_200_OK

        response_data = response.data
        expected_response_flex_fields = [
            {
                "id": str(attr.id),
                "type": attr.type,
                "name": attr.name,
                "labels": [{"language": k, "label": v} for k, v in attr.label.items()],
                "label_en": attr.label.get("English(EN)", None) if getattr(attr, "label", None) else None,
                "hint": str(attr.hint),
                "choices": [
                    {
                        "labels": [{"language": k, "label": v} for k, v in choice.label.items()],
                        "label_en": choice.label.get("English(EN)", None) if getattr(choice, "label", None) else None,
                        "value": choice.name,
                        "list_name": choice.list_name,
                    }
                    for choice in attr.choices.all()
                ],
                "associated_with": "Household" if attr.associated_with == 0 else "Individual",
                "is_flex_field": True,
                "pdu_data": (
                    {
                        "subtype": attr.pdu_data.subtype,
                        "number_of_rounds": attr.pdu_data.number_of_rounds,
                        "rounds_names": attr.pdu_data.rounds_names,
                    }
                )
                if attr.pdu_data
                else None,
            }
            for attr in get_fields_attr_generators(flex_field=True)
        ]
        expected_response_core_fields = [
            {
                "id": attr_dict["id"],
                "type": attr_dict["type"],
                "name": attr_dict["name"],
                "labels": [{"language": k, "label": v} for k, v in attr_dict["label"].items()],
                "label_en": attr_dict.get("label", {}).get("English(EN)", None) if attr_dict.get("label") else None,
                "hint": attr_dict["hint"],
                "choices": [
                    {
                        "labels": [{"language": k, "label": v} for k, v in choice.get("label", {}).items()],
                        "label_en": choice.get("label", {}).get("English(EN)", None) if choice.get("label") else None,
                        "value": choice.get("value", None),
                        "list_name": choice.get("list_name", None),
                    }
                    for choice in attr_dict.get("choices", [])
                ],
                "associated_with": attr_dict.get("associated_with"),
                "is_flex_field": False,
                "pdu_data": None,
            }
            for attr_dict in get_fields_attr_generators(flex_field=False)
        ]
        sorted_response_data = sorted(response_data, key=lambda x: str(x.get("id")))
        sorted_expected_attributes = sorted(
            expected_response_flex_fields + expected_response_core_fields,
            key=lambda x: str(x.get("id")),
        )
        assert len(response_data) == len(sorted_expected_attributes)
        assert sorted_response_data == sorted_expected_attributes

    def test_all_fields_attributes_with_program(self) -> None:
        response = self.client.get(self.all_fields_attributes_url, {"program_id": str(self.program.id)})
        assert response.status_code == status.HTTP_200_OK

        response_data = response.data
        expected_response_flex_fields = [
            {
                "id": str(attr.id),
                "type": attr.type,
                "name": attr.name,
                "labels": [{"language": k, "label": v} for k, v in attr.label.items()],
                "label_en": attr.label.get("English(EN)", None) if getattr(attr, "label", None) else None,
                "hint": str(attr.hint),
                "choices": [
                    {
                        "labels": [{"language": k, "label": v} for k, v in choice.label.items()],
                        "label_en": choice.label.get("English(EN)", None) if getattr(choice, "label", None) else None,
                        "value": choice.name,
                        "list_name": choice.list_name,
                    }
                    for choice in attr.choices.all()
                ],
                "associated_with": "Household" if attr.associated_with == 0 else "Individual",
                "is_flex_field": True,
                "pdu_data": (
                    {
                        "subtype": attr.pdu_data.subtype,
                        "number_of_rounds": attr.pdu_data.number_of_rounds,
                        "rounds_names": attr.pdu_data.rounds_names,
                    }
                )
                if attr.pdu_data
                else None,
            }
            for attr in get_fields_attr_generators(
                flex_field=True,
                business_area_slug=self.afghanistan.slug,
                program_id=self.program.id,
            )
        ]
        expected_response_core_fields = [
            {
                "id": attr_dict["id"],
                "type": attr_dict["type"],
                "name": attr_dict["name"],
                "labels": [{"language": k, "label": v} for k, v in attr_dict["label"].items()],
                "label_en": attr_dict.get("label", {}).get("English(EN)", None) if attr_dict.get("label") else None,
                "hint": attr_dict["hint"],
                "choices": [
                    {
                        "labels": [{"language": k, "label": v} for k, v in choice.get("label", {}).items()],
                        "label_en": choice.get("label", {}).get("English(EN)", None) if choice.get("label") else None,
                        "value": choice.get("value", None),
                        "list_name": choice.get("list_name", None),
                    }
                    for choice in attr_dict.get("choices", [])
                ],
                "associated_with": attr_dict.get("associated_with"),
                "is_flex_field": False,
                "pdu_data": None,
            }
            for attr_dict in get_fields_attr_generators(flex_field=False)
        ]
        sorted_response_data = sorted(response_data, key=lambda x: str(x.get("id")))
        sorted_expected_attributes = sorted(
            expected_response_flex_fields + expected_response_core_fields,
            key=lambda x: str(x.get("id")),
        )
        assert len(response_data) == len(sorted_expected_attributes)
        assert sorted_response_data == sorted_expected_attributes
