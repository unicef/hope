import json
from typing import Callable

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext

import freezegun
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.payment.models import PaymentPlan
from tests.extras.test_utils.factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from tests.extras.test_utils.factories.payment import PaymentPlanFactory
from tests.extras.test_utils.factories.program import ProgramFactory

pytestmark = pytest.mark.django_db


@freezegun.freeze_time("2022-01-01")
class TestTargetPopulationViews:
    def set_up(self, api_client: Callable, afghanistan: BusinessAreaFactory, id_to_base64: Callable) -> None:
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)
        self.afghanistan = afghanistan
        self.program1 = ProgramFactory(business_area=self.afghanistan, name="Program1")
        self.program2 = ProgramFactory(business_area=self.afghanistan, name="Program2")

        self.tp1 = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.program1.cycles.first(),
            status=PaymentPlan.Status.TP_OPEN,
            name="Test TP 1",
        )
        self.tp2 = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.program1.cycles.first(),
            status=PaymentPlan.Status.TP_LOCKED,
            name="Test TP 2",
        )
        self.tp3 = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.program1.cycles.first(),
            status=PaymentPlan.Status.OPEN,
            name="Test 3 TP",
        )
        self.tp_program2 = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.program2.cycles.first(),
            status=PaymentPlan.Status.OPEN,
            name="Test TP Program 2",
        )

        self.url_list = reverse(
            "api:targeting:target-populations-list",
            kwargs={
                "business_area": self.afghanistan.slug,
                "program_id": id_to_base64(self.program1.id, "Program"),
            },
        )

    @pytest.mark.parametrize(
        "permissions, partner_permissions, access_to_program, expected_status",
        [
            ([], [], True, status.HTTP_403_FORBIDDEN),
            ([Permissions.TARGETING_VIEW_LIST], [], True, status.HTTP_200_OK),
            ([], [Permissions.TARGETING_VIEW_LIST], True, status.HTTP_200_OK),
            (
                [Permissions.TARGETING_VIEW_LIST],
                [Permissions.TARGETING_VIEW_LIST],
                True,
                status.HTTP_200_OK,
            ),
            ([], [], False, status.HTTP_403_FORBIDDEN),
            ([Permissions.TARGETING_VIEW_LIST], [], False, status.HTTP_403_FORBIDDEN),
            ([], [Permissions.TARGETING_VIEW_LIST], False, status.HTTP_403_FORBIDDEN),
            (
                [Permissions.TARGETING_VIEW_LIST],
                [Permissions.TARGETING_VIEW_LIST],
                False,
                status.HTTP_403_FORBIDDEN,
            ),
        ],
    )
    def test_list_target_populations_permission(
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

    def test_list_target_populations(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            [Permissions.TARGETING_VIEW_LIST],
            self.afghanistan,
            self.program1,
        )
        response = self.client.get(self.url_list)
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()["results"]
        assert len(response_json) == 3
        assert {
            "id": id_to_base64(self.tp1.id, "PaymentPlan"),
            "name": self.tp1.name,
            "status": self.tp1.get_status_display(),
            "created_by": self.tp1.created_by.get_full_name(),
            "created_at": "2022-01-01T00:00:00Z",
        } in response_json
        assert {
            "id": id_to_base64(self.tp2.id, "PaymentPlan"),
            "name": self.tp2.name,
            "status": self.tp2.get_status_display(),
            "created_by": self.tp2.created_by.get_full_name(),
            "created_at": "2022-01-01T00:00:00Z",
        } in response_json
        assert {
            "id": id_to_base64(self.tp3.id, "PaymentPlan"),
            "name": self.tp3.name,
            "status": "Assigned",
            "created_by": self.tp3.created_by.get_full_name(),
            "created_at": "2022-01-01T00:00:00Z",
        } in response_json
        assert {
            "id": id_to_base64(self.tp_program2.id, "PaymentPlan"),
            "name": self.tp_program2.name,
            "created_by": self.tp1.created_by.get_full_name(),
            "status": "Assigned",
            "created_at": "2022-01-01T00:00:00Z",
        } not in response_json

    def test_list_target_populations_filter(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            [Permissions.TARGETING_VIEW_LIST],
            self.afghanistan,
            self.program1,
        )
        response = self.client.get(self.url_list, {"status": PaymentPlan.Status.TP_OPEN})
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()["results"]
        assert len(response_json) == 1

    def test_list_target_populations_search_by_name(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            [Permissions.TARGETING_VIEW_LIST],
            self.afghanistan,
            self.program1,
        )
        response = self.client.get(self.url_list, {"name": "Test TP"})
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()["results"]
        assert len(response_json) == 2

    def test_list_target_populations_caching(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            [Permissions.TARGETING_VIEW_LIST],
            self.afghanistan,
            self.program1,
        )
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 12

        # Test that reoccurring requests use cached data
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 5

            assert etag_second_call == etag

        # After update, it does not use the cached data
        self.tp1.status = PaymentPlan.Status.TP_PROCESSING
        self.tp1.save()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 12

            assert etag_call_after_update != etag

        # Cached data again
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url_list)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 5

            assert etag_call_after_update_second_call == etag_call_after_update
