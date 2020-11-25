import json
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
    IDENTIFICATION_TYPE_NATIONAL_ID,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    DocumentType,
)
from program.fixtures import ProgramFactory


class TestGrievanceApproveDataChangeMutation(APITestCase):
    APPROVE_ADD_INDIVIDUAL_MUTATION = """
    mutation ApproveAddIndividual($grievanceTicketId: ID!, $approveStatus: Boolean!) {
      approveAddIndividual(grievanceTicketId: $grievanceTicketId, approveStatus: $approveStatus) {
        grievanceTicket {
          id
          addIndividualTicketDetails {
            approveStatus
          }
        }
      }
    }
    """

    APPROVE_INDIVIDUAL_DATA_CHANGE_GRIEVANCE_MUTATION = """
    mutation ApproveIndividualDataChange(
      $grievanceTicketId: ID!, 
      $individualApproveData: JSONString, 
      $approvedDocumentsToCreate: [Int], 
      $approvedDocumentsToRemove: [Int]
    ) {
      approveIndividualDataChange(
        grievanceTicketId: $grievanceTicketId, 
        individualApproveData: $individualApproveData,
        approvedDocumentsToCreate: $approvedDocumentsToCreate, 
        approvedDocumentsToRemove: $approvedDocumentsToRemove
      ) {
        grievanceTicket {
          id
          individualDataUpdateTicketDetails {
            individualData
          }
        }
      }
    }
    """

    APPROVE_HOUSEHOLD_DATA_CHANGE_GRIEVANCE_MUTATION = """
    mutation ApproveHouseholdDataChange($grievanceTicketId: ID!, $householdApproveData: JSONString) {
      approveHouseholdDataChange(
        grievanceTicketId: $grievanceTicketId, householdApproveData: $householdApproveData
      ) {
        grievanceTicket {
          id
          householdDataUpdateTicketDetails {
            householdData
          }
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.generate_document_types_for_all_countries()
        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaTypeFactory(name="Admin type one", admin_level=2, business_area=self.business_area,)
        self.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_type=area_type)
        self.admin_area_2 = AdminAreaFactory(title="City Example", admin_area_type=area_type)
        program_one = ProgramFactory(name="Test program ONE", business_area=BusinessArea.objects.first(),)

        household_one = HouseholdFactory.build(id="07a901ed-d2a5-422a-b962-3570da1d5d07")
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.save()
        household_one.programs.add(program_one)

        self.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
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
        household_one.head_of_household = first_individual
        household_one.save()
        self.household_one = household_one

        self.add_individual_grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
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
                "documents": [
                    {"country": "POL", "type": IDENTIFICATION_TYPE_NATIONAL_ID, "number": "123-XYZ-321",},
                    {"country": "POL", "type": IDENTIFICATION_TYPE_BIRTH_CERTIFICATE, "number": "QWE4567",},
                ],
            },
            approve_status=False,
        )

        self.individual_data_change_grievance_ticket = GrievanceTicketFactory(
            id="acd57aa1-efd8-4c81-ac19-b8cabebe8089",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.individual_data_change_grievance_ticket,
            individual=self.individuals[0],
            individual_data={
                "given_name": {"value": "Test", "approve_status": False},
                "full_name": {"value": "Test Example", "approve_status": False},
                "family_name": {"value": "Example", "approve_status": False},
                "sex": {"value": "MALE", "approve_status": False},
                "birth_date": {"value": date(year=1980, month=2, day=1).isoformat(), "approve_status": False},
                "marital_status": {"value": SINGLE, "approve_status": False},
                "documents": [
                    {
                        "value": {"country": "POL", "type": IDENTIFICATION_TYPE_NATIONAL_ID, "number": "999-888-777"},
                        "approve_status": False,
                    },
                ],
                "documents_to_remove": [
                    {"value": self.id_to_base64(self.national_id.id, "DocumentNode"), "approve_status": False},
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
        )
        TicketHouseholdDataUpdateDetailsFactory(
            ticket=self.household_data_change_grievance_ticket,
            household=self.household_one,
            household_data={"village": {"value": "Test Village"}, "size": {"value": 19}},
        )

    def test_approve_add_individual(self):
        self.snapshot_graphql_request(
            request_string=self.APPROVE_ADD_INDIVIDUAL_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(self.add_individual_grievance_ticket.id, "GrievanceTicketNode"),
                "approveStatus": True,
            },
        )

    def test_approve_update_individual(self):
        self.snapshot_graphql_request(
            request_string=self.APPROVE_INDIVIDUAL_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.individual_data_change_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "individualApproveData": json.dumps({"givenName": True, "fullName": True, "familyName": True}),
                "approvedDocumentsToCreate": [0],
                "approvedDocumentsToRemove": [0],
            },
        )

    def test_approve_update_household(self):
        self.snapshot_graphql_request(
            request_string=self.APPROVE_HOUSEHOLD_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.household_data_change_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "householdApproveData": json.dumps({"village": True}),
            },
        )
