from datetime import datetime
from typing import Any, Callable, Dict
from unicodedata import category
from datetime import date

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
    TicketHouseholdDataUpdateDetailsFactory, TicketIndividualDataUpdateDetailsFactory, \
    TicketAddIndividualDetailsFactory, TicketDeleteIndividualDetailsFactory, TicketDeleteHouseholdDetailsFactory, \
    TicketSystemFlaggingDetailsFactory
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.api.serializers.individual import IndividualForTicketSerializer
from hct_mis_api.apps.household.fixtures import create_household_and_individuals, DocumentFactory, DocumentTypeFactory
from hct_mis_api.apps.household.models import ROLE_ALTERNATE, SINGLE, IndividualRoleInHousehold, ROLE_PRIMARY, DUPLICATE
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.sanction_list.fixtures import SanctionListIndividualFactory
from hct_mis_api.apps.sanction_list.models import SanctionListIndividualDocument, SanctionListIndividualDateOfBirth

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
        self.household2, self.individuals2 = create_household_and_individuals(
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

    def test_grievance_detail_add_individual(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            household_unicef_id=self.household1.unicef_id,
        )
        ticket_details = TicketAddIndividualDetailsFactory(
            ticket=grievance_ticket,
            household=self.household1,
            approve_status=True,
            individual_data={
                "given_name": "Test",
                "full_name": "Test Example",
                "family_name": "Example",
                "sex": "MALE",
                "birth_date": date(year=1980, month=2, day=1).isoformat(),
                "marital_status": SINGLE,
                "documents": [],
            },
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
            "approve_status": ticket_details.approve_status,
        }

    def test_grievance_detail_delete_individual(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
            household_unicef_id=self.household1.unicef_id,
        )
        role_primary = IndividualRoleInHousehold.objects.create(
            role=ROLE_PRIMARY,
            individual=self.individuals1[0],
            household=self.household1,
        )
        ticket_details = TicketDeleteIndividualDetailsFactory(
            ticket=grievance_ticket,
            individual=self.individuals1[0],
            approve_status=True,
            role_reassign_data={
                str(role_primary.id): {
                    "role": ROLE_PRIMARY,
                    "household": str(self.household1.id),
                    "individual":  str(self.individuals1[1].id),
                }
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
            "role_reassign_data": ticket_details.role_reassign_data,
            "approve_status": ticket_details.approve_status,
        }

    def test_grievance_detail_delete_household(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
            household_unicef_id=self.household1.unicef_id,
        )
        role_primary = IndividualRoleInHousehold.objects.create(
            role=ROLE_PRIMARY,
            individual=self.individuals1[0],
            household=self.household2,
        )
        ticket_details = TicketDeleteHouseholdDetailsFactory(
            ticket=grievance_ticket,
            household=self.household1,
            approve_status=True,
            reason_household=self.household2,
            role_reassign_data={
                str(role_primary.id): {
                    "role": ROLE_PRIMARY,
                    "household": str(self.household2.id),
                    "individual": str(self.individuals2[0].id),
                }
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
            "role_reassign_data": ticket_details.role_reassign_data,
            "approve_status": ticket_details.approve_status,
            "reason_household": {
                "id": str(ticket_details.reason_household.id),
                "unicef_id": ticket_details.reason_household.unicef_id,
                "admin2": ticket_details.reason_household.admin2.name,
            },
        }

    def test_grievance_detail_system_flagging(self, create_user_role_with_permissions: Any) -> None:
        grievance_ticket = GrievanceTicketFactory(
            **self.grievance_ticket_base_data,
            category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
            household_unicef_id=self.household1.unicef_id,
        )
        sanction_list_individual = SanctionListIndividualFactory(
            full_name="Sanction Individual"
        )
        sanction_list_individual_document = SanctionListIndividualDocument.objects.create(
            individual=sanction_list_individual,
            document_number="123-456-789",
            type_of_document="DOC",
        )
        sanction_list_date_of_birth = SanctionListIndividualDateOfBirth.objects.create(
            individual=sanction_list_individual,
            date=date(year=1980, month=2, day=1),
        )
        golden_records_individual = self.individuals1[0]
        golden_records_individual.deduplication_golden_record_status = DUPLICATE
        golden_records_individual.deduplication_golden_record_results = {
            "duplicates": [
                {
                    "hit_id": str(golden_records_individual.pk),
                    "score": 9.0,
                    "proximity_to_score": 3.0,
                }
            ],
            "possible_duplicates": [{"hit_id": str(golden_records_individual.pk)}],
        }
        golden_records_individual.save()
        document_type = DocumentTypeFactory()
        document = DocumentFactory(
            document_number="123-456-789",
            type=document_type,
            individual=golden_records_individual,
            program=self.program,
            country=self.country,
        )
        ticket_details = TicketSystemFlaggingDetailsFactory(
            ticket=grievance_ticket,
            golden_records_individual=golden_records_individual,
            sanction_list_individual=sanction_list_individual,
            approve_status=True,
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
            "role_reassign_data": ticket_details.role_reassign_data,
            "approve_status": ticket_details.approve_status,
            "golden_records_individual": {
                "id": str(golden_records_individual.id),
                "unicef_id": golden_records_individual.unicef_id,
                "full_name": golden_records_individual.full_name,
                "birth_date": f"{golden_records_individual.birth_date:%Y-%m-%d}",
                "last_registration_date":  f"{golden_records_individual.last_registration_date:%Y-%m-%d}",
                "sex": golden_records_individual.sex,
                "duplicate": golden_records_individual.duplicate,
                "household": {
                    "id": str(golden_records_individual.household.id),
                    "unicef_id": golden_records_individual.household.unicef_id,
                    "admin2": golden_records_individual.household.admin2.name,
                },
                "deduplication_golden_record_results": [
                    {
                        "hit_id": str(golden_records_individual.pk),
                        "unicef_id": golden_records_individual.unicef_id,
                        "score": 9.0,
                        "proximity_to_score": 3.0,
                        "location": "Not provided",
                        "age": None,
                        "duplicate": False,
                        "distinct": False,
                    }
                ],
                "documents": [
                    {
                        "id": str(document.id),
                        "type": {
                            "id": str(document.type.id),
                            "label": document.type.label,
                            "key": document.type.key,
                        },
                        "country": {
                            "id": str(document.country.id),
                            "name": document.country.name,
                            "iso_code3": document.country.iso_code3,
                        },
                        "document_number": document.document_number,
                    },
                ],
            },
            "sanction_list_individual": {
                "id": str(sanction_list_individual.id),
                "full_name": sanction_list_individual.full_name,
                "reference_number": sanction_list_individual.reference_number,
                "documents": [
                    {
                        "id": str(sanction_list_individual_document.id),
                        "document_number": sanction_list_individual_document.document_number,
                        "type_of_document": sanction_list_individual_document.type_of_document,
                    }
                ],
                "dates_of_birth": [
                    {
                        "id": str(sanction_list_date_of_birth.id),
                        "date": f"{sanction_list_date_of_birth.date:%Y-%m-%d}",
                    }
                ],
            },
        }

    def _assign_ticket_data(self, grievance_ticket: GrievanceTicket) -> None:
        self.ticket_note.ticket = grievance_ticket
        self.ticket_note.save()
        self.grievance_document.grievance_ticket = grievance_ticket
        self.grievance_document.save()

        grievance_ticket.programs.add(self.program)

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
