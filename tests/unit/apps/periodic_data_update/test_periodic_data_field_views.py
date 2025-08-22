import json
from typing import Callable

import freezegun
import pytest
from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from extras.test_utils.factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from extras.test_utils.factories.core import (
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from rest_framework import status
from rest_framework.reverse import reverse

from hope.apps.account.permissions import Permissions
from hope.apps.core.models import PeriodicFieldData

pytestmark = pytest.mark.django_db()


@freezegun.freeze_time("2022-01-01")
class TestPeriodicFieldViews:
    def set_up(self, api_client: Callable, afghanistan: BusinessAreaFactory) -> None:
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
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program1.slug,
            },
        )

    def test_list_periodic_fields(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
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
            "id": str(self.periodic_field1.id),
            "name": self.periodic_field1.name,
            "label": self.periodic_field1.label["English(EN)"],
            "pdu_data": {
                "subtype": self.periodic_field1.pdu_data.subtype,
                "number_of_rounds": self.periodic_field1.pdu_data.number_of_rounds,
                "rounds_names": self.periodic_field1.pdu_data.rounds_names,
                "rounds_covered": self.periodic_field1.pdu_data.rounds_covered,
            },
        } in response_json
        assert {
            "id": str(self.periodic_field2.id),
            "name": self.periodic_field2.name,
            "label": self.periodic_field2.label["English(EN)"],
            "pdu_data": {
                "subtype": self.periodic_field2.pdu_data.subtype,
                "number_of_rounds": self.periodic_field2.pdu_data.number_of_rounds,
                "rounds_names": self.periodic_field2.pdu_data.rounds_names,
                "rounds_covered": self.periodic_field1.pdu_data.rounds_covered,
            },
        } in response_json
        assert {
            "id": str(self.periodic_field3.id),
            "name": self.periodic_field3.name,
            "label": self.periodic_field3.label["English(EN)"],
            "pdu_data": {
                "subtype": self.periodic_field3.pdu_data.subtype,
                "number_of_rounds": self.periodic_field3.pdu_data.number_of_rounds,
                "rounds_names": self.periodic_field3.pdu_data.rounds_names,
                "rounds_covered": self.periodic_field1.pdu_data.rounds_covered,
            },
        } in response_json
        assert {
            "id": str(self.periodic_field_data_program2.id),
            "name": self.periodic_field_program2.name,
            "label": self.periodic_field_program2.label["English(EN)"],
            "pdu_data": {
                "subtype": self.periodic_field_program2.pdu_data.subtype,
                "number_of_rounds": self.periodic_field_program2.pdu_data.number_of_rounds,
                "rounds_names": self.periodic_field_program2.pdu_data.rounds_names,
                "rounds_covered": self.periodic_field1.pdu_data.rounds_covered,
            },
        } not in response_json

    def test_list_periodic_fields_caching(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan)
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
            assert len(ctx.captured_queries) == 7

        # Test that reoccurring requests use cached data
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 1

            assert etag_second_call == etag

        # After update of periodic field, it does not use the cached data
        self.periodic_field1.name = "New Name"
        self.periodic_field1.save()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 7

            assert etag_call_after_update != etag

        # Cached data again
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 1

            assert etag_call_after_update_second_call == etag_call_after_update

        # After update of periodic field, it does not use the cached data
        self.periodic_field1_data.subtype = PeriodicFieldData.DECIMAL
        self.periodic_field1_data.save()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update_2 = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 7

            assert etag_call_after_update_2 != etag_call_after_update_second_call
