from typing import Any, Dict, List, Optional

from django.core.management import call_command
from django.urls import reverse

import pytest
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from rest_framework import status

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db()


class TestGrievanceCreateComplaintTicket:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        call_command("loadcountries")
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner, first_name="TestUser")
        self.user2 = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.program = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="program afghanistan 1",
        )

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        self.admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")

        self.household, self.individuals = create_household(
            {"size": 1, "business_area": self.afghanistan},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )
        self.household2, self.individuals2 = create_household(
            {"size": 1, "business_area": self.afghanistan},
            {"given_name": "John222", "family_name": "Doe222", "middle_name": "", "full_name": "John Doe222"},
        )

        payment_plan = PaymentPlanFactory(program_cycle=self.program.cycles.first(), business_area=self.afghanistan)
        self.payment = PaymentFactory(
            household=self.household,
            collector=self.individuals[0],
            business_area=self.afghanistan,
            parent=payment_plan,
            currency="PLN",
        )
        self.second_payment = PaymentFactory(
            household=self.household2,
            collector=self.individuals2[0],
            business_area=self.afghanistan,
            parent=payment_plan,
            currency="PLN",
        )

        self.list_url = reverse(
            "api:grievance-tickets:grievance-tickets-global-list",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )

    def _prepare_input(
        self,
        household: Optional[str] = None,
        individual: Optional[str] = None,
        payment_records: Optional[List[Optional[str]]] = None,
    ) -> Dict:
        return {
            "description": "Test Feedback",
            "assigned_to": str(self.user.id),
            "category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            "issue_type": GrievanceTicket.ISSUE_TYPE_FSP_COMPLAINT,
            "admin": str(self.admin_area.id),
            "language": "Polish, English",
            "consent": True,
            "extras": {
                "category": {
                    "grievance_complaint_ticket_extras": {
                        "household": household,
                        "individual": individual,
                        "payment_record": payment_records,
                    }
                }
            },
        }

    def test_create_complaint_ticket(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        input_data = self._prepare_input(
            household=str(self.household.id),
            individual=str(self.individuals[0].id),
            payment_records=[str(self.payment.id)],
        )

        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()[0]

    def test_create_complaint_ticket_without_payment_record(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        input_data = self._prepare_input(
            household=str(self.household.id),
            individual=str(self.individuals[0].id),
            payment_records=[],
        )
        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()[0]

    def test_create_complaint_ticket_with_two_payment_records(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        input_data = self._prepare_input(
            household=str(self.household.id),
            individual=str(self.individuals[0].id),
            payment_records=[
                str(self.payment.id),
                str(self.second_payment.id),
            ],
        )
        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()[0]

    def test_create_complaint_ticket_without_household(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        input_data = self._prepare_input(
            individual=str(self.individuals[0].id),
            payment_records=[str(self.payment.id)],
        )
        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()[0]

    def test_create_complaint_ticket_without_individual(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        input_data = self._prepare_input(
            household=str(self.household.id),
            payment_records=[str(self.payment.id)],
        )
        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()[0]

    def test_create_complaint_ticket_without_extras(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        input_data = self._prepare_input(payment_records=[])
        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.json()[0]
