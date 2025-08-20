from typing import Any, Dict, Optional

import pytest
from django.core.management import call_command
from django.urls import reverse
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.grievance import ReferralTicketWithoutExtrasFactory
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.program import ProgramFactory
from rest_framework import status

from hope.apps.account.permissions import Permissions
from hope.apps.geo import models as geo_models
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db()


class TestGrievanceUpdateReferralTicket:
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
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe",
            },
        )
        self.ticket = ReferralTicketWithoutExtrasFactory(
            ticket__business_area=self.afghanistan,
            ticket__status=GrievanceTicket.STATUS_NEW,
            ticket__description="OLD description",
            ticket__language="",
        )
        self.ticket.ticket.programs.set([self.program])

        self.list_details = reverse(
            "api:grievance-tickets:grievance-tickets-global-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "pk": str(self.ticket.ticket.pk),
            },
        )

    def _prepare_input(self, extras: Optional[Dict] = None) -> Dict:
        input_data = {
            "description": "Test Feedback NEW",
            "assigned_to": str(self.user.id),
            "admin": str(self.admin_area.id),
            "language": "Polish, English, ESP",
        }

        if extras:
            input_data["extras"] = {"category": {"referral_ticket_extras": extras}}  # type: ignore

        return input_data

    def test_update_referral_ticket_without_extras(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.afghanistan, self.program)
        input_data = self._prepare_input()

        response = self.api_client.patch(self.list_details, input_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["description"] == "OLD description"
        assert response.json()["language"] == "Polish, English, ESP"
        assert response.json()["assigned_to"]["first_name"] == "TestUser"

    def test_update_referral_ticket_with_household_extras(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.afghanistan, self.program)
        extras = {
            "household": str(self.household.id),
        }
        input_data = self._prepare_input(extras)

        response = self.api_client.patch(self.list_details, input_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["household"]["id"] == str(self.household.id)

    def test_update_referral_ticket_with_individual_extras(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.afghanistan, self.program)
        extras = {
            "individual": str(self.individuals[0].id),
        }
        input_data = self._prepare_input(extras)

        response = self.api_client.patch(self.list_details, input_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["individual"]["id"] == str(self.individuals[0].id)

    def test_update_referral_ticket_with_household_and_individual_extras(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.afghanistan, self.program)
        extras = {
            "individual": str(self.individuals[0].id),
            "household": str(self.household.id),
        }
        input_data = self._prepare_input(extras)

        response = self.api_client.patch(self.list_details, input_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["individual"]["id"] == str(self.individuals[0].id)
        assert response.json()["household"]["id"] == str(self.household.id)
