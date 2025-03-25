import json
from typing import Any, Callable

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.utils import encode_id_base64, encode_id_base64_required
from hct_mis_api.apps.payment.api.views import PaymentPlanManagerialViewSet
from hct_mis_api.apps.payment.fixtures import (
    ApprovalFactory,
    ApprovalProcessFactory,
    PaymentPlanFactory,
)
from hct_mis_api.apps.payment.models import Approval, PaymentPlan
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program

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
            "api:payments:payment-plans-managerial-list", kwargs={"business_area_slug": self.afghanistan.slug}
        )

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([], status.HTTP_403_FORBIDDEN),
            ([Permissions.PAYMENT_VIEW_LIST_MANAGERIAL], status.HTTP_200_OK),
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
        create_partner_role_with_permissions: Callable,
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
            [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
            self.afghanistan,
            program=self.program1,
        )
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()["results"]
        assert len(response_json) == 1
        assert response_json[0]["unicef_id"] == self.payment_plan1.unicef_id

        create_partner_role_with_permissions(
            self.partner,
            [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
            self.afghanistan,
            program=self.program2,
        )

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()["results"]
        assert len(response_json) == 2

        with CaptureQueriesContext(connection) as ctx:
            response = _test_list()
            etag = response.headers["etag"]

            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 12

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
            [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
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
                "api:payments:payment-plans-managerial-bulk-action",
                kwargs={"business_area_slug": self.afghanistan.slug},
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
        create_partner_role_with_permissions: Callable,
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
        create_partner_role_with_permissions(
            self.partner,
            [
                Permissions.PM_VIEW_LIST,
                Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
                Permissions.PAYMENT_VIEW_LIST_MANAGERIAL,
            ],
            self.afghanistan,
            self.program2,
        )
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
        create_partner_role_with_permissions: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
            self.afghanistan,
            self.program1,
        )
        create_partner_role_with_permissions(
            self.partner,
            [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL],
            self.afghanistan,
            self.program2,
        )
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


class TestPaymentPlanList:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner)
        self.program_active = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.cycle = self.program_active.cycles.first()
        self.pp = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.IN_APPROVAL,
            created_by=self.user,
        )
        # add TP
        self.tp = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.TP_OPEN,
            created_by=self.user,
        )
        self.pp_list_url = reverse(
            "api:payments:payment-plans-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program_active.slug},
        )
        self.pp_count_url = reverse(
            "api:payments:payment-plans-count",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program_active.slug},
        )
        self.client = api_client(self.user)

    def test_payment_plan_list_without_permissions(
        self,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            self.afghanistan,
            self.program_active,
        )
        response = self.client.get(self.pp_list_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        "permissions",
        [
            [Permissions.PM_VIEW_LIST],
        ],
    )
    def test_payment_plan_list_with_permissions(
        self,
        permissions: list,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            permissions,
            self.afghanistan,
            self.program_active,
        )
        response = self.client.get(self.pp_list_url)
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1

        response_count = self.client.get(self.pp_count_url)
        assert response_count.status_code == status.HTTP_200_OK
        assert response_count.json()["count"] == 1

        self.pp.refresh_from_db()
        payment_plan = response_data[0]
        assert encode_id_base64_required(self.pp.id, "PaymentPlan") == payment_plan["id"]
        assert payment_plan["unicef_id"] == self.pp.unicef_id
        assert payment_plan["name"] == self.pp.name
        assert payment_plan["status"] == self.pp.get_status_display()
        assert payment_plan["total_households_count"] == self.pp.total_households_count
        assert payment_plan["currency"] == self.pp.get_currency_display()
        assert payment_plan["excluded_ids"] == self.pp.excluded_ids
        assert payment_plan["total_entitled_quantity"] == str(self.pp.total_entitled_quantity)
        assert payment_plan["total_delivered_quantity"] == str(self.pp.total_delivered_quantity)
        assert payment_plan["total_undelivered_quantity"] == str(self.pp.total_undelivered_quantity)
        assert payment_plan["dispersion_start_date"] == self.pp.dispersion_start_date.strftime("%Y-%m-%d")
        assert payment_plan["dispersion_end_date"] == self.pp.dispersion_end_date.strftime("%Y-%m-%d")
        assert payment_plan["is_follow_up"] == self.pp.is_follow_up
        assert payment_plan["follow_ups"] == []

    def test_payment_plan_caching(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_LIST],
            self.afghanistan,
            self.program_active,
        )
        # first api call no cache
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.pp_list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(response.json()["results"]) == 1
            assert len(ctx.captured_queries) == 23

        # second call get from cache
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.pp_list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_second_call = response.headers["etag"]
            assert etag == etag_second_call
            assert len(ctx.captured_queries) == 14
        # upd PP
        self.pp.status = PaymentPlan.Status.IN_REVIEW
        self.pp.save()
        # PaymentPlan updated, invalidate cache... new call
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.pp_list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            new_etag = response.headers["etag"]
            assert json.loads(cache.get(new_etag)[0].decode("utf8")) == response.json()
            assert len(response.json()["results"]) == 1
            assert len(ctx.captured_queries) == 17
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.pp_list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_second_call = response.headers["etag"]
            assert new_etag == etag_second_call
            assert len(ctx.captured_queries) == 14
        # add new PP cache invalidate... new call
        PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.OPEN,
            created_by=self.user,
        )
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.pp_list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(response.json()["results"]) == 2
            assert len(ctx.captured_queries) == 19
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.pp_list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_second_call = response.headers["etag"]
            assert etag == etag_second_call
            assert len(ctx.captured_queries) == 14

        # delete PP
        self.pp.delete()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.pp_list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(response.json()["results"]) == 1
            assert len(ctx.captured_queries) == 17
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.pp_list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            last_etag_second_call = response.headers["etag"]
            assert etag == last_etag_second_call
            assert len(ctx.captured_queries) == 14

        # upd TP no changes in cache
        self.tp.status = PaymentPlan.Status.TP_LOCKED
        self.tp.save()
        # cache will update because in TargetPopulationListKeyBit query set getting all PPs
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.pp_list_url)
            assert response.status_code == status.HTTP_200_OK
            assert len(response.json()["results"]) == 1
            assert response.has_header("etag")
            get_etag = response.headers["etag"]
            assert get_etag != last_etag_second_call
            assert len(ctx.captured_queries) == 17


class TestPaymentPlanDetail:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner)
        self.program_active = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.cycle = self.program_active.cycles.first()
        self.pp = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.IN_APPROVAL,
            created_by=self.user,
        )
        pp_id = encode_id_base64_required(self.pp.id, "PaymentPlan")
        self.pp_detail_url = reverse(
            "api:payments:payment-plans-detail",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program_active.slug, "pk": pp_id},
        )
        self.client = api_client(self.user)

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PM_VIEW_DETAILS], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_payment_plan_detail_permissions(
        self, permissions: list, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)

        response = self.client.get(self.pp_detail_url)
        assert response.status_code == expected_status

    def test_payment_plan_detail(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.PM_VIEW_DETAILS], self.afghanistan, self.program_active
        )
        response = self.client.get(self.pp_detail_url)
        assert response.status_code == status.HTTP_200_OK

        payment_plan = response.json()
        self.pp.refresh_from_db()

        assert payment_plan["id"] == encode_id_base64_required(self.pp.id, "PaymentPlan")
        assert payment_plan["unicef_id"] == self.pp.unicef_id
        assert payment_plan["name"] == self.pp.name
        assert payment_plan["status"] == self.pp.get_status_display()
        assert payment_plan["total_households_count"] == self.pp.total_households_count
        assert payment_plan["currency"] == self.pp.get_currency_display()
        assert payment_plan["excluded_ids"] == self.pp.excluded_ids
        assert payment_plan["total_entitled_quantity"] == str(self.pp.total_entitled_quantity)
        assert payment_plan["total_delivered_quantity"] == str(self.pp.total_delivered_quantity)
        assert payment_plan["total_undelivered_quantity"] == str(self.pp.total_undelivered_quantity)
        assert payment_plan["dispersion_start_date"] == self.pp.dispersion_start_date.strftime("%Y-%m-%d")
        assert payment_plan["dispersion_end_date"] == self.pp.dispersion_end_date.strftime("%Y-%m-%d")
        assert payment_plan["is_follow_up"] == self.pp.is_follow_up
        assert payment_plan["follow_ups"] == []
        assert payment_plan["created_by"] == f"{self.user.first_name} {self.user.last_name}"
        assert payment_plan["background_action_status"] is None
        assert payment_plan["start_date"] is None
        assert payment_plan["program"] == self.program_active.name
        assert payment_plan["has_payment_list_export_file"] is False
        assert payment_plan["has_fsp_delivery_mechanism_xlsx_template"] is False
        assert payment_plan["imported_file_name"] == ""
        assert payment_plan["payments_conflicts_count"] == 0
        assert payment_plan["delivery_mechanisms"] == []
        assert payment_plan["bank_reconciliation_success"] == 0
        assert payment_plan["bank_reconciliation_error"] == 0
        assert payment_plan["can_create_payment_verification_plan"] is False
        assert payment_plan["available_payment_records_count"] == 0
        assert payment_plan["can_create_follow_up"] is False
        assert payment_plan["total_withdrawn_households_count"] == 0
        assert payment_plan["unsuccessful_payments_count"] == 0
        assert payment_plan["can_send_to_payment_gateway"] is False
        assert payment_plan["can_split"] is False
        assert payment_plan["total_households_count_with_valid_phone_no"] == 0
        assert payment_plan["can_create_xlsx_with_fsp_auth_code"] is False
        assert payment_plan["fsp_communication_channel"] == "XLSX"
        assert payment_plan["can_export_xlsx"] is False
        assert payment_plan["can_download_xlsx"] is False
        assert payment_plan["can_send_xlsx_password"] is False


class TestPaymentPlanFilter:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any, create_user_role_with_permissions: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner)
        self.program_active = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.cycle = self.program_active.cycles.first()
        self.pp = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.IN_APPROVAL,
            created_by=self.user,
        )
        self.pp_finished = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.FINISHED,
            created_by=self.user,
        )
        self.list_url = reverse(
            "api:payments:payment-plans-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program_active.slug},
        )
        self.partner = PartnerFactory(name="ABC")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)
        create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_LIST],
            self.afghanistan,
            self.program_active,
        )

    def test_filter_by_status(self) -> None:
        response = self.client.get(self.list_url, {"status": PaymentPlan.Status.FINISHED.value})
        self.pp_finished.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == encode_id_base64_required(self.pp_finished.id, "PaymentPlan")
        assert response_data[0]["status"] == "Finished"
        assert response_data[0]["name"] == self.pp_finished.name

        response = self.client.get(self.list_url, {"status": PaymentPlan.Status.IN_APPROVAL.value})
        self.pp.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == encode_id_base64_required(self.pp.id, "PaymentPlan")
        assert response_data[0]["status"] == "In Approval"
        assert response_data[0]["name"] == self.pp.name

    def test_filter_by_program_cycle(self) -> None:
        new_pp = PaymentPlanFactory(
            name="TEST_ABC_123",
            business_area=self.afghanistan,
            program_cycle=ProgramCycleFactory(program=self.program_active),
            status=PaymentPlan.Status.ACCEPTED,
            created_by=self.user,
        )
        response = self.client.get(
            self.list_url, {"program_cycle": encode_id_base64_required(new_pp.program_cycle.id, "ProgramCycle")}
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["name"] == "TEST_ABC_123"
        assert response_data[0]["status"] == "Accepted"

    def test_filter_by_search(self) -> None:
        new_pp = PaymentPlanFactory(
            name="TEST_ABC_999",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.ACCEPTED,
            created_by=self.user,
        )
        new_pp.refresh_from_db()
        # name
        response = self.client.get(self.list_url, {"search": "TEST_ABC"})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["name"] == "TEST_ABC_999"
        assert response_data[0]["status"] == "Accepted"
        # id
        response = self.client.get(self.list_url, {"search": str(new_pp.id)})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["name"] == "TEST_ABC_999"
        # unicef_id
        response = self.client.get(self.list_url, {"search": new_pp.unicef_id})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["name"] == "TEST_ABC_999"

    def test_filter_by_entitled_quantity(self) -> None:
        PaymentPlanFactory(
            name="PP_1",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.LOCKED_FSP,
            created_by=self.user,
            total_entitled_quantity=100,
        )
        PaymentPlanFactory(
            name="PP_2",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.LOCKED_FSP,
            created_by=self.user,
            total_entitled_quantity=200,
        )
        response = self.client.get(
            self.list_url, {"total_entitled_quantity__gte": "99", "total_entitled_quantity__lte": 201}
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 2
        assert response_data[0]["name"] == "PP_1"
        assert response_data[1]["name"] == "PP_2"

        response = self.client.get(self.list_url, {"total_entitled_quantity__lte": 101})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["name"] == "PP_1"

    def test_filter_by_dispersion_date(self) -> None:
        PaymentPlanFactory(
            name="PP_abc",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.LOCKED_FSP,
            created_by=self.user,
            dispersion_start_date="2022-02-24",
            dispersion_end_date="2022-03-03",
        )
        PaymentPlanFactory(
            name="PP_xyz",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.LOCKED_FSP,
            created_by=self.user,
            dispersion_start_date="2022-01-01",
            dispersion_end_date="2022-01-17",
        )
        response = self.client.get(
            self.list_url, {"dispersion_start_date__gte": "2022-02-23", "dispersion_end_date__lte": "2022-03-04"}
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["name"] == "PP_abc"

        response = self.client.get(self.list_url, {"dispersion_end_date__lte": "2022-01-18"})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["name"] == "PP_xyz"

    def test_filter_by_is_follow_up(self) -> None:
        PaymentPlanFactory(
            name="NEW_FOLLOW_up",
            is_follow_up=True,
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.OPEN,
            created_by=self.user,
        )
        response = self.client.get(self.list_url, {"is_follow_up": True})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["name"] == "NEW_FOLLOW_up"


class TestTargetPopulationList:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner)
        self.program_active = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.cycle = self.program_active.cycles.first()
        self.tp = PaymentPlanFactory(
            name="Test new TP",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.TP_OPEN,
            created_by=self.user,
        )
        # add PaymentPlan
        self.pp = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.LOCKED_FSP,
            created_by=self.user,
        )
        self.tp_list_url = reverse(
            "api:payments:target-populations-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program_active.slug},
        )
        self.tp_count_url = reverse(
            "api:payments:target-populations-count",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program_active.slug},
        )
        self.client = api_client(self.user)

    def test_target_population_list_without_permissions(
        self,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PM_ACCEPTANCE_PROCESS_APPROVE],
            self.afghanistan,
            self.program_active,
        )
        response = self.client.get(self.tp_list_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        "permissions",
        [
            [Permissions.TARGETING_VIEW_LIST],
        ],
    )
    def test_target_population_list_with_permissions(
        self,
        permissions: list,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            permissions,
            self.afghanistan,
            self.program_active,
        )
        response = self.client.get(self.tp_list_url)
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 2

        response_count = self.client.get(self.tp_count_url)
        assert response_count.status_code == status.HTTP_200_OK
        assert response_count.json()["count"] == 2

        self.tp.refresh_from_db()
        tp = response_data[0]
        assert encode_id_base64_required(self.tp.id, "PaymentPlan") == tp["id"]
        assert tp["name"] == "Test new TP"
        assert tp["status"] == self.tp.get_status_display()
        assert tp["total_households_count"] == self.tp.total_households_count
        assert tp["total_individuals_count"] == self.tp.total_individuals_count
        assert tp["created_at"] == self.tp.created_at.isoformat().replace("+00:00", "Z")
        assert tp["updated_at"] == self.tp.updated_at.isoformat().replace("+00:00", "Z")
        assert tp["created_by"] == self.user.get_full_name()

    def test_target_population_caching(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.TARGETING_VIEW_LIST],
            self.afghanistan,
            self.program_active,
        )
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.tp_list_url)
            assert response.status_code == status.HTTP_200_OK

            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 35

        # Test that reoccurring requests use cached data
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.tp_list_url)
            assert response.status_code == status.HTTP_200_OK

            etag_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 14
            assert etag_second_call == etag

        # After update, it does not use the cached data
        self.tp.status = PaymentPlan.Status.TP_PROCESSING
        self.tp.save()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.tp_list_url)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 29

            assert etag_call_after_update != etag

        # Cached data again
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.tp_list_url)
            assert response.status_code == status.HTTP_200_OK

            etag_call_after_update_second_call = response.headers["etag"]
            assert json.loads(cache.get(response.headers["etag"])[0].decode("utf8")) == response.json()
            assert len(ctx.captured_queries) == 14
            assert etag_call_after_update_second_call == etag_call_after_update


class TestTargetPopulationDetail:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner)
        self.program_active = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.cycle = self.program_active.cycles.first()
        self.tp = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.TP_LOCKED,
            created_by=self.user,
        )
        tp_id = encode_id_base64_required(self.tp.id, "PaymentPlan")
        self.tp_detail_url = reverse(
            "api:payments:target-populations-detail",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program_active.slug, "pk": tp_id},
        )
        self.client = api_client(self.user)

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.TARGETING_VIEW_DETAILS], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_target_population_detail_permissions(
        self, permissions: list, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)

        response = self.client.get(self.tp_detail_url)
        assert response.status_code == expected_status

    def test_target_population_detail(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.TARGETING_VIEW_DETAILS], self.afghanistan, self.program_active
        )
        response = self.client.get(self.tp_detail_url)
        assert response.status_code == status.HTTP_200_OK

        tp = response.json()
        self.tp.refresh_from_db()

        assert tp["id"] == encode_id_base64_required(self.tp.id, "PaymentPlan")
        assert tp["name"] == self.tp.name
        assert tp["program_cycle"] == self.cycle.title
        assert tp["program"] == self.program_active.name
        assert tp["status"] == self.tp.get_status_display()
        assert tp["total_households_count"] == self.tp.total_households_count
        assert tp["total_individuals_count"] == self.tp.total_individuals_count
        assert tp["created_by"] == f"{self.user.first_name} {self.user.last_name}"
        assert tp["background_action_status"] is None
        assert tp["male_children_count"] == self.tp.male_children_count
        assert tp["female_children_count"] == self.tp.female_children_count
        assert tp["male_adults_count"] == self.tp.male_adults_count
        assert tp["female_adults_count"] == self.tp.female_adults_count


class TestTargetPopulationFilter:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any, create_user_role_with_permissions: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner)
        self.program_active = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.cycle = self.program_active.cycles.first()
        self.tp = PaymentPlanFactory(
            name="OPEN",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.TP_OPEN,
            created_by=self.user,
            total_households_count=999,
        )
        self.tp_locked = PaymentPlanFactory(
            name="LOCKED",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.TP_LOCKED,
            created_by=self.user,
            total_households_count=888,
        )
        self.tp_assigned = PaymentPlanFactory(
            name="Assigned TP",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.FINISHED,
            created_by=self.user,
            total_households_count=777,
        )
        self.list_url = reverse(
            "api:payments:target-populations-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program_active.slug},
        )
        self.partner = PartnerFactory(name="ABC")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)
        create_user_role_with_permissions(
            self.user,
            [Permissions.TARGETING_VIEW_LIST],
            self.afghanistan,
            self.program_active,
        )

    def test_filter_by_status(self) -> None:
        response = self.client.get(self.list_url, {"status": PaymentPlan.Status.TP_LOCKED.value})
        self.tp_locked.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == encode_id_base64_required(self.tp_locked.id, "PaymentPlan")
        assert response_data[0]["status"] == "Locked"
        assert response_data[0]["name"] == "LOCKED"

        response = self.client.get(self.list_url, {"status": "ASSIGNED"})
        self.tp_assigned.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == encode_id_base64_required(self.tp_assigned.id, "PaymentPlan")
        assert response_data[0]["name"] == "Assigned TP"

    def test_filter_by_program_cycle(self) -> None:
        new_tp = PaymentPlanFactory(
            name="TEST_ABC_QWOOL",
            business_area=self.afghanistan,
            program_cycle=ProgramCycleFactory(program=self.program_active),
            status=PaymentPlan.Status.TP_STEFICON_RUN,
            created_by=self.user,
        )
        response = self.client.get(
            self.list_url, {"program_cycle": encode_id_base64_required(new_tp.program_cycle.id, "ProgramCycle")}
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["name"] == "TEST_ABC_QWOOL"
        assert response_data[0]["status"] == "Steficon Run"

    def test_filter_by_number_of_hh(self) -> None:
        PaymentPlanFactory(
            name="PP_1",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.TP_LOCKED,
            created_by=self.user,
            total_households_count=100,
        )
        PaymentPlanFactory(
            name="PP_2",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.TP_LOCKED,
            created_by=self.user,
            total_households_count=200,
        )
        response = self.client.get(
            self.list_url, {"total_households_count__gte": "99", "total_households_count__lte": 201}
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 2
        assert response_data[0]["name"] == "PP_1"
        assert response_data[1]["name"] == "PP_2"

        response = self.client.get(self.list_url, {"total_households_count__lte": 101})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["name"] == "PP_1"

    def test_filter_by_created_date(self) -> None:
        tp_1 = PaymentPlanFactory(
            name="TP_Mmmmmmm",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.LOCKED_FSP,
            created_by=self.user,
            created_at="2022-02-24",
        )
        tp_2 = PaymentPlanFactory(
            name="TP_Uuuuu_Aaaaa",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.LOCKED_FSP,
            created_by=self.user,
            created_at="2022-01-01",
        )
        tp_1.created_at = "2022-02-24"
        tp_1.save()
        tp_2.created_at = "2022-01-01"
        tp_2.save()
        response = self.client.get(self.list_url, {"created_at__gte": "2022-02-23", "created_at__lte": "2022-03-04"})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["name"] == "TP_Mmmmmmm"

        response = self.client.get(self.list_url, {"created_at__lte": "2022-01-18"})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["name"] == "TP_Uuuuu_Aaaaa"
