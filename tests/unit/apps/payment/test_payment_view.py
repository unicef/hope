from typing import Any, List

from django.urls import reverse

import pytest
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from rest_framework import status

from hope.apps.account.permissions import Permissions
from hope.apps.payment.models import Payment, PaymentPlan
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db


class TestPaymentViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner)
        self.program_active = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.cycle = self.program_active.cycles.first()
        self.client = api_client(self.user)
        self.pp = PaymentPlanFactory(
            name="Payment Plan",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.DRAFT,
            created_by=self.user,
            created_at="2022-02-24",
        )
        self.payment = PaymentFactory(
            parent=self.pp, status=Payment.STATUS_SUCCESS, delivered_quantity=999, entitlement_quantity=112
        )
        pp_id = self.pp.pk
        url_kwargs = {
            "business_area_slug": self.afghanistan.slug,
            "program_slug": self.program_active.slug,
            "payment_plan_id": pp_id,
        }
        url_kwargs_with_payment = {
            "business_area_slug": self.afghanistan.slug,
            "program_slug": self.program_active.slug,
            "payment_plan_id": pp_id,
            "payment_id": self.payment.pk,
        }
        self.url_list = reverse("api:payments:payments-list", kwargs=url_kwargs)
        self.url_details = reverse("api:payments:payments-detail", kwargs=url_kwargs_with_payment)
        self.url_mark_as_failed = reverse("api:payments:payments-mark-as-failed", kwargs=url_kwargs_with_payment)
        self.url_revert_mark_as_failed = reverse(
            "api:payments:payments-revert-mark-as-failed", kwargs=url_kwargs_with_payment
        )

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PM_VIEW_DETAILS], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_get_list(self, permissions: List, expected_status: int, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_list)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert len(resp_data["results"]) == 1
            payment = resp_data["results"][0]
            assert payment["delivered_quantity"] == "999.00"
            assert payment["status"] == "Transaction Successful"

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PM_VIEW_DETAILS], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_details(self, permissions: List, expected_status: int, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_details)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["delivered_quantity"] == "999.00"
            assert resp_data["status"] == "Transaction Successful"

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PM_MARK_PAYMENT_AS_FAILED], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_mark_as_failed(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_mark_as_failed)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["delivered_quantity"] == "0.00"
            assert resp_data["status"] == "Force failed"

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PM_MARK_PAYMENT_AS_FAILED], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_revert_mark_as_failed(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        self.payment.status = "Force failed"
        self.payment.save()
        response = self.client.post(
            self.url_revert_mark_as_failed, {"delivered_quantity": "111.00", "delivery_date": "2024-01-01"}
        )
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert "id" in resp_data
            assert resp_data["delivered_quantity"] == "111.00"
            assert resp_data["status"] == "Partially Distributed"
            assert resp_data["delivery_date"] == "2024-01-01T00:00:00Z"
