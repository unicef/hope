import json
from typing import Any, Callable

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from tests.extras.test_utils.factories.account import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.payment.api.views import PaymentPlanManagerialViewSet
from tests.extras.test_utils.factories.payment import (
    ApprovalFactory,
    ApprovalProcessFactory,
    PaymentPlanFactory,
)
from hct_mis_api.apps.payment.models import Approval, PaymentPlan
from tests.extras.test_utils.factories.fixtures import ProgramFactory

pytestmark = pytest.mark.django_db


class PaymentPlanTestMixin:
    def set_up(self, api_client: Callable, afghanistan: BusinessAreaFactory, id_to_base64: Callable) -> None:
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)
        self.afghanistan = afghanistan
        self.program1 = ProgramFactory(business_area=self.afghanistan)
        self.program2 = ProgramFactory(business_area=self.afghanistan)
        self.payment_plan1 = PaymentPlanFactory(
            program_cycle=self.program1.cycles.first(),
            business_area=self.afghanistan,
            status=PaymentPlan.Status.IN_APPROVAL,
            created_by=self.user,
        )
        self.payment_plan2 = PaymentPlanFactory(
            program_cycle=self.program2.cycles.first(),
            business_area=self.afghanistan,
            status=PaymentPlan.Status.IN_APPROVAL,
            created_by=self.user,
        )
        self.payment_plan3 = PaymentPlanFactory(
            program_cycle=self.program2.cycles.first(),
            business_area=self.afghanistan,
            status=PaymentPlan.Status.OPEN,
            created_by=self.user,
        )
        self.payment_plan1.refresh_from_db()
        self.payment_plan2.refresh_from_db()
        self.payment_plan3.refresh_from_db()


class TestPaymentPlanManagerialList(PaymentPlanTestMixin):
    def set_up(self, api_client: Callable, afghanistan: BusinessAreaFactory, id_to_base64: Callable) -> None:
        super().set_up(api_client, afghanistan, id_to_base64)
        self.url = reverse(
            "api:payments:payment-plans-managerial-list", kwargs={"business_area": self.afghanistan.slug}
        )

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([], status.HTTP_403_FORBIDDEN),
            ([Permissions.PM_VIEW_LIST], status.HTTP_403_FORBIDDEN),
            ([Permissions.PM_VIEW_LIST, Permissions.PAYMENT_VIEW_LIST_MANAGERIAL], status.HTTP_200_OK),
        ],
    )
    def test_list_payment_plans_permission(
        self,
        permissions: list,
        expected_status: str,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)

        create_user_role_with_permissions(
            self.user,
            permissions,
            self.afghanistan,
            self.program1,
        )
        response = self.client.get(self.url)
        assert response.status_code == expected_status

    def test_list_payment_plans(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        update_partner_access_to_program: Callable,
        id_to_base64: Callable,
    ) -> None:
        def _test_list() -> Any:
            """
            Helper function to test list payment plans now and again to test caching
            """
            response = self.client.get(self.url)
            assert response.status_code == status.HTTP_200_OK
            response_json = response.json()["results"]
            assert len(response_json) == 2
            assert self.payment_plan1.unicef_id in [response_json[0]["unicef_id"], response_json[1]["unicef_id"]]
            assert self.payment_plan2.unicef_id in [response_json[0]["unicef_id"], response_json[1]["unicef_id"]]
            assert self.payment_plan3.unicef_id not in [response_json[0]["unicef_id"], response_json[1]["unicef_id"]]
            return response

        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_LIST, Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
            self.afghanistan,
            self.program1,
        )
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()["results"]
        assert len(response_json) == 1
        assert response_json[0]["unicef_id"] == self.payment_plan1.unicef_id

        update_partner_access_to_program(self.partner, self.program2)

        with CaptureQueriesContext(connection) as ctx:
            response = _test_list()
            etag = response.headers["etag"]

            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 26

        # Test that reoccurring request use cached data
        with CaptureQueriesContext(connection) as ctx:
            response = _test_list()
            etag_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert etag_second_call == etag
            assert len(ctx.captured_queries) == 12

    def test_list_payment_plans_approval_process_data(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        approval_process = ApprovalProcessFactory(
            payment_plan=self.payment_plan1,
            sent_for_approval_date=timezone.datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            sent_for_approval_by=self.user,
        )
        approval_approval = ApprovalFactory(approval_process=approval_process, type=Approval.APPROVAL)
        approval_authorization = ApprovalFactory(approval_process=approval_process, type=Approval.AUTHORIZATION)
        approval_release = ApprovalFactory(approval_process=approval_process, type=Approval.FINANCE_RELEASE)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_LIST, Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
            self.afghanistan,
            self.program1,
        )
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()["results"]
        assert len(response_json) == 1
        assert response_json[0]["last_approval_process_date"] == approval_process.sent_for_approval_date.strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        assert response_json[0]["last_approval_process_by"] == str(approval_process.sent_for_approval_by)

        self.payment_plan1.status = PaymentPlan.Status.IN_AUTHORIZATION
        self.payment_plan1.save()
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()["results"]
        assert len(response_json) == 1
        assert response_json[0]["last_approval_process_date"] == approval_approval.created_at.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        assert response_json[0]["last_approval_process_by"] == str(approval_approval.created_by)

        self.payment_plan1.status = PaymentPlan.Status.IN_REVIEW
        self.payment_plan1.save()
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()["results"]
        assert len(response_json) == 1
        assert response_json[0]["last_approval_process_date"] == approval_authorization.created_at.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        assert response_json[0]["last_approval_process_by"] == str(approval_authorization.created_by)

        self.payment_plan1.status = PaymentPlan.Status.ACCEPTED
        self.payment_plan1.save()
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()["results"]
        assert len(response_json) == 1
        assert response_json[0]["last_approval_process_date"] == approval_release.created_at.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        assert response_json[0]["last_approval_process_by"] == str(approval_release.created_by)

    def _bulk_approve_action_response(self) -> Any:
        ApprovalProcessFactory(payment_plan=self.payment_plan1)
        ApprovalProcessFactory(payment_plan=self.payment_plan2)
        response = self.client.post(
            reverse(
                "api:payments:payment-plans-managerial-bulk-action", kwargs={"business_area": self.afghanistan.slug}
            ),
            data={
                "ids": [
                    encode_id_base64(self.payment_plan1.id, "PaymentPlan"),
                    encode_id_base64(self.payment_plan2.id, "PaymentPlan"),
                ],
                "action": PaymentPlan.Action.APPROVE.value,
                "comment": "Test comment",
            },
        )
        return response

    def test_bulk_action(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        update_partner_access_to_program: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            [
                Permissions.PM_VIEW_LIST,
                Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
                Permissions.PAYMENT_VIEW_LIST_MANAGERIAL,
            ],
            self.afghanistan,
            self.program1,
        )
        update_partner_access_to_program(self.partner, self.program2)
        response = self._bulk_approve_action_response()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        self.payment_plan1.refresh_from_db()
        self.payment_plan2.refresh_from_db()
        assert self.payment_plan1.status == PaymentPlan.Status.IN_AUTHORIZATION
        assert self.payment_plan2.status == PaymentPlan.Status.IN_AUTHORIZATION

    def test_bulk_action_no_approve_permissions(
        self,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        update_partner_access_to_program: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_LIST, Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
            self.afghanistan,
            self.program1,
        )
        update_partner_access_to_program(self.partner, self.program2)
        response = self._bulk_approve_action_response()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        self.payment_plan1.refresh_from_db()
        self.payment_plan2.refresh_from_db()
        assert self.payment_plan1.status == PaymentPlan.Status.IN_APPROVAL
        assert self.payment_plan2.status == PaymentPlan.Status.IN_APPROVAL

    @pytest.mark.parametrize(
        "action_name, result",
        (
            (PaymentPlan.Action.APPROVE.name, Permissions.PM_ACCEPTANCE_PROCESS_APPROVE.name),
            (PaymentPlan.Action.AUTHORIZE.name, Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE.name),
            (PaymentPlan.Action.REVIEW.name, Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW.name),
            ("Some other action name", None),
        ),
    )
    def test_get_action_permission(self, action_name: str, result: str) -> None:
        payment_plan_managerial_viewset = PaymentPlanManagerialViewSet()
        assert payment_plan_managerial_viewset._get_action_permission(action_name) == result


#  commented until we have payment plans used via API
# class TestPaymentPlanList(PaymentPlanTestMixin):
#     def set_up(self, api_client: Callable, afghanistan: BusinessAreaFactory, id_to_base64: Callable) -> None:
#         super().set_up(api_client, afghanistan, id_to_base64)
#         self.url = reverse(
#             "api:payments:payment-plans-list",
#             kwargs={
#                 "business_area": self.afghanistan.slug,
#                 "program_id": id_to_base64(self.program1.id, "Program"),
#             },
#         )
#
#     @pytest.mark.parametrize(
#         "permissions, expected_status",
#         [
#             ([], status.HTTP_403_FORBIDDEN),
#             ([Permissions.PAYMENT_VIEW_LIST_MANAGERIAL], status.HTTP_403_FORBIDDEN),
#             ([Permissions.PM_VIEW_LIST], status.HTTP_200_OK),
#             ([Permissions.PM_VIEW_LIST, Permissions.PAYMENT_VIEW_LIST_MANAGERIAL], status.HTTP_200_OK),
#         ],
#     )
#     def test_list_payment_plans_permissions(
#         self,
#         permissions: list,
#         expected_status: str,
#         api_client: Callable,
#         afghanistan: BusinessAreaFactory,
#         create_user_role_with_permissions: Callable,
#         id_to_base64: Callable,
#     ) -> None:
#         self.set_up(api_client, afghanistan, id_to_base64)
#         create_user_role_with_permissions(
#             self.user,
#             permissions,
#             self.afghanistan,
#             self.program1,
#         )
#         response = self.client.get(self.url)
#         assert response.status_code == expected_status
#
#     def test_list_payment_plans(
#         self,
#         api_client: Callable,
#         afghanistan: BusinessAreaFactory,
#         create_user_role_with_permissions: Callable,
#         update_partner_access_to_program: Callable,
#         id_to_base64: Callable,
#     ) -> None:
#         self.set_up(api_client, afghanistan, id_to_base64)
#         create_user_role_with_permissions(
#             self.user,
#             [Permissions.PM_VIEW_LIST, Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
#             self.afghanistan,
#             self.program1,
#         )
#         update_partner_access_to_program(self.partner, self.program2)
#         response = self.client.get(self.url)
#         assert response.status_code == status.HTTP_200_OK
#         response_json = response.json()["results"]
#         assert len(response_json) == 1
#
#         assert response_json[0] == {
#             "id": encode_id_base64(self.payment_plan1.id, "PaymentPlan"),
#             "unicef_id": self.payment_plan1.unicef_id,
#             "name": self.payment_plan1.name,
#             "status": self.payment_plan1.get_status_display(),
#             "target_population": self.payment_plan1.target_population.name,
#             "total_households_count": self.payment_plan1.total_households_count,
#             "currency": self.payment_plan1.get_currency_display(),
#             "total_entitled_quantity": str(self.payment_plan1.total_entitled_quantity),
#             "total_delivered_quantity": str(self.payment_plan1.total_delivered_quantity),
#             "total_undelivered_quantity": str(self.payment_plan1.total_undelivered_quantity),
#             "dispersion_start_date": self.payment_plan1.dispersion_start_date.strftime("%Y-%m-%d"),
#             "dispersion_end_date": self.payment_plan1.dispersion_end_date.strftime("%Y-%m-%d"),
#             "is_follow_up": self.payment_plan1.is_follow_up,
#             "follow_ups": [],
#             "program": self.program1.name,
#             "program_id": encode_id_base64(self.program1.id, "Program"),
#             "last_approval_process_date": self.payment_plan1.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
#             "last_approval_process_by": None,
#         }
