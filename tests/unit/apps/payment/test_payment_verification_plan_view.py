from typing import Any, List

from django.urls import reverse

import pytest
from rest_framework import status

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.payment.fixtures import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationPlanFactory,
)
from hct_mis_api.apps.payment.models import (
    Payment,
    PaymentPlan,
    PaymentVerificationSummary,
    build_summary,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db


class TestPaymentVerificationViewSet:
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
            status=PaymentPlan.Status.FINISHED,
            created_by=self.user,
            created_at="2022-02-24",
        )
        PaymentVerificationSummary.objects.create(payment_plan=self.pp)
        build_summary(self.pp)
        self.payment = PaymentFactory(
            parent=self.pp, status=Payment.STATUS_SUCCESS, delivered_quantity=999, entitlement_quantity=112
        )
        self.pvp = PaymentVerificationPlanFactory(payment_plan=self.pp)
        url_kwargs = {
            "business_area_slug": self.afghanistan.slug,
            "program_slug": self.program_active.slug,
            "pk": str(self.pp.pk),
        }
        url_kwargs_id = {
            "business_area_slug": self.afghanistan.slug,
            "program_slug": self.program_active.slug,
            "pk": str(self.pp.pk),
            "verification_plan_id": str(self.pvp.pk),
        }
        self.url_list = reverse(
            "api:payments:payment-verifications-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program_active.slug,
            },
        )
        self.url_details = reverse("api:payments:payment-verifications-detail", kwargs=url_kwargs)
        self.url_create = reverse(
            "api:payments:payment-verifications-create-payment-verification-plan", kwargs=url_kwargs
        )
        self.url_update = reverse(
            "api:payments:payment-verifications-update-payment-verification-plan", kwargs=url_kwargs_id
        )

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PAYMENT_VERIFICATION_VIEW_LIST], status.HTTP_200_OK),
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
            pv = resp_data["results"][0]
            assert "PENDING" == pv["verification_status"]

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS], status.HTTP_200_OK),
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
            assert 1 == resp_data["available_payment_records_count"]
            assert 1 == resp_data["eligible_payments_count"]
            assert "Pending" == resp_data["payment_verification_plans"][0]["status"]
            assert "Pending" == resp_data["payment_verification_summary"]["status"]
