from typing import Any, List

from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    SensitiveGrievanceTicketWithoutExtrasFactory,
)
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import GrievanceTicket
from hope.models import Payment, PaymentPlan, Program

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


class TestPaymentOfficeSearch:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.global_url_name = "api:payments:payments-global-list"
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.cycle = self.program.cycles.first()

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        # Create first payment plan with household and individuals
        self.payment_plan1 = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.ACCEPTED,
        )

        self.household1, self.individuals1 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.household1_2, self.individuals1_2 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}],
        )

        self.payment_plan2 = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.ACCEPTED,
        )
        self.household2, self.individuals2 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.payment_plan3 = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.cycle,
            status=PaymentPlan.Status.ACCEPTED,
        )
        self.household3, self.individuals3 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.payment1 = PaymentFactory(
            parent=self.payment_plan1,
            household=self.household1,
            head_of_household=self.individuals1[0],
            program=self.program,
            status=Payment.STATUS_SUCCESS,
        )
        self.payment1_second = PaymentFactory(
            parent=self.payment_plan1,
            household=self.household1_2,
            head_of_household=self.individuals1_2[0],
            program=self.program,
            status=Payment.STATUS_SUCCESS,
        )
        self.payment2 = PaymentFactory(
            parent=self.payment_plan2,
            household=self.household2,
            head_of_household=self.individuals2[0],
            program=self.program,
            status=Payment.STATUS_PENDING,
        )
        self.payment3 = PaymentFactory(
            parent=self.payment_plan3,
            household=self.household3,
            head_of_household=self.individuals3[0],
            program=self.program,
            status=Payment.STATUS_SUCCESS,
        )

    def test_search_by_payment_unicef_id(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.payment1.unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.payment1.id)

    def test_search_by_household_unicef_id(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.household2.unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.payment2.id)

    def test_search_by_individual_unicef_id(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.individuals3[0].unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.payment3.id)

    def test_search_by_payment_plan_unicef_id(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )

        self.payment_plan1.refresh_from_db()
        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": self.payment_plan1.unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        result_ids = [result["id"] for result in response.data["results"]]
        assert str(self.payment1.id) in result_ids
        assert str(self.payment1_second.id) in result_ids

    def test_search_by_grievance_unicef_id(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )

        ticket = GrievanceTicketFactory(
            business_area=self.afghanistan,
            category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
        )

        SensitiveGrievanceTicketWithoutExtrasFactory(
            ticket=ticket,
            payment=self.payment2,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": ticket.unicef_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.payment2.id)

    def test_search_by_phone_number(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Update individual with phone number
        self.individuals1[0].phone_no = "+1234567890"
        self.individuals1[0].save()

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": "+1234567890"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.payment1.id)

    def test_search_by_phone_number_alternative(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Update individual with alternative phone number
        self.individuals2[0].phone_no_alternative = "+9876543210"
        self.individuals2[0].save()

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": "+9876543210"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.payment2.id)

    def test_search_by_individual_name(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Update individual with specific name
        self.individuals3[0].full_name = "UniqueCharliePay"
        self.individuals3[0].save()

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": "UniqueCharliePay"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.payment3.id)

    def test_search_with_active_programs_filter(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_DETAILS],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )

        finished_program = ProgramFactory(business_area=self.afghanistan, status=Program.FINISHED)
        finished_cycle = finished_program.cycles.first()
        finished_payment_plan = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=finished_cycle,
            status=PaymentPlan.Status.ACCEPTED,
        )
        finished_household, finished_individuals = create_household_and_individuals(
            household_data={
                "program": finished_program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}],
        )
        payment_finished = PaymentFactory(
            parent=finished_payment_plan,
            household=finished_household,
            head_of_household=finished_individuals[0],
            program=finished_program,
            status=Payment.STATUS_SUCCESS,
        )

        # Set same phone number for both active and finished program individuals
        self.individuals1[0].phone_no = "+5555556666"
        self.individuals1[0].save()

        finished_individuals[0].phone_no = "+5555556666"
        finished_individuals[0].save()

        # First, search WITHOUT active_programs filter - should return both payments
        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": "+5555556666", "active_programs_only": "false"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        result_ids = [result["id"] for result in response.data["results"]]
        assert str(self.payment1.id) in result_ids
        assert str(payment_finished.id) in result_ids

        # Now search WITH active_programs_only=true filter - should only return active program payment
        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            ),
            {"office_search": "+5555556666", "active_programs_only": "true"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.payment1.id)
