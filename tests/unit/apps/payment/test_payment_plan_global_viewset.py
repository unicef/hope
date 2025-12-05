from typing import Any

from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan, create_ukraine
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.models import PaymentPlan, Program

pytestmark = pytest.mark.django_db


class TestPaymentPlanGlobalViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.global_url_name = "api:payments:payment-plans-global-list"
        self.global_count_url = "api:payments:payment-plans-global-count"

        self.afghanistan = create_afghanistan()
        self.ukraine = create_ukraine()

        self.program_afghanistan1 = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="Program Afghanistan 1",
        )
        self.program_afghanistan2 = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="Program Afghanistan 2",
        )
        self.program_ukraine = ProgramFactory(
            business_area=self.ukraine,
            status=Program.ACTIVE,
            name="Program Ukraine",
        )

        self.program_cycle_afghanistan1 = ProgramCycleFactory(program=self.program_afghanistan1)
        self.program_cycle_afghanistan2 = ProgramCycleFactory(program=self.program_afghanistan2)
        self.program_cycle_ukraine = ProgramCycleFactory(program=self.program_ukraine)

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.payment_plan_afghanistan1 = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.program_cycle_afghanistan1,
            status=PaymentPlan.Status.ACCEPTED,
        )
        self.payment_plan_afghanistan2 = PaymentPlanFactory(
            business_area=self.afghanistan,
            program_cycle=self.program_cycle_afghanistan2,
            status=PaymentPlan.Status.ACCEPTED,
        )
        self.payment_plan_ukraine = PaymentPlanFactory(
            business_area=self.ukraine,
            program_cycle=self.program_cycle_ukraine,
            status=PaymentPlan.Status.ACCEPTED,
        )

        self.household_afghanistan1, self.individuals_afghanistan1 = create_household_and_individuals(
            household_data={
                "program": self.program_afghanistan1,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        self.household_afghanistan2, self.individuals_afghanistan2 = create_household_and_individuals(
            household_data={
                "program": self.program_afghanistan2,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.household_ukraine, self.individuals_ukraine = create_household_and_individuals(
            household_data={
                "program": self.program_ukraine,
                "business_area": self.ukraine,
            },
            individuals_data=[{}, {}],
        )

        self.payment_afghanistan1 = PaymentFactory(
            business_area=self.afghanistan,
            parent=self.payment_plan_afghanistan1,
            household=self.household_afghanistan1,
            head_of_household=self.individuals_afghanistan1[0],
            program=self.program_afghanistan1,
        )
        self.payment_afghanistan2 = PaymentFactory(
            business_area=self.afghanistan,
            parent=self.payment_plan_afghanistan2,
            household=self.household_afghanistan2,
            head_of_household=self.individuals_afghanistan2[0],
            program=self.program_afghanistan2,
        )
        self.payment_ukraine = PaymentFactory(
            business_area=self.ukraine,
            parent=self.payment_plan_ukraine,
            household=self.household_ukraine,
            head_of_household=self.individuals_ukraine[0],
            program=self.program_ukraine,
        )

    def test_payment_plan_global_list_with_whole_business_area_access(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 2

        response_count = self.api_client.get(
            reverse(
                self.global_count_url,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response_count.status_code == status.HTTP_200_OK
        assert response_count.json()["count"] == 2

        result_ids = [result["id"] for result in response_results]
        assert str(self.payment_plan_afghanistan1.id) in result_ids
        assert str(self.payment_plan_afghanistan2.id) in result_ids
        assert str(self.payment_plan_ukraine.id) not in result_ids

    def test_payment_plan_global_list_with_permissions_in_one_program(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_LIST],
            business_area=self.afghanistan,
            program=self.program_afghanistan1,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 1

        result_ids = [result["id"] for result in response_results]
        assert str(self.payment_plan_afghanistan1.id) in result_ids
        assert str(self.payment_plan_afghanistan2.id) not in result_ids
        assert str(self.payment_plan_ukraine.id) not in result_ids

    def test_payment_plan_global_list_with_permissions_in_multiple_programs(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_LIST],
            business_area=self.afghanistan,
            program=self.program_afghanistan1,
        )
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_LIST],
            business_area=self.afghanistan,
            program=self.program_afghanistan2,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 2

        result_ids = [result["id"] for result in response_results]
        assert str(self.payment_plan_afghanistan1.id) in result_ids
        assert str(self.payment_plan_afghanistan2.id) in result_ids
        assert str(self.payment_plan_ukraine.id) not in result_ids

    @pytest.mark.parametrize(
        "permissions",
        [
            [],
            (Permissions.PROGRAMME_ACTIVATE,),
        ],
    )
    def test_payment_plan_global_list_without_permissions(
        self, permissions: list, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_payment_plan_global_count_endpoint(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )

        response = self.api_client.get(
            reverse(
                self.global_count_url,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] == 2

    def test_payment_plan_global_list_ukraine(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_LIST],
            business_area=self.ukraine,
            whole_business_area_access=True,
        )

        response = self.api_client.get(
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.ukraine.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 1

        result_ids = [result["id"] for result in response_results]
        assert str(self.payment_plan_ukraine.id) in result_ids
        assert str(self.payment_plan_afghanistan1.id) not in result_ids
        assert str(self.payment_plan_afghanistan2.id) not in result_ids


class TestPaymentPlanOfficeSearch:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.global_url_name = "api:payments:payment-plans-global-list"
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.program_cycle = ProgramCycleFactory(program=self.program)

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.household1, self.individuals1 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.household2, self.individuals2 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.household3, self.individuals3 = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.payment_plan1 = PaymentPlanFactory(
            program_cycle=self.program_cycle,
            status=PaymentPlan.Status.ACCEPTED,
        )

        self.payment_plan2 = PaymentPlanFactory(
            program_cycle=self.program_cycle,
            status=PaymentPlan.Status.ACCEPTED,
        )

        self.payment_plan3 = PaymentPlanFactory(
            program_cycle=self.program_cycle,
            status=PaymentPlan.Status.ACCEPTED,
        )

        self.payment1 = PaymentFactory(
            parent=self.payment_plan1,
            household=self.household1,
            head_of_household=self.individuals1[0],
            program=self.program,
        )

        self.payment2 = PaymentFactory(
            parent=self.payment_plan2,
            household=self.household2,
            head_of_household=self.individuals2[0],
            program=self.program,
        )

        self.payment3 = PaymentFactory(
            parent=self.payment_plan3,
            household=self.household3,
            head_of_household=self.individuals3[0],
            program=self.program,
        )

    def test_search_by_payment_plan_unicef_id(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
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
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == str(self.payment_plan1.id)

    def test_search_by_household_unicef_id(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
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
        assert response.data["results"][0]["id"] == str(self.payment_plan2.id)

    def test_search_by_individual_unicef_id(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
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
        assert response.data["results"][0]["id"] == str(self.payment_plan3.id)

    def test_search_by_payment_unicef_id(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PM_VIEW_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
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
        assert response.data["results"][0]["id"] == str(self.payment_plan1.id)
