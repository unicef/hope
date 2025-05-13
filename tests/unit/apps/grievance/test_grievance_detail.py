from datetime import datetime
from typing import Any, Callable, Dict
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
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory, TicketNoteFactory, GrievanceDocumentFactory, \
    TicketHouseholdDataUpdateDetailsFactory, TicketIndividualDataUpdateDetailsFactory
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import ROLE_ALTERNATE
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
        self.linked_ticket.created_at = timezone.make_aware(datetime(year=2021, month=8, day=22))
        self.linked_ticket.save()

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
        self.existing_ticket.created_at = timezone.make_aware(datetime(year=2021, month=8, day=23))
        self.existing_ticket.save()

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

    @pytest.mark.parametrize(
        "permissions, area_limit, expected_status_1, expected_status_2",
        [
            ([Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE], False, status.HTTP_200_OK, status.HTTP_404_NOT_FOUND),
            ([Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR], False, status.HTTP_200_OK, status.HTTP_404_NOT_FOUND),
            ([Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER], False, status.HTTP_404_NOT_FOUND, status.HTTP_404_NOT_FOUND),
            ([Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE], False, status.HTTP_404_NOT_FOUND, status.HTTP_200_OK),
            ([Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR], False, status.HTTP_404_NOT_FOUND, status.HTTP_404_NOT_FOUND),
            ([Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER], False, status.HTTP_404_NOT_FOUND, status.HTTP_200_OK),
            (
                [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE],
                False, status.HTTP_200_OK, status.HTTP_200_OK,
            ),
            (
                [Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE, Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE],
                True, status.HTTP_404_NOT_FOUND, status.HTTP_200_OK,
            ),
        ],
    )
    def test_grievance_ticket_detail_access_based_on_permissions(
        self,
        permissions: list,
        area_limit: bool,
        expected_status_1: status,
        expected_status_2: status,
        create_user_role_with_permissions: Callable,
        set_admin_area_limits_in_program: Callable,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )
        grievance_ticket_non_sensitive_with_creator = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
        )
        grievance_ticket_non_sensitive_with_creator.programs.add(self.program)
        grievance_ticket_sensitive_with_owner = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            issue_type=GrievanceTicket.ISSUE_TYPE_UNAUTHORIZED_USE,
        )
        grievance_ticket_sensitive_with_owner.created_by = self.user2
        grievance_ticket_sensitive_with_owner.assigned_to = self.user
        grievance_ticket_sensitive_with_owner.admin2 = None
        grievance_ticket_sensitive_with_owner.save()
        grievance_ticket_sensitive_with_owner.programs.add(self.program)
        if area_limit:
            set_admin_area_limits_in_program(self.partner, self.program, [self.area2])

        response_1 = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket_non_sensitive_with_creator.id),
                },
            )
        )
        assert response_1.status_code == expected_status_1

        response_2 = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(grievance_ticket_sensitive_with_owner.id),
                },
            )
        )
        assert response_2.status_code == expected_status_2

    def test_grievance_detail_household_data_update(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            household_unicef_id=self.household1.unicef_id,
        )
        grievance_ticket.programs.add(self.program)
        ticket_details = TicketHouseholdDataUpdateDetailsFactory(
            ticket=grievance_ticket,
            household=self.household1,
            household_data={
                "village": {"value": "Test Village", "approve_status": True}
            }
        )
        self._assign_ticket_data(grievance_ticket)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
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
        data = response.data

        self._assert_base_grievance_data(data, grievance_ticket)
        assert data["payment_record"] == {}

        assert data["ticket_details"] == {
            "id": str(ticket_details.id),
            "household_data": ticket_details.household_data,
        }

    def test_grievance_detail_individual_data_update(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            household_unicef_id=self.household1.unicef_id,
        )
        grievance_ticket.programs.add(self.program)
        ticket_details = TicketIndividualDataUpdateDetailsFactory(
            ticket=grievance_ticket,
            individual=self.individuals1[0],
            individual_data={"role": {"value": ROLE_ALTERNATE, "approve_status": True}},
        )
        self._assign_ticket_data(grievance_ticket)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE],
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
        data = response.data

        self._assert_base_grievance_data(data, grievance_ticket)
        assert data["payment_record"] == {}

        assert data["ticket_details"] == {
            "id": str(ticket_details.id),
            "individual_data": ticket_details.individual_data,
            "role_reassign_data": ticket_details.role_reassign_data,
        }

    def _assign_ticket_data(self, grievance_ticket: GrievanceTicket) -> None:
        self.ticket_note.ticket = grievance_ticket
        self.ticket_note.save()
        self.grievance_document.grievance_ticket = grievance_ticket
        self.grievance_document.save()

        grievance_ticket.linked_tickets.add(self.linked_ticket)

    def _assert_base_grievance_data(self, data: Dict, grievance_ticket: GrievanceTicket) -> None:
        assert data["id"] == str(grievance_ticket.id)
        assert data["unicef_id"] == grievance_ticket.unicef_id
        assert data["status"] == grievance_ticket.status
        assert data["programs"] == [
            {
                "id": str(grievance_ticket.programs.first().id),
                "programme_code": grievance_ticket.programs.first().programme_code,
                "slug": grievance_ticket.programs.first().slug,
                "name": grievance_ticket.programs.first().name,
                "status": grievance_ticket.programs.first().status,
            }
        ]
        household = getattr(getattr(grievance_ticket, "ticket_details", None), "household", None)
        expected_household = (
            {
                "id": str(household.id),
                "unicef_id": household.unicef_id,
                "admin2": household.admin2.name,
            }
            if household
            else None
        )
        assert data["household"] == expected_household
        assert data["admin"] == (grievance_ticket.admin2.name if grievance_ticket.admin2 else "")
        expected_admin2 = (
            {
                "id": str(grievance_ticket.admin2.id),
                "name": grievance_ticket.admin2.name,
                "p_code": grievance_ticket.admin2.p_code,
            }
            if grievance_ticket.admin2
            else None
        )
        assert data["admin2"] == expected_admin2
        assert data["assigned_to"] == {
            "id": str(grievance_ticket.assigned_to.id),
            "first_name": grievance_ticket.assigned_to.first_name,
            "last_name": grievance_ticket.assigned_to.last_name,
            "email": grievance_ticket.assigned_to.email,
            "username": grievance_ticket.assigned_to.username,
        }
        assert data["created_by"] == {
            "id": str(grievance_ticket.created_by.id),
            "first_name": grievance_ticket.created_by.first_name,
            "last_name": grievance_ticket.created_by.last_name,
            "email": grievance_ticket.created_by.email,
            "username": grievance_ticket.created_by.username,
        }
        assert data["user_modified"] == f"{grievance_ticket.user_modified:%Y-%m-%dT%H:%M:%SZ}"
        assert data["category"] == grievance_ticket.category
        assert data["issue_type"] == grievance_ticket.issue_type
        assert data["priority"] == grievance_ticket.priority
        assert data["urgency"] == grievance_ticket.urgency
        assert data["created_at"] == f"{grievance_ticket.created_at:%Y-%m-%dT%H:%M:%SZ}"
        assert data["updated_at"] == f"{grievance_ticket.updated_at:%Y-%m-%dT%H:%M:%SZ}"

        # total_days
        if grievance_ticket.status == GrievanceTicket.STATUS_CLOSED:
            delta = grievance_ticket.updated_at - grievance_ticket.created_at
        else:
            delta = timezone.now() - grievance_ticket.created_at
        expected_total_days = delta.days
        assert data["total_days"] == expected_total_days
        assert data["target_id"] == grievance_ticket.target_id
        assert data["partner"] == (
            {
                "id": str(grievance_ticket.partner.id),
                "name": grievance_ticket.partner.name,
            } if grievance_ticket.partner else None)
        assert data["postpone_deduplication"] == self.afghanistan.postpone_deduplication
        individual = getattr(getattr(grievance_ticket, "ticket_details", None), "individual", None)
        expected_individual = (
            {
                "id": str(individual.id),
                "unicef_id": individual.unicef_id,
                "full_name": individual.full_name,
                "household": {
                    "id": str(individual.household.id),
                    "unicef_id": individual.household.unicef_id,
                    "admin2": individual.household.admin2.name,
                },
            }
            if individual
            else None
        )
        assert data["individual"] == expected_individual

        related_tickets = data["related_tickets"]
        assert             {
                "id": str(self.existing_ticket.id),
                "unicef_id": self.existing_ticket.unicef_id,
            } in related_tickets
        assert {
                "id": str(self.linked_ticket.id),
                "unicef_id": self.linked_ticket.unicef_id,
            } in related_tickets
        assert data["linked_tickets"] == [
            {
                "id": str(self.linked_ticket.id),
                "unicef_id": self.linked_ticket.unicef_id,
            },
        ]
        assert data["existing_tickets"] == [
            {
                "id": str(self.existing_ticket.id),
                "unicef_id": self.existing_ticket.unicef_id,
            },
        ]

        assert data["ticket_notes"] == [
            {
                "id": str(self.ticket_note.id),
                "description": self.ticket_note.description,
                "created_by": {
                    "id": str(self.user.id),
                    "first_name": self.user.first_name,
                    "last_name": self.user.last_name,
                    "email": self.user.email,
                    "username": self.user.username,
                },
                "created_at": f"{self.ticket_note.created_at:%Y-%m-%dT%H:%M:%S.%fZ}",
                "updated_at": f"{self.ticket_note.updated_at:%Y-%m-%dT%H:%M:%SZ}",
            }
        ]

        assert data["documentation"] == [
            {
                "id": str(self.grievance_document.id),
                "name": self.grievance_document.name,
                "file_path": self.grievance_document.file_path,
                "file_name": self.grievance_document.file_name,
                "content_type": self.grievance_document.content_type,
                "file_size": self.grievance_document.file_size,
                "created_by": {
                    "id": str(self.user.id),
                    "first_name": self.user.first_name,
                    "last_name": self.user.last_name,
                    "email": self.user.email,
                    "username": self.user.username,
                },
                "created_at": f"{self.grievance_document.created_at:%Y-%m-%dT%H:%M:%S.%fZ}",
                "updated_at": f"{self.grievance_document.updated_at:%Y-%m-%dT%H:%M:%SZ}",
            }
        ]
