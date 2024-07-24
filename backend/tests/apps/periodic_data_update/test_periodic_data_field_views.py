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
from hct_mis_api.apps.core.fixtures import (
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
)
from hct_mis_api.apps.core.models import PeriodicFieldData
from hct_mis_api.apps.program.fixtures import ProgramFactory

pytestmark = pytest.mark.django_db


@freezegun.freeze_time("2022-01-01")
class TestPeriodicFieldViews:
    def set_up(self, api_client: Callable, afghanistan: BusinessAreaFactory, id_to_base64: Callable) -> None:
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)
        self.afghanistan = afghanistan
        self.program1 = ProgramFactory(business_area=self.afghanistan, name="Program1")
        self.program2 = ProgramFactory(business_area=self.afghanistan, name="Program2")

        self.periodic_field1_data = PeriodicFieldDataFactory()
        self.periodic_field1 = FlexibleAttributeForPDUFactory(program=self.program1, pdu_data=self.periodic_field1_data)

        self.periodic_field2_data = PeriodicFieldDataFactory()
        self.periodic_field2 = FlexibleAttributeForPDUFactory(program=self.program1, pdu_data=self.periodic_field2_data)

        self.periodic_field3_data = PeriodicFieldDataFactory()
        self.periodic_field3 = FlexibleAttributeForPDUFactory(program=self.program1, pdu_data=self.periodic_field3_data)

        self.periodic_field_data_program2 = PeriodicFieldDataFactory()
        self.periodic_field_program2 = FlexibleAttributeForPDUFactory(
            program=self.program2, pdu_data=self.periodic_field_data_program2
        )
        self.url_list = reverse(
            "api:periodic-data-update:periodic-fields-list",
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
    def test_list_periodic_fields_permission(
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

    def test_list_periodic_fields(
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
        assert len(response_json) == 3
        assert {
            "id": id_to_base64((self.periodic_field1.id), "FlexibleAttribute"),
            "name": self.periodic_field1.name,
            "pdu_data": {
                "subtype": self.periodic_field1.pdu_data.subtype,
                "number_of_rounds": self.periodic_field1.pdu_data.number_of_rounds,
                "rounds_names": self.periodic_field1.pdu_data.rounds_names,
            },
        } in response_json
        assert {
            "id": id_to_base64(self.periodic_field2.id, "FlexibleAttribute"),
            "name": self.periodic_field2.name,
            "pdu_data": {
                "subtype": self.periodic_field2.pdu_data.subtype,
                "number_of_rounds": self.periodic_field2.pdu_data.number_of_rounds,
                "rounds_names": self.periodic_field2.pdu_data.rounds_names,
            },
        } in response_json
        assert {
            "id": id_to_base64(self.periodic_field3.id, "FlexibleAttribute"),
            "name": self.periodic_field3.name,
            "pdu_data": {
                "subtype": self.periodic_field3.pdu_data.subtype,
                "number_of_rounds": self.periodic_field3.pdu_data.number_of_rounds,
                "rounds_names": self.periodic_field3.pdu_data.rounds_names,
            },
        } in response_json
        assert {
            "id": id_to_base64(self.periodic_field_data_program2.id, "FlexibleAttribute"),
            "name": self.periodic_field_program2.name,
            "pdu_data": {
                "subtype": self.periodic_field_program2.pdu_data.subtype,
                "number_of_rounds": self.periodic_field_program2.pdu_data.number_of_rounds,
                "rounds_names": self.periodic_field_program2.pdu_data.rounds_names,
            },
        } not in response_json

    def test_list_periodic_fields_caching(
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

        # After update of periodic field, it does not use the cached data
        self.periodic_field1.name = "New Name"
        self.periodic_field1.save()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 11

            assert etag_call_after_update != etag

        # Cached data again
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 5

            assert etag_call_after_update_second_call == etag_call_after_update

        # After update of periodic field, it does not use the cached data
        self.periodic_field1_data.subtype = PeriodicFieldData.DECIMAL
        self.periodic_field1_data.save()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update_2 = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 11

            assert etag_call_after_update_2 != etag_call_after_update_second_call
