from django.core.management import call_command
from parameterized import parameterized

from hct_mis_api.apps.grievance.fixtures import TicketIndividualDataUpdateDetailsFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory
from hct_mis_api.apps.grievance.management.commands.fix_grievance_tickets import fix_disability_fields
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.household.models import HEAD, MALE, DISABLED, NOT_DISABLED
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


class TestFixingGrievanceTickets(APITestCase):
    databases = "__all__"

    CREATE_DATA_CHANGE_GRIEVANCE_MUTATION = """
    mutation createGrievanceTicket($input:CreateGrievanceTicketInput!){
      createGrievanceTicket(input:$input){
        grievanceTickets{
          description
          category
          issueType
          individualDataUpdateTicketDetails{
            individual{
              fullName
            }
            individualData
          }
          sensitiveTicketDetails{
            id
          }
          householdDataUpdateTicketDetails{
            household{
              id
            }
            householdData
          }
          addIndividualTicketDetails{
            household{
              id
            }
            individualData
          }
        }
      }
    }
    """

    @parameterized.expand(
        [
            (True, DISABLED),
            (False, NOT_DISABLED),
        ]
    )
    def test_wrong_value_in_disability_field(self, previous_value, new_value):
        self.user = UserFactory.create()
        self.business_area = BusinessAreaFactory(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            slug="afghanistan",
            has_data_sharing_agreement=True,
        )
        self.registration_data_import = RegistrationDataImportFactory(business_area=self.business_area)

        (_, individuals) = create_household_and_individuals(
            household_data={
                "registration_data_import": self.registration_data_import,
                "business_area": self.business_area,
            },
            individuals_data=[
                {
                    "registration_data_import": self.registration_data_import,
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": HEAD,
                    "sex": MALE,
                    "birth_date": "1955-09-07",
                },
            ],
        )
        self.individual = individuals[0]

        self.assertEqual(GrievanceTicket.objects.count(), 0)
        ticket = GrievanceTicketFactory(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        )
        self.assertEqual(GrievanceTicket.objects.count(), 1)
        TicketIndividualDataUpdateDetailsFactory(
            ticket=ticket,
            individual=self.individual,
            individual_data={
                "disability": {
                    "value": previous_value,
                }
            },
        )
        self.assertEqual(
            ticket.individual_data_update_ticket_details.individual_data["disability"]["value"],
            previous_value,
        )

        fix_disability_fields()

        ticket.refresh_from_db()
        self.assertEqual(
            ticket.individual_data_update_ticket_details.individual_data["disability"]["value"],
            new_value,
        )

    def test_skipping_when_ind_data_update_ticket_details_does_not_exist(self):
        self.user = UserFactory.create()
        self.business_area = BusinessAreaFactory(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            slug="afghanistan",
            has_data_sharing_agreement=True,
        )
        self.registration_data_import = RegistrationDataImportFactory(business_area=self.business_area)

        (_, individuals) = create_household_and_individuals(
            household_data={
                "registration_data_import": self.registration_data_import,
                "business_area": self.business_area,
            },
            individuals_data=[
                {
                    "registration_data_import": self.registration_data_import,
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": HEAD,
                    "sex": MALE,
                    "birth_date": "1955-09-07",
                },
            ],
        )
        self.individual = individuals[0]

        self.assertEqual(GrievanceTicket.objects.count(), 0)
        GrievanceTicketFactory(
            business_area=self.business_area,
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        )
        self.assertEqual(GrievanceTicket.objects.count(), 1)

        fix_disability_fields()
        # didn't throw, so it skipped ticket with not existing TicketIndividualDataUpdateDetailsFactory
