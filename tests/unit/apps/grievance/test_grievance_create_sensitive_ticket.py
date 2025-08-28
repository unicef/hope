from typing import Any

from django.core.management import call_command
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.geo import models as geo_models
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db()


class TestGrievanceCreateSensitiveTicket:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.business_area = create_afghanistan()
        call_command("loadcountries")
        partner = PartnerFactory(name="Partner")
        self.user = UserFactory.create(partner=partner)
        self.api_client = api_client(self.user)
        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        self.admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="asfdsfg")

        self.household1, self.individuals1 = create_household(
            {"size": 1, "business_area": self.business_area},
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe",
            },
        )
        self.household2, self.individuals2 = create_household(
            {"size": 1, "business_area": self.business_area},
            {
                "given_name": "John",
                "family_name": "Doe",
                "middle_name": "",
                "full_name": "John Doe Second Individual",
            },
        )
        self.program = ProgramFactory(status=Program.ACTIVE, business_area=self.business_area)
        payment_plan = PaymentPlanFactory(program_cycle=self.program.cycles.first(), business_area=self.business_area)
        self.payment = PaymentFactory(
            household=self.household1,
            collector=self.individuals1[0],
            business_area=self.business_area,
            parent=payment_plan,
            currency="PLN",
        )
        self.second_payment = PaymentFactory(
            household=self.household2,
            collector=self.individuals2[0],
            business_area=self.business_area,
            parent=payment_plan,
            currency="PLN",
        )
        self.list_url = reverse(
            "api:grievance-tickets:grievance-tickets-global-list",
            kwargs={"business_area_slug": self.business_area.slug},
        )

    def test_create_sensitive_ticket(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.business_area, self.program)
        input_data = {
            "description": "Test Feedback",
            "assigned_to": str(self.user.id),
            "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            "issue_type": GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
            "admin": str(self.admin_area.id),
            "language": "Polish, English",
            "consent": True,
            "extras": {
                "category": {
                    "sensitive_grievance_ticket_extras": {
                        "household": str(self.household1.id),
                        "individual": str(self.individuals1[0].id),
                    }
                }
            },
        }
        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data[0]["payment_record"] is None

    def test_create_sensitive_ticket_wrong_extras(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.business_area, self.program)
        input_data = {
            "description": "Test Feedback",
            "assigned_to": str(self.user.id),
            "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            "issue_type": GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
            "admin": str(self.admin_area.id),
            "language": "Polish, English",
            "consent": True,
            "extras": {
                "category": {
                    "grievance_complaint_ticket_extras": {
                        "household": str(self.household1.id),
                        "individual": str(self.individuals1[0].id),
                    }
                }
            },
        }
        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        # The test is intentionally using wrong extras type for category
        # Should get validation error about wrong extras for this category
        assert "You can't provide extras.category.grievance_complaint_ticket_extras in 3" in str(response_data)

    def test_create_sensitive_ticket_without_issue_type(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.business_area, self.program)
        input_data = {
            "description": "Test Feedback",
            "assigned_to": str(self.user.id),
            "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            "admin": str(self.admin_area.id),
            "language": "Polish, English",
            "consent": True,
            "extras": {
                "category": {
                    "sensitive_grievance_ticket_extras": {
                        "household": str(self.household1.id),
                        "individual": str(self.individuals1[0].id),
                        "payment_record": [str(self.payment.id)],
                    }
                }
            },
        }

        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "You have to provide issue_type in 3" in response.json()

    def test_create_sensitive_ticket_with_two_payment_records(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.business_area, self.program)
        input_data = {
            "description": "Test Feedback",
            "assigned_to": str(self.user.id),
            "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            "issue_type": GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
            "admin": str(self.admin_area.id),
            "language": "Polish, English",
            "consent": True,
            "extras": {
                "category": {
                    "sensitive_grievance_ticket_extras": {
                        "household": str(self.household1.id),
                        "individual": str(self.individuals1[0].id),
                        "payment_record": [
                            str(self.payment.id),
                            str(self.second_payment.id),
                        ],
                    }
                }
            },
        }

        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()[0]["payment_record"] is not None

    def test_create_sensitive_ticket_without_payment_record(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.business_area, self.program)

        input_data = {
            "description": "Test Feedback",
            "assigned_to": str(self.user.id),
            "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            "issue_type": GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
            "admin": str(self.admin_area.id),
            "language": "Polish, English",
            "consent": True,
            "extras": {
                "category": {
                    "sensitive_grievance_ticket_extras": {
                        "household": str(self.household1.id),
                        "individual": str(self.individuals1[0].id),
                    }
                }
            },
        }

        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data[0]["payment_record"] is None

    def test_create_sensitive_ticket_without_household(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.business_area, self.program)
        input_data = {
            "description": "Test Feedback",
            "assigned_to": str(self.user.id),
            "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            "issue_type": GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
            "admin": str(self.admin_area.id),
            "language": "Polish, English",
            "consent": True,
            "extras": {"category": {"sensitive_grievance_ticket_extras": {"individual": str(self.individuals1[0].id)}}},
        }
        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data[0]["payment_record"] is None
        assert response.data[0]["household"] is None
        assert response.data[0]["individual"] is not None

    def test_create_sensitive_ticket_without_individual(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.business_area, self.program)

        input_data = {
            "description": "Test Feedback",
            "assigned_to": str(self.user.id),
            "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            "issue_type": GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
            "admin": str(self.admin_area.id),
            "language": "Polish, English",
            "consent": True,
            "extras": {"category": {"sensitive_grievance_ticket_extras": {"household": str(self.household1.id)}}},
        }

        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data[0]["individual"] is None
        assert response.data[0]["payment_record"] is None
        assert response.data[0]["household"] is not None

    def test_create_sensitive_ticket_without_extras(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.business_area, self.program)
        input_data = {
            "description": "Test Feedback",
            "assigned_to": str(self.user.id),
            "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            "issue_type": GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
            "admin": str(self.admin_area.id),
            "language": "Polish, English",
            "consent": True,
        }
        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data[0]["individual"] is None
        assert response.data[0]["payment_record"] is None
        assert response.data[0]["household"] is None
