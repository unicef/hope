from typing import Any, List

import pytest
from django.urls import reverse
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from rest_framework import status

from hope.apps.account.permissions import Permissions
from hope.models.payment import Payment
from hope.models.payment_plan import PaymentPlan
from hope.models.program import Program

pytestmark = pytest.mark.django_db


class TestPaymentGlobalViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner)
        self.program_active = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.cycle = self.program_active.cycles.first()
        self.client = api_client(self.user)

        # Use a status not in PRE_PAYMENT_PLAN_STATUSES so it appears in global list
        self.pp = PaymentPlanFactory(
            name="Payment Plan",
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.OPEN,
            created_by=self.user,
            created_at="2022-02-24",
        )
        self.payment = PaymentFactory(
            parent=self.pp,
            status=Payment.STATUS_SUCCESS,
            delivered_quantity=999,
            entitlement_quantity=112,
        )

        self.url_list_global = reverse(
            "api:payments:payments-global-list",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )
        self.url_choices_global = reverse(
            "api:payments:payments-global-choices",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PM_VIEW_DETAILS], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_global_list(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_list_global)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            resp_data = response.json()
            assert len(resp_data["results"]) == 1
            payment = resp_data["results"][0]
            assert payment["delivered_quantity"] == "999.00"
            assert payment["status"] == "Transaction Successful"

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PM_VIEW_DETAILS], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_global_choices(
        self,
        permissions: List,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, self.program_active)
        response = self.client.get(self.url_choices_global)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            data = response.json()
            assert "status_choices" in data
            assert isinstance(data["status_choices"], list)
            assert any(x.get("value") == Payment.STATUS_SUCCESS for x in data["status_choices"])  # sanity

    def test_count_endpoint(self, create_user_role_with_permissions: Any) -> None:
        """Test the count action endpoint from CountActionMixin"""
        create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_DETAILS],
            self.afghanistan,
            self.program_active,
        )

        # Create additional payment
        PaymentFactory(parent=self.pp, status=Payment.STATUS_PENDING)

        url_count = reverse(
            "api:payments:payments-global-count",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )
        response = self.client.get(url_count)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 2

    def test_ordering(self, create_user_role_with_permissions: Any) -> None:
        """Test ordering functionality from OrderingFilter"""
        create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_DETAILS],
            self.afghanistan,
            self.program_active,
        )

        # Create payments with different delivered quantities for ordering test
        PaymentFactory(parent=self.pp, delivered_quantity=100)
        PaymentFactory(parent=self.pp, delivered_quantity=500)

        # Test ordering by delivered_quantity
        response = self.client.get(f"{self.url_list_global}?ordering=delivered_quantity")
        results = response.json()["results"]
        assert len(results) == 3
        quantities = [float(r["delivered_quantity"]) for r in results]
        assert quantities == sorted(quantities)

        # Test reverse ordering
        response = self.client.get(f"{self.url_list_global}?ordering=-delivered_quantity")
        results = response.json()["results"]
        quantities = [float(r["delivered_quantity"]) for r in results]
        assert quantities == sorted(quantities, reverse=True)

    def test_excludes_pre_payment_statuses(self, create_user_role_with_permissions: Any) -> None:
        """Test that payments with pre-payment plan statuses are excluded"""
        create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_DETAILS],
            self.afghanistan,
            self.program_active,
        )

        # Create payment plan with TP_OPEN status (pre-payment status)
        pp_tp_open = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.TP_OPEN,
        )
        PaymentFactory(parent=pp_tp_open)

        response = self.client.get(self.url_list_global)
        results = response.json()["results"]
        assert len(results) == 1  # Only the original payment, not the one with TP_OPEN status
        assert str(results[0]["id"]) == str(self.payment.id)

    def test_program_filtering(self, create_user_role_with_permissions: Any) -> None:
        """Test BusinessAreaProgramsAccessMixin program filtering"""
        # Create another program the user doesn't have access to
        program_no_access = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        cycle_no_access = program_no_access.cycles.first()

        pp_no_access = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=cycle_no_access,
            status=PaymentPlan.Status.ACCEPTED,
        )
        PaymentFactory(parent=pp_no_access, program=program_no_access)

        # User only has access to self.program_active
        create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_DETAILS],
            self.afghanistan,
            self.program_active,
        )

        response = self.client.get(self.url_list_global)
        results = response.json()["results"]

        # Should only see payment from authorized program
        assert len(results) == 1
        assert str(results[0]["id"]) == str(self.payment.id)

    def test_multiple_payments(self, create_user_role_with_permissions: Any) -> None:
        """Test with multiple payments"""
        create_user_role_with_permissions(
            self.user,
            [Permissions.PM_VIEW_DETAILS],
            self.afghanistan,
            self.program_active,
        )

        # Create multiple payments
        payments = [PaymentFactory(parent=self.pp) for i in range(3)]
        response = self.client.get(self.url_list_global)
        results = response.json()["results"]
        assert len(results) == 4  # 1 original + 3 new

        # Verify all payments are returned
        payment_ids = {str(r["id"]) for r in results}
        assert str(self.payment.id) in payment_ids
        for p in payments:
            assert str(p.id) in payment_ids
