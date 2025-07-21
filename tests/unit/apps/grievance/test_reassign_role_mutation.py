from django.conf import settings
from django.core.management import call_command

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import ROLE_PRIMARY, IndividualRoleInHousehold
from hct_mis_api.apps.utils.models import MergeStatusModel
from tests.extras.test_utils.factories.account import UserFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from tests.extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketDeleteIndividualDetailsFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from tests.extras.test_utils.factories.household import (
    HouseholdFactory,
    IndividualFactory,
)
from tests.extras.test_utils.factories.program import ProgramFactory


class TestRoleReassignMutation(APITestCase):
    REASSIGN_ROLE_MUTATION = """
    mutation ReassignRole(
      $grievanceTicketId: ID!,
      $householdId: ID!,
      $individualId: ID!,
      $newIndividualId: ID,
      $role: String!
    ) {
      reassignRole(
        grievanceTicketId: $grievanceTicketId,
        householdId: $householdId,
        individualId: $individualId,
        newIndividualId: $newIndividualId,
        role: $role
      ) {
        household {
          id
        }
        individual {
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
        cls.admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="sadf3223")

        program_one = ProgramFactory(name="Test program ONE", business_area=BusinessArea.objects.first())

        cls.household = HouseholdFactory.build(program=program_one)
        cls.household.household_collection.save()
        cls.household.registration_data_import.imported_by.save()
        cls.household.registration_data_import.program = program_one
        cls.household.registration_data_import.save()

        cls.individual = IndividualFactory(
            **{
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "household": None,
                "program": program_one,
            },
        )

        cls.household.head_of_household = cls.individual
        cls.household.save()

        cls.individual.household = cls.household
        cls.individual.save()

        cls.household.refresh_from_db()
        cls.individual.refresh_from_db()

        cls.role = IndividualRoleInHousehold.objects.create(
            household=cls.household,
            individual=cls.individual,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        cls.grievance_ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
            admin2=cls.admin_area,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketDeleteIndividualDetailsFactory(
            ticket=cls.grievance_ticket,
            individual=cls.individual,
            approve_status=True,
        )

    def test_role_reassignment(self) -> None:
        variables = {
            "grievanceTicketId": self.id_to_base64(self.grievance_ticket.id, "GrievanceTicketNode"),
            "householdId": self.id_to_base64(self.household.id, "HouseholdNode"),
            "individualId": self.id_to_base64(self.individual.id, "IndividualNode"),
            "role": ROLE_PRIMARY,
        }
        self.graphql_request(
            request_string=self.REASSIGN_ROLE_MUTATION,
            context={"user": self.user},
            variables=variables,
        )

        self.grievance_ticket.refresh_from_db()
        ticket_details = self.grievance_ticket.delete_individual_ticket_details
        role_reassign_data = ticket_details.role_reassign_data

        expected_data = {
            str(self.role.id): {
                "role": "PRIMARY",
                "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                "individual": self.id_to_base64(self.individual.id, "IndividualNode"),
            }
        }
        self.assertEqual(role_reassign_data, expected_data)


class TestRoleReassignMutationNewTicket(APITestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    REASSIGN_ROLE_MUTATION = """
    mutation ReassignRole(
      $grievanceTicketId: ID!,
      $householdId: ID!,
      $individualId: ID!,
      $newIndividualId: ID,
      $role: String!
    ) {
      reassignRole(
        grievanceTicketId: $grievanceTicketId,
        householdId: $householdId,
        individualId: $individualId,
        newIndividualId: $newIndividualId,
        role: $role
      ) {
        household {
          id
        }
        individual {
          id
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="sadf3223")

        program_one = ProgramFactory(name="Test program ONE", business_area=BusinessArea.objects.first())

        cls.household = HouseholdFactory.build(program=program_one)
        cls.household.household_collection.save()
        cls.household.registration_data_import.imported_by.save()
        cls.household.registration_data_import.program = program_one
        cls.household.registration_data_import.save()

        cls.individual_1 = IndividualFactory(
            **{
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "household": None,
                "program": program_one,
            },
        )

        cls.individual_2 = IndividualFactory(
            **{
                "full_name": "Andrew Jackson",
                "given_name": "Andrew",
                "family_name": "Jackson",
                "phone_no": "(853)692-4696",
                "birth_date": "1963-09-12",
                "household": None,
                "program": program_one,
            },
        )

        cls.individual_3 = IndividualFactory(
            **{
                "full_name": "Ulysses Grant",
                "given_name": "Ulysses",
                "family_name": "Grant",
                "phone_no": "(953)682-1111",
                "birth_date": "1913-01-31",
                "household": None,
                "program": program_one,
            },
        )

        cls.household.head_of_household = cls.individual_1
        cls.household.save()

        cls.individual_1.household = cls.household
        cls.individual_2.household = cls.household

        cls.individual_1.save()
        cls.individual_2.save()

        cls.household.refresh_from_db()
        cls.individual_1.refresh_from_db()
        cls.individual_2.refresh_from_db()

        cls.role = IndividualRoleInHousehold.objects.create(
            household=cls.household,
            individual=cls.individual_1,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        cls.grievance_ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            admin2=cls.admin_area,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )

        TicketNeedsAdjudicationDetailsFactory(
            ticket=cls.grievance_ticket,
            golden_records_individual=cls.individual_1,
            possible_duplicate=cls.individual_2,
            is_multiple_duplicates_version=True,
            selected_individual=None,
        )

    def test_role_reassignment_new_ticket(self) -> None:
        variables = {
            "grievanceTicketId": self.id_to_base64(self.grievance_ticket.id, "GrievanceTicketNode"),
            "householdId": self.id_to_base64(self.household.id, "HouseholdNode"),
            "individualId": self.id_to_base64(self.individual_1.id, "IndividualNode"),
            "newIndividualId": self.id_to_base64(self.individual_2.id, "IndividualNode"),
            "role": ROLE_PRIMARY,
        }
        self.graphql_request(
            request_string=self.REASSIGN_ROLE_MUTATION,
            context={"user": self.user},
            variables=variables,
        )

        self.grievance_ticket.refresh_from_db()
        ticket_details = self.grievance_ticket.ticket_details
        role_reassign_data = ticket_details.role_reassign_data

        expected_data = {
            str(self.role.id): {
                "role": "PRIMARY",
                "household": self.id_to_base64(self.household.id, "HouseholdNode"),
                "individual": self.id_to_base64(self.individual_1.id, "IndividualNode"),
                "new_individual": self.id_to_base64(self.individual_2.id, "IndividualNode"),
            }
        }

        self.assertEqual(role_reassign_data, expected_data)
