from django.core.management import call_command

import pytest

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketIndividualDataUpdateDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import (
    AUNT_UNCLE,
    BROTHER_SISTER,
    HEAD,
    Individual,
)
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


class TestChangeHeadOfHousehold(APITestCase):
    STATUS_CHANGE_MUTATION = """
    mutation GrievanceStatusChange($grievanceTicketId: ID!, $status: Int) {
      grievanceStatusChange(grievanceTicketId: $grievanceTicketId, status: $status) {
        grievanceTicket {
          id
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        call_command("loadcountries")
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        admin_area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="sfds323")

        cls.household = HouseholdFactory.build()
        cls.household.program.save()
        cls.household.household_collection.save()
        cls.household.registration_data_import.imported_by.save()
        cls.household.registration_data_import.program = cls.household.program
        cls.household.registration_data_import.save()

        cls.individual1: Individual = IndividualFactory(household=cls.household, program=cls.household.program)
        cls.individual2: Individual = IndividualFactory(household=cls.household, program=cls.household.program)
        cls.individual1.relationship = HEAD
        cls.individual2.relationship = BROTHER_SISTER
        cls.individual1.save()
        cls.individual2.save()

        cls.household.head_of_household = cls.individual1
        cls.household.save()

        cls.grievance_ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin2=admin_area_1,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=cls.grievance_ticket,
            individual=cls.individual2,
            individual_data={
                "relationship": {"value": "HEAD", "approve_status": True, "previous_value": "BROTHER_SISTER"}
            },
        )

        cls.create_user_role_with_permissions(
            cls.user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], cls.business_area
        )
        rebuild_search_index()

    def test_close_update_individual_should_throw_error_when_there_is_one_head_of_household(self) -> None:
        self.individual1.relationship = HEAD
        self.individual1.save()

        self.household.head_of_household = self.individual1
        self.household.save()

        response = self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(self.grievance_ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )

        self.individual1.refresh_from_db()
        self.individual2.refresh_from_db()

        self.assertTrue("There is one head of household" in response["errors"][0]["message"])
        self.assertEqual(self.individual1.relationship, "HEAD")
        self.assertEqual(self.individual2.relationship, "BROTHER_SISTER")

    def test_close_update_individual_should_change_head_of_household_if_there_was_no_one(self) -> None:
        self.individual1.relationship = AUNT_UNCLE
        self.individual1.save()

        self.household.head_of_household = self.individual1
        self.household.save()

        response = self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(self.grievance_ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        self.assertFalse("errors" in response)
        self.individual1.refresh_from_db()
        self.individual2.refresh_from_db()

        self.assertEqual(self.individual1.relationship, "AUNT_UNCLE")
        self.assertEqual(self.individual2.relationship, "HEAD")
