from datetime import date
from parameterized import parameterized

from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import AdminAreaLevelFactory, AdminAreaFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import SINGLE, FEMALE, WIDOWED, RELATIONSHIP_UNKNOWN, ROLE_NO_ROLE
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

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CREATE],
            ),
            ("without_permission", []),
        ]
    )
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
