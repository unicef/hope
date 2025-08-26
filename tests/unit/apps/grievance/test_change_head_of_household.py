from typing import Any

from django.core.management import call_command
from django.urls import reverse
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketIndividualDataUpdateDetailsFactory,
)
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
import pytest
from rest_framework import status

from hope.apps.account.permissions import Permissions
from hope.apps.geo import models as geo_models
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.models import AUNT_UNCLE, BROTHER_SISTER, HEAD, Individual
from hope.apps.program.models import Program
from hope.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")
pytestmark = pytest.mark.django_db()


@pytest.mark.elasticsearch
class TestChangeHeadOfHousehold:
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
        self.admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="asdeeed")

        self.household = HouseholdFactory.build()
        self.household.program.save()
        self.household.household_collection.save()
        self.household.registration_data_import.imported_by.save()
        self.household.registration_data_import.program = self.household.program
        self.household.registration_data_import.save()

        self.individual1: Individual = IndividualFactory(household=self.household, program=self.household.program)
        self.individual2: Individual = IndividualFactory(household=self.household, program=self.household.program)
        self.individual1.relationship = HEAD
        self.individual2.relationship = BROTHER_SISTER
        self.individual1.save()
        self.individual2.save()

        self.household.head_of_household = self.individual1
        self.household.save()

        self.grievance_ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin2=self.admin_area,
            business_area=self.afghanistan,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        self.grievance_ticket.programs.set([self.program])
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.grievance_ticket,
            individual=self.individual2,
            individual_data={
                "relationship": {
                    "value": "HEAD",
                    "approve_status": True,
                    "previous_value": "BROTHER_SISTER",
                }
            },
        )
        rebuild_search_index()

    def test_close_update_individual_should_throw_error_when_there_is_one_head_of_household(
        self, create_user_role_with_permissions: Any
    ) -> None:
        url = reverse(
            "api:grievance-tickets:grievance-tickets-global-status-change",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "pk": str(self.grievance_ticket.pk),
            },
        )
        create_user_role_with_permissions(
            self.user,
            [
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
                Permissions.GRIEVANCES_UPDATE,
            ],
            self.afghanistan,
            self.program,
        )
        self.individual1.relationship = HEAD
        self.individual1.save()

        self.household.head_of_household = self.individual1
        self.household.save()

        self.individual1.refresh_from_db()
        self.individual2.refresh_from_db()
        assert self.individual1.relationship == "HEAD"
        assert self.individual2.relationship == "BROTHER_SISTER"

        response = self.api_client.post(url, {"status": GrievanceTicket.STATUS_CLOSED}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        self.individual1.refresh_from_db()
        self.individual2.save()
        self.individual2.refresh_from_db()

        assert "There is one head of household. First, you need to change its role." in response.json()
        assert self.individual1.relationship == "HEAD"
        assert self.individual2.relationship == "BROTHER_SISTER"

    def test_close_update_individual_should_change_head_of_household_if_there_was_no_one(
        self, create_user_role_with_permissions: Any
    ) -> None:
        url = reverse(
            "api:grievance-tickets:grievance-tickets-global-status-change",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "pk": str(self.grievance_ticket.pk),
            },
        )
        create_user_role_with_permissions(
            self.user,
            [
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
                Permissions.GRIEVANCES_UPDATE,
            ],
            self.afghanistan,
            self.program,
        )
        self.individual1.relationship = AUNT_UNCLE
        self.individual1.save()

        self.household.head_of_household = self.individual1
        self.household.save()

        response = self.api_client.post(url, {"status": GrievanceTicket.STATUS_CLOSED}, format="json")
        assert response.status_code == status.HTTP_202_ACCEPTED

        self.individual1.refresh_from_db()
        self.individual2.refresh_from_db()

        assert self.individual1.relationship == "AUNT_UNCLE"
        assert self.individual2.relationship == "HEAD"
