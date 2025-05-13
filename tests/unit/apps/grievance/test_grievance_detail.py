from datetime import datetime
from typing import Any, Callable
from unicodedata import category

from django.templatetags.i18n import language
from django.utils import timezone

import pytest
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan, create_ukraine
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory, TicketNoteFactory, GrievanceDocumentFactory
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db()


@freeze_time("2024-08-25 12:00:00")
class TestGrievanceTicketDetail:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.detail_url_name = "api:grievance:grievance-tickets-global-detail"

        self.afghanistan = create_afghanistan()
        self.ukraine = create_ukraine()
        self.program = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="program afghanistan 1",
        )

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.user2 = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.country = CountryFactory()
        self.admin_type = AreaTypeFactory(country=self.country, area_level=1)
        self.area1 = AreaFactory(parent=None, p_code="AF01", area_type=self.admin_type)
        self.area2 = AreaFactory(parent=None, p_code="AF0101", area_type=self.admin_type)

        self.grievance_ticket_base_data = {
            "business_area": self.afghanistan,
            "admin2": self.area1,
            "language": "Polish",
            "consent": True,
            "description": "Test Description",
            "status": GrievanceTicket.STATUS_NEW,
            "created_by": self.user,
            "assigned_to": self.user2,
            "user_modified": timezone.make_aware(datetime(year=2021, month=8, day=22)),
        }

        self.ticket_note = TicketNoteFactory(
            description="Test Note",
            created_by=self.user,
            created_at=timezone.make_aware(datetime(year=2021, month=8, day=22)),
            updated_at=timezone.make_aware(datetime(year=2021, month=8, day=24)),
        )

        self.grievance_document = GrievanceDocumentFactory(
            name="Test Document",
            created_by=self.user,
            created_at=timezone.make_aware(datetime(year=2022, month=8, day=22)),
            updated_at=timezone.make_aware(datetime(year=2022, month=8, day=24)),
        )

        self.household1, self.individuals1 = create_household_and_individuals(
            household_data={
                "admin_area": self.area1,
                "admin1": self.area1,
                "admin2": self.area2,
                "country": self.country,
                "country_origin": self.country,
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.linked_ticket = GrievanceTicketFactory(
            business_area=self.ukraine,
            admin2=self.area1,
            language="Polish",
            consent=True,
            description="Linked Ticket",
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            status=GrievanceTicket.STATUS_NEW,
            created_by=self.user2,
            assigned_to=self.user2,
        )

        self.existing_ticket = GrievanceTicketFactory(
            business_area=self.ukraine,
            admin2=self.area1,
            language="Polish",
            consent=True,
            description="Linked Ticket",
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            status=GrievanceTicket.STATUS_NEW,
            created_by=self.user2,
            assigned_to=self.user2,
            household_unicef_id=self.household1.unicef_id,  # will match if household_unicef_id is the same
        )

    def test_grievance_detail_with_all_permissions(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        )
        grievance_ticket.programs.add(self.program)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
            ],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "permissions",
        [
            [],
            (Permissions.PROGRAMME_ACTIVATE,),
        ],
    )
    def test_grievance_detail_without_permissions(self, permissions:list, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        )
        grievance_ticket.programs.add(self.program)

        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_grievance_detail_area_limits(self, create_user_role_with_permissions: Any, set_admin_area_limits_in_program: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        )
        grievance_ticket.programs.add(self.program)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
            ],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        set_admin_area_limits_in_program(self.partner, self.program, [self.area2])

        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_grievance_detail_with_permissions_in_program(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        )
        grievance_ticket.programs.add(self.program)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
                Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
            ],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK

