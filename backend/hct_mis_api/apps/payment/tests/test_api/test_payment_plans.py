from typing import Any

from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIClient

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.payment.fixtures import (
    ApprovalFactory,
    ApprovalProcessFactory,
    PaymentPlanFactory,
)
from hct_mis_api.apps.payment.models import Approval, PaymentPlan
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestPaymentPlansListView(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.business_area = create_afghanistan()
        self.program1 = ProgramFactory(business_area=self.business_area)
        self.program2 = ProgramFactory(business_area=self.business_area)
        self.partner = PartnerFactory(name="TestPartner")
        self.payment_plan1 = PaymentPlanFactory(
            program=self.program1,
            business_area=self.business_area,
            status=PaymentPlan.Status.IN_APPROVAL,
        )
        self.payment_plan2 = PaymentPlanFactory(
            program=self.program2,
            business_area=self.business_area,
            status=PaymentPlan.Status.IN_APPROVAL,
        )
        self.payment_plan3 = PaymentPlanFactory(
            program=self.program2,
            business_area=self.business_area,
            status=PaymentPlan.Status.OPEN,
        )
        self.payment_plan1.refresh_from_db()
        self.payment_plan2.refresh_from_db()
        self.payment_plan3.refresh_from_db()

        self.headers = {
            "HTTP_Business-Area": self.business_area.slug,
            "HTTP_Program": self.id_to_base64(self.program1.id, "Program"),
        }
        self.headers_no_program = {
            "HTTP_Business-Area": self.business_area.slug,
        }
        self.url = reverse("payments:payment-plan-list")
        self.user = UserFactory(partner=self.partner)
        self.client = APIClient()  # type: ignore
        self.client.force_authenticate(user=self.user)

    def test_list_payment_plans_no_permissions(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [],
            self.business_area,
            self.program1,
        )
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_payment_plans_program_header_and_one_permission(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_LIST],
            self.business_area,
            self.program1,
        )
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_payment_plans_no_program_header_and_all_permission(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_LIST, Permissions.PAYMENT_VIEW_LIST_NO_GPF],
            self.business_area,
            self.program1,
        )
        response = self.client.get(self.url, **self.headers_no_program)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_payment_plans_no_program_header_and_no_gpf_permission(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_LIST],
            self.business_area,
            self.program1,
        )
        response = self.client.get(self.url, **self.headers_no_program)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_payment_plans(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_LIST, Permissions.PAYMENT_VIEW_LIST_NO_GPF],
            self.business_area,
            self.program1,
        )
        self.update_user_partner_perm_for_program(self.user, self.business_area, self.program2)
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()["results"]
        self.assertEqual(len(response_json), 1)

        self.assertEqual(
            response_json[0],
            {
                "id": encode_id_base64(self.payment_plan1.id, "PaymentPlan"),
                "unicef_id": self.payment_plan1.unicef_id,
                "name": self.payment_plan1.name,
                "status": self.payment_plan1.get_status_display(),
                "target_population": self.payment_plan1.target_population.name,
                "total_households_count": self.payment_plan1.total_households_count,
                "currency": self.payment_plan1.get_currency_display(),
                "total_entitled_quantity": str(self.payment_plan1.total_entitled_quantity),
                "total_delivered_quantity": str(self.payment_plan1.total_delivered_quantity),
                "total_undelivered_quantity": str(self.payment_plan1.total_undelivered_quantity),
                "dispersion_start_date": self.payment_plan1.dispersion_start_date.strftime("%Y-%m-%d"),
                "dispersion_end_date": self.payment_plan1.dispersion_end_date.strftime("%Y-%m-%d"),
                "is_follow_up": self.payment_plan1.is_follow_up,
                "follow_ups": [],
                "program": self.program1.name,
                "program_id": encode_id_base64(self.program1.id, "Program"),
                "last_modified_date": self.payment_plan1.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "last_modified_by": None,
            },
        )

    def test_list_payment_plans_no_program(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_LIST, Permissions.PAYMENT_VIEW_LIST_NO_GPF],
            self.business_area,
            self.program1,
        )
        response = self.client.get(self.url, **self.headers_no_program)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()["results"]
        self.assertEqual(len(response_json), 1)
        self.assertEqual(response_json[0]["unicef_id"], self.payment_plan1.unicef_id)

        self.update_user_partner_perm_for_program(self.user, self.business_area, self.program2)
        response = self.client.get(self.url, **self.headers_no_program)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()["results"]
        self.assertEqual(len(response_json), 2)
        self.assertIn(self.payment_plan1.unicef_id, [response_json[0]["unicef_id"], response_json[1]["unicef_id"]])
        self.assertIn(self.payment_plan2.unicef_id, [response_json[0]["unicef_id"], response_json[1]["unicef_id"]])
        self.assertNotIn(self.payment_plan3.unicef_id, [response_json[0]["unicef_id"], response_json[1]["unicef_id"]])

    def test_list_payment_plans_last_modified_data(self) -> None:
        approval_process = ApprovalProcessFactory(
            payment_plan=self.payment_plan1,
            sent_for_approval_date=timezone.datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            sent_for_approval_by=self.user,
        )
        approval_approval = ApprovalFactory(approval_process=approval_process, type=Approval.APPROVAL)
        approval_authorization = ApprovalFactory(approval_process=approval_process, type=Approval.AUTHORIZATION)
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_LIST, Permissions.PAYMENT_VIEW_LIST_NO_GPF],
            self.business_area,
            self.program1,
        )
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()["results"]
        self.assertEqual(len(response_json), 1)
        self.assertEqual(
            response_json[0]["last_modified_date"],
            approval_process.sent_for_approval_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        self.assertEqual(response_json[0]["last_modified_by"], approval_process.sent_for_approval_by.username)

        self.payment_plan1.status = PaymentPlan.Status.IN_AUTHORIZATION
        self.payment_plan1.save()
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()["results"]
        self.assertEqual(len(response_json), 1)
        self.assertEqual(
            response_json[0]["last_modified_date"], approval_approval.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        )
        self.assertEqual(response_json[0]["last_modified_by"], approval_approval.created_by.username)

        self.payment_plan1.status = PaymentPlan.Status.IN_REVIEW
        self.payment_plan1.save()
        response = self.client.get(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()["results"]
        self.assertEqual(len(response_json), 1)
        self.assertEqual(
            response_json[0]["last_modified_date"],
            approval_authorization.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        )
        self.assertEqual(response_json[0]["last_modified_by"], approval_authorization.created_by.username)

    def _bulk_approve_action_response(self) -> Any:
        ApprovalProcessFactory(payment_plan=self.payment_plan1)
        ApprovalProcessFactory(payment_plan=self.payment_plan2)
        response = self.client.post(
            reverse("payments:payment-plan-bulk-action"),
            data={
                "ids": [
                    encode_id_base64(self.payment_plan1.id, "PaymentPlan"),
                    encode_id_base64(self.payment_plan2.id, "PaymentPlan"),
                ],
                "action": PaymentPlan.Action.APPROVE.value,
                "comment": "Test comment",
            },
            **self.headers_no_program,
        )
        return response

    def test_bulk_action(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [
                Permissions.PM_VIEW_LIST,
                Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
                Permissions.PAYMENT_VIEW_LIST_NO_GPF,
            ],
            self.business_area,
            self.program1,
        )
        self.update_user_partner_perm_for_program(self.user, self.business_area, self.program2)
        response = self._bulk_approve_action_response()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.payment_plan1.refresh_from_db()
        self.payment_plan2.refresh_from_db()
        self.assertEqual(self.payment_plan1.status, PaymentPlan.Status.IN_AUTHORIZATION)
        self.assertEqual(self.payment_plan2.status, PaymentPlan.Status.IN_AUTHORIZATION)

    def test_bulk_action_no_approve_permissions(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_LIST, Permissions.PAYMENT_VIEW_LIST_NO_GPF],
            self.business_area,
            self.program1,
        )
        self.update_user_partner_perm_for_program(self.user, self.business_area, self.program2)
        response = self._bulk_approve_action_response()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.payment_plan1.refresh_from_db()
        self.payment_plan2.refresh_from_db()
        self.assertEqual(self.payment_plan1.status, PaymentPlan.Status.IN_APPROVAL)
        self.assertEqual(self.payment_plan2.status, PaymentPlan.Status.IN_APPROVAL)
