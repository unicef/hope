from datetime import date

from django.core.management import call_command
from django_countries.fields import Country

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import AdminAreaTypeFactory, AdminAreaFactory
from core.models import BusinessArea
from grievance.fixtures import (
    GrievanceTicketFactory,
    TicketAddIndividualDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
    TicketHouseholdDataUpdateDetailsFactory,
)
from grievance.models import GrievanceTicket
from household.fixtures import HouseholdFactory, IndividualFactory, DocumentFactory
from household.models import (
    SINGLE,
    ROLE_PRIMARY,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    DocumentType,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    MALE,
    DIVORCED,
    FEMALE,
)
from program.fixtures import ProgramFactory


class TestUpdateGrievanceTickets(APITestCase):
    UPDATE_GRIEVANCE_TICKET_MUTATION = """
    mutation UpdateGrievanceTicket(
      $input: UpdateGrievanceTicketInput!
    ) {
      updateGrievanceTicket(input: $input) {
        grievanceTicket {
          id
          addIndividualTicketDetails {
            individualData
          }
          householdDataUpdateTicketDetails {
            householdData
          }
          individualDataUpdateTicketDetails {
            individualData
          }
          description
          assignedTo {
            id
          }
          status
          area
          admin
          description
          language
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.generate_document_types_for_all_countries()
        self.user = UserFactory(id="a5c44eeb-482e-49c2-b5ab-d769f83db116")
        self.user_two = UserFactory(id="a34716d8-aaf1-4c70-bdd8-0d58be94981a")
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaTypeFactory(name="Admin type one", admin_level=2, business_area=self.business_area, )
        self.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_type=area_type)
        self.admin_area_2 = AdminAreaFactory(title="City Example", admin_area_type=area_type)
        program_one = ProgramFactory(name="Test program ONE", business_area=BusinessArea.objects.first(), )

        household_one = HouseholdFactory.build(id="07a901ed-d2a5-422a-b962-3570da1d5d07", size=2, village="Example")
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.save()
        household_one.programs.add(program_one)

        self.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "sex": FEMALE,
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "marital_status": DIVORCED,
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "sex": FEMALE,
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
                "marital_status": DIVORCED,
            },
        ]

        self.individuals = [
            IndividualFactory(household=household_one, **individual) for individual in self.individuals_to_create
        ]

        first_individual = self.individuals[0]
        national_id_type = DocumentType.objects.get(country=Country("POL"), type=IDENTIFICATION_TYPE_NATIONAL_ID)
        birth_certificate_type = DocumentType.objects.get(
            country=Country("POL"), type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
        )
        self.national_id = DocumentFactory(
            type=national_id_type, document_number="789-789-645", individual=first_individual
        )
        self.birth_certificate = DocumentFactory(
            type=birth_certificate_type, document_number="ITY8456", individual=first_individual
        )
        household_one.head_of_household = self.individuals[0]
        household_one.save()
        self.household_one = household_one

        self.add_individual_grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketAddIndividualDetailsFactory(
            ticket=self.add_individual_grievance_ticket,
            household=self.household_one,
            individual_data={
                "given_name": "Test",
                "full_name": "Test Example",
                "family_name": "Example",
                "sex": "MALE",
                "birth_date": date(year=1980, month=2, day=1).isoformat(),
                "marital_status": SINGLE,
                "role": ROLE_PRIMARY,
                "documents": [{"type": IDENTIFICATION_TYPE_NATIONAL_ID, "country": "POL", "number": "123-123-UX-321"}],
            },
            approve_status=True,
        )

        self.individual_data_change_grievance_ticket = GrievanceTicketFactory(
            id="acd57aa1-efd8-4c81-ac19-b8cabebe8089",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.individual_data_change_grievance_ticket,
            individual=self.individuals[0],
            individual_data={
                "given_name": {"value": "Test", "approve_status": True},
                "full_name": {"value": "Test Example", "approve_status": True},
                "family_name": {"value": "Example", "approve_status": True},
                "sex": {"value": "MALE", "approve_status": False},
                "birth_date": {"value": date(year=1980, month=2, day=1).isoformat(), "approve_status": False},
                "marital_status": {"value": SINGLE, "approve_status": True},
                "role": {"value": ROLE_PRIMARY, "approve_status": True},
                "documents": [
                    {
                        "value": {"country": "POL", "type": IDENTIFICATION_TYPE_NATIONAL_ID, "number": "999-888-777"},
                        "approve_status": True,
                    },
                ],
                "documents_to_remove": [
                    {"value": self.id_to_base64(self.national_id.id, "DocumentNode"), "approve_status": True},
                    {"value": self.id_to_base64(self.birth_certificate.id, "DocumentNode"), "approve_status": False},
                ],
            },
        )

        self.household_data_change_grievance_ticket = GrievanceTicketFactory(
            id="72ee7d98-6108-4ef0-85bd-2ef20e1d5410",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketHouseholdDataUpdateDetailsFactory(
            ticket=self.household_data_change_grievance_ticket,
            household=self.household_one,
            household_data={
                "village": {"value": "Test Village", "approve_status": True},
                "size": {"value": 19, "approve_status": True},
            },
        )

        self.positive_feedback_grievance_ticket = GrievanceTicketFactory(
            id="a2a15944-f836-4764-8163-30e0c47ce3bb",
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            issue_type=None,
            admin="",
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            description="",
            language="Spanish",
        )

    def test_update_add_individual(self):
        input_data = {
            "input": {
                "description": self.add_individual_grievance_ticket.description,
                "assignedTo": self.id_to_base64(self.add_individual_grievance_ticket.assigned_to.id, "UserNode"),
                "admin": self.add_individual_grievance_ticket.admin,
                "language": self.add_individual_grievance_ticket.language,
                "area": self.add_individual_grievance_ticket.area,
                "ticketId": self.id_to_base64(self.add_individual_grievance_ticket.id, "GrievanceTicketNode"),
                "extras": {
                    "addIndividualIssueTypeExtras": {
                        "individualData": {
                            "givenName": "John",
                            "fullName": "John Example",
                            "familyName": "Example",
                            "sex": "MALE",
                            "birthDate": date(year=1981, month=2, day=2).isoformat(),
                            "maritalStatus": SINGLE,
                            "role": ROLE_PRIMARY,
                            "documents": [
                                {"type": IDENTIFICATION_TYPE_NATIONAL_ID, "country": "USA", "number": "321-321-UX-321"}
                            ],
                        }
                    }
                },
            }
        }
        self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION, context={"user": self.user}, variables=input_data,
        )
        self.add_individual_grievance_ticket.refresh_from_db()
        result = self.add_individual_grievance_ticket.add_individual_ticket_details.individual_data
        expected_result = {
            "sex": "MALE",
            "role": "PRIMARY",
            "documents": [{"type": "NATIONAL_ID", "number": "321-321-UX-321", "country": "USA"}],
            "full_name": "John Example",
            "birth_date": "1981-02-02",
            "given_name": "John",
            "family_name": "Example",
            "marital_status": "SINGLE",
            "flex_fields": {},
        }
        self.assertEqual(result, expected_result)
        self.assertEqual(self.add_individual_grievance_ticket.status, GrievanceTicket.STATUS_FOR_APPROVAL)
        self.assertFalse(self.add_individual_grievance_ticket.add_individual_ticket_details.approve_status)

    def test_update_change_individual(self):
        input_data = {
            "input": {
                "description": self.individual_data_change_grievance_ticket.description,
                "assignedTo": self.id_to_base64(
                    self.individual_data_change_grievance_ticket.assigned_to.id, "UserNode"
                ),
                "admin": self.individual_data_change_grievance_ticket.admin,
                "language": self.individual_data_change_grievance_ticket.language,
                "area": self.individual_data_change_grievance_ticket.area,
                "ticketId": self.id_to_base64(self.individual_data_change_grievance_ticket.id, "GrievanceTicketNode"),
                "extras": {
                    "individualDataUpdateIssueTypeExtras": {
                        "individualData": {
                            "givenName": "John",
                            "fullName": "John Example",
                            "familyName": "Example",
                            "sex": MALE,
                            "birthDate": date(year=1962, month=12, day=21).isoformat(),
                            "maritalStatus": SINGLE,
                            "role": ROLE_PRIMARY,
                            "documents": [
                                {"country": "POL", "type": IDENTIFICATION_TYPE_NATIONAL_ID, "number": "111-222-777"},
                            ],
                            "documentsToRemove": [],
                        }
                    }
                },
            }
        }
        self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION, context={"user": self.user}, variables=input_data,
        )
        self.individual_data_change_grievance_ticket.refresh_from_db()
        result = self.individual_data_change_grievance_ticket.individual_data_update_ticket_details.individual_data
        expected_result = {
            "sex": {"value": "MALE", "approve_status": False, "previous_value": "FEMALE"},
            "role": {"value": "PRIMARY", "approve_status": False, "previous_value": None},
            "documents": [
                {"value": {"type": "NATIONAL_ID", "number": "111-222-777", "country": "POL"}, "approve_status": False}
            ],
            "full_name": {"value": "John Example", "approve_status": False, "previous_value": "Benjamin Butler"},
            "birth_date": {"value": "1962-12-21", "approve_status": False, "previous_value": "1943-07-30"},
            "given_name": {"value": "John", "approve_status": False, "previous_value": "Benjamin"},
            "family_name": {"value": "Example", "approve_status": False, "previous_value": "Butler"},
            "marital_status": {"value": "SINGLE", "approve_status": False, "previous_value": "DIVORCED"},
            "previous_documents": {},
            "documents_to_remove": [],
            "flex_fields": {},
        }
        self.assertEqual(result, expected_result)
        self.assertEqual(self.individual_data_change_grievance_ticket.status, GrievanceTicket.STATUS_FOR_APPROVAL)

    def test_update_change_household(self):
        input_data = {
            "input": {
                "description": "this is new description",
                "assignedTo": self.id_to_base64(self.user_two.id, "UserNode"),
                "admin": self.household_data_change_grievance_ticket.admin,
                "language": self.household_data_change_grievance_ticket.language,
                "area": self.household_data_change_grievance_ticket.area,
                "ticketId": self.id_to_base64(self.household_data_change_grievance_ticket.id, "GrievanceTicketNode"),
                "extras": {
                    "householdDataUpdateIssueTypeExtras": {"householdData": {"village": "Test Town", "size": 3, }}
                },
            }
        }
        self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION, context={"user": self.user}, variables=input_data,
        )
        self.household_data_change_grievance_ticket.refresh_from_db()
        result = self.household_data_change_grievance_ticket.household_data_update_ticket_details.household_data
        expected_result = {
            "village": {"value": "Test Town", "approve_status": False, "previous_value": "Example"},
            "size": {"value": 3, "approve_status": False, "previous_value": 2},
            "flex_fields": {},
        }
        self.assertEqual(result, expected_result)
        self.assertEqual(str(self.household_data_change_grievance_ticket.assigned_to.id), self.user_two.id)
        self.assertNotEqual(self.household_data_change_grievance_ticket.description, "this is new description")
        self.assertEqual(self.household_data_change_grievance_ticket.status, GrievanceTicket.STATUS_IN_PROGRESS)

    def test_update_feedback_ticket(self):
        input_data = {
            "input": {
                "description": "New Description",
                "assignedTo": self.id_to_base64(self.user_two.id, "UserNode"),
                "admin": self.admin_area_1.title,
                "language": "Polish, English",
                "area": "Example Town",
                "ticketId": self.id_to_base64(self.positive_feedback_grievance_ticket.id, "GrievanceTicketNode"),
            }
        }
        self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION, context={"user": self.user}, variables=input_data,
        )
        self.positive_feedback_grievance_ticket.refresh_from_db()

        self.assertEqual(self.positive_feedback_grievance_ticket.description, "New Description")
        self.assertEqual(str(self.positive_feedback_grievance_ticket.assigned_to.id), self.user_two.id)
        self.assertEqual(self.positive_feedback_grievance_ticket.admin, self.admin_area_1.title)
        self.assertNotEqual(self.positive_feedback_grievance_ticket.language, "Polish, English")
        self.assertNotEqual(self.positive_feedback_grievance_ticket.area, "Example Town")
