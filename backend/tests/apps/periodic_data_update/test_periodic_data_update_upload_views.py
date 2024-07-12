import json
from typing import Callable

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext

import freezegun
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.periodic_data_update.fixtures import (
    PeriodicDataUpdateTemplateFactory,
    PeriodicDataUpdateUploadFactory,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory

pytestmark = pytest.mark.django_db


@freezegun.freeze_time("2022-01-01")
class TestPeriodicDataUpdateUploadViews:
    def set_up(self, api_client: Callable, afghanistan: BusinessAreaFactory, id_to_base64: Callable) -> None:
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)
        self.afghanistan = afghanistan
        self.program1 = ProgramFactory(business_area=self.afghanistan, name="Program1")
        self.program2 = ProgramFactory(business_area=self.afghanistan, name="Program2")

        pdu_template1_program1 = PeriodicDataUpdateTemplateFactory(program=self.program1)
        pdu_template2_program1 = PeriodicDataUpdateTemplateFactory(program=self.program1)
        pdu_template_program2 = PeriodicDataUpdateTemplateFactory(program=self.program2)

        self.pdu_upload1_program1 = PeriodicDataUpdateUploadFactory(
            template=pdu_template1_program1, created_by=self.user
        )
        self.pdu_upload2_program1 = PeriodicDataUpdateUploadFactory(
            template=pdu_template2_program1, created_by=self.user
        )
        self.pdu_upload_program2 = PeriodicDataUpdateUploadFactory(template=pdu_template_program2, created_by=self.user)
        self.url_list = reverse(
            "api:periodic-data-update:periodic-data-update-uploads-list",
            kwargs={
                "business_area": self.afghanistan.slug,
                "program_id": id_to_base64(self.program1.id, "Program"),
            },
        )

    @pytest.mark.parametrize(
        "permissions, partner_permissions, access_to_program, expected_status",
        [
            ([], [], True, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_VIEW_LIST_AND_DETAILS], [], True, status.HTTP_200_OK),
            ([], [Permissions.PDU_VIEW_LIST_AND_DETAILS], True, status.HTTP_200_OK),
            (
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                True,
                status.HTTP_200_OK,
            ),
            ([], [], False, status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_VIEW_LIST_AND_DETAILS], [], False, status.HTTP_403_FORBIDDEN),
            ([], [Permissions.PDU_VIEW_LIST_AND_DETAILS], False, status.HTTP_403_FORBIDDEN),
            (
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                False,
                status.HTTP_403_FORBIDDEN,
            ),
        ],
    )
    def test_list_periodic_data_update_uploads_permission(
        self,
        permissions: list,
        partner_permissions: list,
        access_to_program: bool,
        expected_status: str,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        create_partner_role_with_permissions: Callable,
        update_partner_access_to_program: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            permissions,
            self.afghanistan,
        )
        create_partner_role_with_permissions(self.partner, partner_permissions, self.afghanistan)
        if access_to_program:
            update_partner_access_to_program(self.partner, self.program1)

        response = self.client.get(self.url_list)
        assert response.status_code == expected_status

    def test_list_periodic_data_update_templates(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            self.afghanistan,
            self.program1,
        )
        response = self.client.get(self.url_list)
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()["results"]
        assert len(response_json) == 2

        assert {
            "id": self.pdu_upload1_program1.id,
            "status": self.pdu_upload1_program1.get_status_display(),
            "template": self.pdu_upload1_program1.template.id,
            "created_at": "2022-01-01T00:00:00Z",
            "created_by": self.pdu_upload1_program1.created_by.get_full_name(),
        } in response_json
        assert {
            "id": self.pdu_upload2_program1.id,
            "status": self.pdu_upload2_program1.get_status_display(),
            "template": self.pdu_upload2_program1.template.id,
            "created_at": "2022-01-01T00:00:00Z",
            "created_by": self.pdu_upload2_program1.created_by.get_full_name(),
        } in response_json
        assert {
            "id": self.pdu_upload_program2.id,
            "status": self.pdu_upload_program2.get_status_display(),
            "template": self.pdu_upload_program2.template.id,
            "created_at": "2022-01-01T00:00:00Z",
            "created_by": self.pdu_upload_program2.created_by.get_full_name(),
        } not in response_json

    def test_list_periodic_data_update_templates_caching(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PDU_VIEW_LIST_AND_DETAILS],
            self.afghanistan,
            self.program1,
        )
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 11

        # Test that reoccurring requests use cached data
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 5

            assert etag_second_call == etag
