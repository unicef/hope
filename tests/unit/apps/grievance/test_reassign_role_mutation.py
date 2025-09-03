from typing import Any

from django.core.management import call_command
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketDeleteIndividualDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.geo import models as geo_models
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.models import ROLE_PRIMARY, IndividualRoleInHousehold
from hope.apps.program.models import Program
from hope.apps.utils.models import MergeStatusModel

pytestmark = pytest.mark.django_db()


class TestRoleReassignMutation:
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
        self.household = HouseholdFactory.build(program=self.program)
        self.household.household_collection.save()
        self.household.registration_data_import.imported_by.save()
        self.household.registration_data_import.program = self.program
        self.household.registration_data_import.save()

        self.individual = IndividualFactory(
            full_name="Benjamin Butler",
            given_name="Benjamin",
            family_name="Butler",
            phone_no="(953)682-4596",
            birth_date="1943-07-30",
            household=None,
            program=self.program,
        )

        self.household.head_of_household = self.individual
        self.household.save()

        self.individual.household = self.household
        self.individual.save()

        self.household.refresh_from_db()
        self.individual.refresh_from_db()

        self.role = IndividualRoleInHousehold.objects.create(
            household=self.household,
            individual=self.individual,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        self.grievance_ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
            admin2=self.admin_area,
            business_area=self.afghanistan,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        self.grievance_ticket.programs.set([self.program])
        TicketDeleteIndividualDetailsFactory(
            ticket=self.grievance_ticket,
            individual=self.individual,
            approve_status=True,
        )

    def test_role_reassignment(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.afghanistan, self.program)
        response = self.api_client.post(
            reverse(
                "api:grievance-tickets:grievance-tickets-global-reassign-role",
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(self.grievance_ticket.id),
                },
            ),
            {
                "household_id": str(self.household.id),
                "individual_id": str(self.individual.id),
                "role": ROLE_PRIMARY,
                "version": self.grievance_ticket.version,
            },
            format="json",
        )
        resp_data = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "id" in resp_data

        self.grievance_ticket.refresh_from_db()
        ticket_details = self.grievance_ticket.delete_individual_ticket_details
        role_reassign_data = ticket_details.role_reassign_data

        expected_data = {
            str(self.role.id): {
                "role": "PRIMARY",
                "household": str(self.household.id),
                "individual": str(self.individual.id),
            }
        }
        assert role_reassign_data == expected_data


class TestRoleReassignMutationNewTicket:
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

        self.household = HouseholdFactory.build(program=self.program)
        self.household.household_collection.save()
        self.household.registration_data_import.imported_by.save()
        self.household.registration_data_import.program = self.program
        self.household.registration_data_import.save()

        self.individual_1 = IndividualFactory(
            full_name="Benjamin Butler",
            given_name="Benjamin",
            family_name="Butler",
            phone_no="(953)682-4596",
            birth_date="1943-07-30",
            household=None,
            program=self.program,
        )

        self.individual_2 = IndividualFactory(
            full_name="Andrew Jackson",
            given_name="Andrew",
            family_name="Jackson",
            phone_no="(853)692-4696",
            birth_date="1963-09-12",
            household=None,
            program=self.program,
        )

        self.individual_3 = IndividualFactory(
            full_name="Ulysses Grant",
            given_name="Ulysses",
            family_name="Grant",
            phone_no="(953)682-1111",
            birth_date="1913-01-31",
            household=None,
            program=self.program,
        )

        self.household.head_of_household = self.individual_1
        self.household.save()

        self.individual_1.household = self.household
        self.individual_2.household = self.household

        self.individual_1.save()
        self.individual_2.save()

        self.household.refresh_from_db()
        self.individual_1.refresh_from_db()
        self.individual_2.refresh_from_db()

        self.role = IndividualRoleInHousehold.objects.create(
            household=self.household,
            individual=self.individual_1,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        self.grievance_ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            admin2=self.admin_area,
            business_area=self.afghanistan,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        self.grievance_ticket.programs.set([self.program])
        TicketNeedsAdjudicationDetailsFactory(
            ticket=self.grievance_ticket,
            golden_records_individual=self.individual_1,
            possible_duplicate=self.individual_2,
            is_multiple_duplicates_version=True,
            selected_individual=None,
        )

    def test_role_reassignment_new_ticket(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.afghanistan, self.program)
        response = self.api_client.post(
            reverse(
                "api:grievance-tickets:grievance-tickets-global-reassign-role",
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "pk": str(self.grievance_ticket.id),
                },
            ),
            {
                "household_id": str(self.household.id),
                "individual_id": str(self.individual_1.id),
                "new_individual_id": str(self.individual_2.id),
                "role": ROLE_PRIMARY,
                "version": self.grievance_ticket.version,
            },
            format="json",
        )
        resp_data = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "id" in resp_data

        self.grievance_ticket.refresh_from_db()
        ticket_details = self.grievance_ticket.ticket_details
        role_reassign_data = ticket_details.role_reassign_data

        expected_data = {
            str(self.role.id): {
                "role": "PRIMARY",
                "household": str(self.household.id),
                "individual": str(self.individual_1.id),
                "new_individual": str(self.individual_2.id),
            }
        }

        assert role_reassign_data == expected_data
