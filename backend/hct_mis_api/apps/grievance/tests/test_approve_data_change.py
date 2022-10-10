import json
from datetime import date

from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketAddIndividualDetailsFactory,
    TicketHouseholdDataUpdateDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
)
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    SINGLE,
    DocumentType,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory


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
      $flexFieldsApproveData: JSONString,
      $approvedDocumentsToCreate: [Int],
      $approvedDocumentsToEdit: [Int],
      $approvedDocumentsToRemove: [Int],
      $approvedIdentitiesToCreate: [Int],
      $approvedIdentitiesToEdit: [Int],
      $approvedIdentitiesToRemove: [Int],
      $approvedPaymentChannelsToCreate: [Int], 
      $approvedPaymentChannelsToEdit: [Int], 
      $approvedPaymentChannelsToRemove: [Int]
    ) {
      approveIndividualDataChange(
        grievanceTicketId: $grievanceTicketId,
        individualApproveData: $individualApproveData,
        flexFieldsApproveData: $flexFieldsApproveData,
        approvedDocumentsToCreate: $approvedDocumentsToCreate,
        approvedDocumentsToEdit: $approvedDocumentsToEdit,
        approvedDocumentsToRemove: $approvedDocumentsToRemove,
        approvedIdentitiesToCreate: $approvedIdentitiesToCreate,
        approvedIdentitiesToEdit: $approvedIdentitiesToEdit,
        approvedIdentitiesToRemove: $approvedIdentitiesToRemove,
        approvedPaymentChannelsToCreate: $approvedPaymentChannelsToCreate, 
        approvedPaymentChannelsToEdit: $approvedPaymentChannelsToEdit, 
        approvedPaymentChannelsToRemove: $approvedPaymentChannelsToRemove
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
    mutation ApproveHouseholdDataChange(
        $grievanceTicketId: ID!,
        $householdApproveData: JSONString,
        $flexFieldsApproveData: JSONString
    ) {
      approveHouseholdDataChange(
        grievanceTicketId: $grievanceTicketId,
        householdApproveData: $householdApproveData,
        flexFieldsApproveData: $flexFieldsApproveData
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

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        call_command("loadcountries")
        cls.generate_document_types_for_all_countries()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="asdsdf334")
        cls.admin_area_2 = AreaFactory(name="City Example", area_type=area_type, p_code="jghhrrr")

        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )

        household_one = HouseholdFactory.build(id="07a901ed-d2a5-422a-b962-3570da1d5d07")
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.save()
        household_one.programs.add(program_one)

        cls.individuals_to_create = [
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

        cls.individuals = [
            IndividualFactory(household=household_one, **individual) for individual in cls.individuals_to_create
        ]
        first_individual = cls.individuals[0]
        country_pl = geo_models.Country.objects.get(iso_code2="PL")
        national_id_type = DocumentType.objects.get(country=country_pl, type=IDENTIFICATION_TYPE_NATIONAL_ID)
        birth_certificate_type = DocumentType.objects.get(
            country=country_pl, type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
        )

        cls.national_id = DocumentFactory(
            id="df1ce6e8-2864-4c3f-803d-19ec6f4c47f3",
            type=national_id_type,
            document_number="789-789-645",
            individual=first_individual,
        )
        cls.birth_certificate = DocumentFactory(
            id="8ad5e3b8-4c4d-4c10-8756-118d86095dd0",
            type=birth_certificate_type,
            document_number="ITY8456",
            individual=first_individual,
        )
        household_one.head_of_household = first_individual
        household_one.save()
        cls.household_one = household_one

        cls.add_individual_grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            admin2=cls.admin_area_1,
            business_area=cls.business_area,
        )
        TicketAddIndividualDetailsFactory(
            ticket=cls.add_individual_grievance_ticket,
            household=cls.household_one,
            individual_data={
                "given_name": "Test",
                "full_name": "Test Example",
                "family_name": "Example",
                "sex": "MALE",
                "birth_date": date(year=1980, month=2, day=1).isoformat(),
                "marital_status": SINGLE,
                "documents": [
                    {
                        "country": "POL",
                        "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                        "number": "123-XYZ-321",
                    },
                    {
                        "country": "POL",
                        "type": IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
                        "number": "QWE4567",
                    },
                ],
            },
            approve_status=False,
        )

        cls.individual_data_change_grievance_ticket = GrievanceTicketFactory(
            id="acd57aa1-efd8-4c81-ac19-b8cabebe8089",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin2=cls.admin_area_1,
            business_area=cls.business_area,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=cls.individual_data_change_grievance_ticket,
            individual=cls.individuals[0],
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
                "documents_to_edit": [
                    {
                        "value": {
                            "id": cls.id_to_base64(cls.national_id.id, "DocumentNode"),
                            "country": None,
                            "type": None,
                            "number": "999-888-666",
                            "photo": "",
                        },
                        "previous_value": {
                            "id": cls.id_to_base64(cls.national_id.id, "DocumentNode"),
                            "country": "POL",
                            "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                            "number": "789-789-645",
                            "photo": "",
                        },
                        "approve_status": False,
                    }
                ],
                "documents_to_remove": [
                    {"value": cls.id_to_base64(cls.national_id.id, "DocumentNode"), "approve_status": False},
                    {"value": cls.id_to_base64(cls.birth_certificate.id, "DocumentNode"), "approve_status": False},
                ],
                "flex_fields": {},
            },
        )

        cls.household_data_change_grievance_ticket = GrievanceTicketFactory(
            id="72ee7d98-6108-4ef0-85bd-2ef20e1d5410",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            admin2=cls.admin_area_1,
            business_area=cls.business_area,
        )
        TicketHouseholdDataUpdateDetailsFactory(
            ticket=cls.household_data_change_grievance_ticket,
            household=cls.household_one,
            household_data={
                "village": {"value": "Test Village"},
                "size": {"value": 19},
                "flex_fields": {},
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_APPROVE_DATA_CHANGE],
            ),
            ("without_permission", []),
        ]
    )
    def test_approve_add_individual(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_ADD_INDIVIDUAL_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(self.add_individual_grievance_ticket.id, "GrievanceTicketNode"),
                "approveStatus": True,
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_APPROVE_DATA_CHANGE],
            ),
            ("without_permission", []),
        ]
    )
    def test_approve_update_individual(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_INDIVIDUAL_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.individual_data_change_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "individualApproveData": json.dumps({"givenName": True, "fullName": True, "familyName": True}),
                "approvedDocumentsToCreate": [0],
                "approvedDocumentsToEdit": [0],
                "approvedDocumentsToRemove": [0],
                "approvedIdentitiesToCreate": [],
                "approvedIdentitiesToEdit": [],
                "approvedIdentitiesToRemove": [],
                "approvedPaymentChannelsToCreate": [],
                "approvedPaymentChannelsToEdit": [],
                "approvedPaymentChannelsToRemove": [],
                "flexFieldsApproveData": json.dumps({}),
            },
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_APPROVE_DATA_CHANGE],
            ),
            ("without_permission", []),
        ]
    )
    def test_approve_update_household(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.APPROVE_HOUSEHOLD_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.household_data_change_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "householdApproveData": json.dumps({"village": True}),
                "flexFieldsApproveData": json.dumps({}),
            },
        )
