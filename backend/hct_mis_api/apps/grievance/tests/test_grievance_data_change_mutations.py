from datetime import date
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command

from django_countries.fields import Country
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import AdminAreaFactory, AdminAreaLevelFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
)
from hct_mis_api.apps.household.models import (
    FEMALE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    RELATIONSHIP_UNKNOWN,
    ROLE_NO_ROLE,
    SINGLE,
    UNHCR,
    WIDOWED,
    Agency,
    DocumentType,
    IndividualIdentity,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestGrievanceCreateDataChangeMutation(APITestCase):
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

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        call_command("loadcountries")
        self.generate_document_types_for_all_countries()

        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=self.business_area,
        )
        self.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_level=area_type, p_code="dffgh565556")
        self.admin_area_2 = AdminAreaFactory(title="City Example", admin_area_level=area_type, p_code="fggtyjyj")
        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )
        program_two = ProgramFactory(
            name="Test program TWO",
            business_area=BusinessArea.objects.first(),
        )

        household_one = HouseholdFactory.build(id="07a901ed-d2a5-422a-b962-3570da1d5d07", size=3, country="AFG")
        household_two = HouseholdFactory.build(id="ac540aa1-5c7a-47d0-a013-32054e2af454")
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.save()
        household_two.registration_data_import.imported_by.save()
        household_two.registration_data_import.save()
        household_one.programs.add(program_one)
        household_two.programs.add(program_two)

        self.individuals_to_create = [
            {
                "id": "b6ffb227-a2dd-4103-be46-0c9ebe9f001a",
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "sex": FEMALE,
                "marital_status": WIDOWED,
                "estimated_birth_date": False,
                "relationship": RELATIONSHIP_UNKNOWN,
            },
            {
                "id": "e6b0acc8-f4db-4d70-8f50-c2080b3ba9ec",
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
                "sex": FEMALE,
                "marital_status": WIDOWED,
                "estimated_birth_date": False,
                "relationship": RELATIONSHIP_UNKNOWN,
            },
            {
                "id": "667be49c-6620-4381-a69a-211ba9f7d8c8",
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "phone_no": "(548)313-1700-902",
                "birth_date": "1983-12-21",
                "sex": FEMALE,
                "marital_status": WIDOWED,
                "estimated_birth_date": False,
                "relationship": RELATIONSHIP_UNKNOWN,
            },
            {
                "id": "ef52d4d7-3142-4d51-a31b-2ad231120c58",
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "phone_no": "(228)231-5473",
                "birth_date": "1973-03-23",
                "sex": FEMALE,
                "marital_status": WIDOWED,
                "estimated_birth_date": False,
                "relationship": RELATIONSHIP_UNKNOWN,
            },
            {
                "id": "cb2e2e3a-d9c4-40ce-8777-707ca18d7fc8",
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "phone_no": "001-296-358-5428-607",
                "birth_date": "1969-11-29",
                "sex": FEMALE,
                "marital_status": WIDOWED,
                "estimated_birth_date": False,
                "relationship": RELATIONSHIP_UNKNOWN,
            },
        ]

        self.individuals = [
            IndividualFactory(household=household_one if index % 2 else household_two, **individual)
            for index, individual in enumerate(self.individuals_to_create)
        ]
        household_one.head_of_household = self.individuals[0]
        household_two.head_of_household = self.individuals[1]
        household_one.save()
        household_two.save()
        self.household_one = household_one

        national_id_type = DocumentType.objects.get(country=Country("POL"), type=IDENTIFICATION_TYPE_NATIONAL_ID)
        self.national_id = DocumentFactory.create(
            id="d367e431-b807-4c1f-a811-ef2e0d217cc4",
            type=national_id_type,
            document_number="789-789-645",
            individual=self.individuals[0],
        )

        unhcr_agency = Agency.objects.create(type="unhcr", label="UNHCR", country="POL")
        self.identity = IndividualIdentityFactory.create(
            id=1,
            agency=unhcr_agency,
            individual=self.individuals[0],
            number="1111",
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    @mock.patch("django.core.files.storage.default_storage.save", lambda filename, file: "test_file_name.jpg")
    def test_grievance_create_individual_data_change(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        variables = {
            "input": {
                "description": "Test",
                "businessArea": "afghanistan",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "issueType": 16,
                "category": 2,
                "consent": True,
                "language": "PL",
                "extras": {
                    "issueType": {
                        "addIndividualIssueTypeExtras": {
                            "household": self.id_to_base64(self.household_one.id, "HouseholdNode"),
                            "individualData": {
                                "givenName": "Test",
                                "fullName": "Test Test",
                                "familyName": "Romaniak",
                                "sex": "MALE",
                                "birthDate": date(year=1980, month=2, day=1).isoformat(),
                                "maritalStatus": SINGLE,
                                "estimatedBirthDate": False,
                                "relationship": RELATIONSHIP_UNKNOWN,
                                "role": ROLE_NO_ROLE,
                                "documents": [
                                    {
                                        "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                                        "country": "POL",
                                        "number": "123-123-UX-321",
                                        "photo": SimpleUploadedFile(name="test.jpg", content="".encode("utf-8")),
                                    }
                                ],
                                "identities": [
                                    {
                                        "agency": UNHCR,
                                        "country": "POL",
                                        "number": "2222",
                                    }
                                ],
                            },
                        }
                    }
                },
            }
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=variables,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    @mock.patch("django.core.files.storage.default_storage.save", lambda filename, file: "test_file_name.jpg")
    def test_grievance_update_individual_data_change(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        variables = {
            "input": {
                "description": "Test",
                "businessArea": "afghanistan",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "issueType": 14,
                "category": 2,
                "consent": True,
                "language": "PL",
                "extras": {
                    "issueType": {
                        "individualDataUpdateIssueTypeExtras": {
                            "individual": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
                            "individualData": {
                                "givenName": "Test",
                                "fullName": "Test Test",
                                "sex": "MALE",
                                "birthDate": date(year=1980, month=2, day=1).isoformat(),
                                "maritalStatus": SINGLE,
                                "documents": [
                                    {
                                        "type": IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
                                        "country": "POL",
                                        "number": "321-321-XU-987",
                                        "photo": SimpleUploadedFile(name="test.jpg", content="".encode("utf-8")),
                                    }
                                ],
                                "documentsToEdit": [
                                    {
                                        "id": self.id_to_base64(self.national_id.id, "DocumentNode"),
                                        "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                                        "country": "POL",
                                        "number": "321-321-XU-123",
                                        "photo": SimpleUploadedFile(name="test.jpg", content="".encode("utf-8")),
                                    }
                                ],
                                "identities": [
                                    {
                                        "agency": UNHCR,
                                        "country": "POL",
                                        "number": "2222",
                                    }
                                ],
                                "identitiesToEdit": [
                                    {
                                        "id": self.id_to_base64(self.identity.id, "IndividualIdentityNode"),
                                        "agency": UNHCR,
                                        "country": "POL",
                                        "number": "3333",
                                    }
                                ],
                            },
                        }
                    }
                },
            }
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=variables,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_grievance_delete_individual_data_change(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        variables = {
            "input": {
                "description": "Test",
                "businessArea": "afghanistan",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "issueType": 15,
                "category": 2,
                "consent": True,
                "language": "PL",
                "extras": {
                    "issueType": {
                        "individualDeleteIssueTypeExtras": {
                            "individual": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
                        }
                    }
                },
            }
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=variables,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_grievance_update_household_data_change(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.household_one.female_age_group_6_11_count = 2
        self.household_one.save()

        variables = {
            "input": {
                "description": "Test",
                "businessArea": "afghanistan",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "issueType": 13,
                "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
                "consent": True,
                "language": "PL",
                "extras": {
                    "issueType": {
                        "householdDataUpdateIssueTypeExtras": {
                            "household": self.id_to_base64(self.household_one.id, "HouseholdNode"),
                            "householdData": {
                                "femaleAgeGroup611Count": 14,
                                "country": "AFG",
                                "size": 4,
                            },
                        }
                    }
                },
            }
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=variables,
        )
