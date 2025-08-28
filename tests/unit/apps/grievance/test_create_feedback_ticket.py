from typing import Any

import pytest
from django.core.management import call_command
from django.urls import reverse
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.program import ProgramFactory
from rest_framework import status

from hope.apps.account.permissions import Permissions
from hope.models import country as geo_models
from hope.apps.grievance.models import GrievanceTicket
from hope.models.program import Program

pytestmark = pytest.mark.django_db()


class TestGrievanceCreateFeedbackTicket:
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
        self.list_url = reverse(
            "api:grievance-tickets:grievance-tickets-global-list",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )

    def test_create_negative_feedback_ticket_not_supported(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        input_data = {
            "description": "Test Feedback AaaaQwooL",
            "assigned_to": str(self.user.id),
            "category": GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            "admin": str(self.admin_area.id),
            "language": "Polish, English",
            "consent": True,
        }

        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Feedback tickets are not allowed to be created through this mutation." in response.json()

    def test_create_positive_feedback_ticket_not_supported(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)

        input_data = {
            "description": "Test Feedback AaaaQwooL",
            "assigned_to": str(self.user.id),
            "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            "admin": str(self.admin_area.id),
            "language": "Polish, English",
            "consent": True,
        }

        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Feedback tickets are not allowed to be created through this mutation." in response.json()
