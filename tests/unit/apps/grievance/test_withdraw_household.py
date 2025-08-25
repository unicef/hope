from typing import Any

import pytest
from django.core.management import call_command
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketDeleteIndividualDetailsFactory,
)
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from rest_framework import status
from rest_framework.reverse import reverse

from hope.apps.account.permissions import Permissions
from models.core import BusinessArea
from models import geo as geo_models
from hope.apps.grievance.models import GrievanceTicket
from models.household import Household, Individual
from models.program import Program

pytestmark = pytest.mark.django_db()


class TestWithdrawHousehold:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        call_command("loadcountries")
        self.business_area = create_afghanistan()
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.program = ProgramFactory(
            business_area=self.business_area,
            status=Program.ACTIVE,
            name="program afghanistan 1",
        )
        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        self.area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="dffgh565556")

        self.program = ProgramFactory(
            status=Program.ACTIVE,
            business_area=BusinessArea.objects.first(),
        )

    def test_withdraw_household_when_withdraw_last_individual_empty(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [
                Permissions.GRIEVANCES_UPDATE,
                Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
            ],
            self.business_area,
            self.program,
        )
        household = HouseholdFactory.build(program=self.program)
        household.household_collection.save()
        household.registration_data_import.imported_by.save()
        household.registration_data_import.program = self.program
        household.registration_data_import.save()
        household.program = self.program
        individual_data = {
            "full_name": "Test Example",
            "given_name": "Test",
            "family_name": "Example",
            "phone_no": "+18773523904",
            "birth_date": "1965-03-15",
            "household": household,
            "program": self.program,
        }

        individual = IndividualFactory(**individual_data)
        household.head_of_household = individual
        household.save()

        ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
            admin2=self.area_1,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        ticket.programs.set([self.program])
        TicketDeleteIndividualDetailsFactory(
            ticket=ticket,
            individual=individual,
            role_reassign_data={},
            approve_status=True,
        )

        url = reverse(
            "api:grievance-tickets:grievance-tickets-global-status-change",
            kwargs={
                "business_area_slug": self.business_area.slug,
                "pk": str(ticket.id),
            },
        )
        response = self.api_client.post(url, {"status": GrievanceTicket.STATUS_CLOSED}, format="json")
        assert response.status_code == status.HTTP_202_ACCEPTED

        ind = Individual.objects.filter(id=individual.id).first()
        hh = Household.objects.filter(id=household.id).first()

        assert ind.withdrawn is True
        assert hh.withdrawn is True
