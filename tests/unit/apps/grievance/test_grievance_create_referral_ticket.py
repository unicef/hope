from typing import Any, Dict, Optional

from django.core.management import call_command
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.core.models import BusinessArea
from hope.apps.geo import models as geo_models
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db()


class TestGrievanceCreateReferralTicket:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        call_command("loadcountries")
        self.business_area = create_afghanistan()
        partner = PartnerFactory(name="Partner")
        self.user = UserFactory.create(partner=partner)
        self.api_client = api_client(self.user)
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        self.program = ProgramFactory(status=Program.ACTIVE, business_area=self.business_area)
        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        self.admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")

        self.household, self.individuals = create_household(
            {"size": 1, "business_area": self.business_area},
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe",
            },
        )
        self.list_url = reverse(
            "api:grievance-tickets:grievance-tickets-global-list",
            kwargs={"business_area_slug": self.business_area.slug},
        )

    def _prepare_input(self, extras: Optional[Dict] = None) -> Dict:
        input_data = {
            "description": "Test Feedback",
            "assigned_to": str(self.user.id),
            "category": GrievanceTicket.CATEGORY_REFERRAL,
            "admin": str(self.admin_area.id),
            "language": "Polish, English",
            "consent": True,
            "business_area": "afghanistan",
        }

        if extras:
            input_data["extras"] = {"category": {"referral_ticket_extras": extras}}

        return input_data

    def test_create_referral_ticket_without_extras(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.business_area, self.program)

        input_data = self._prepare_input()

        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_referral_ticket_with_household_extras(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.business_area, self.program)

        extras = {
            "household": str(self.household.id),
        }
        input_data = self._prepare_input(extras)

        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()[0]["household"]["unicef_id"] == self.household.unicef_id
        assert response.json()[0]["individual"] is None

    def test_create_referral_ticket_with_individual_extras(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.business_area, self.program)

        extras = {
            "individual": str(self.individuals[0].id),
        }
        input_data = self._prepare_input(extras)

        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()[0]["individual"]["unicef_id"] == self.individuals[0].unicef_id
        assert response.json()[0]["household"] is None

    def test_create_referral_ticket_with_household_and_individual_extras(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.business_area, self.program)

        extras = {
            "household": str(self.household.id),
            "individual": str(self.individuals[0].id),
        }
        input_data = self._prepare_input(extras)

        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()[0]["individual"]["unicef_id"] == self.individuals[0].unicef_id
        assert response.json()[0]["household"]["unicef_id"] == self.household.unicef_id
