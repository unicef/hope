from datetime import date
from typing import Any, List
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command

import pytest
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
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
    DocumentType,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


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

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        call_command("loadcountries")
        cls.generate_document_types_for_all_countries()

        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory.create(partner=partner)
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        AreaFactory(name="City Test", area_type=area_type, p_code="dffgh565556")
        AreaFactory(name="City Example", area_type=area_type, p_code="fggtyjyj")

        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )
        program_two = ProgramFactory(
            name="Test program TWO",
            business_area=BusinessArea.objects.first(),
        )

        cls.program = ProgramFactory(
            status=Program.ACTIVE,
            business_area=BusinessArea.objects.first(),
        )
        cls.update_partner_access_to_program(partner, cls.program)

        household_one = HouseholdFactory.build(
            id="07a901ed-d2a5-422a-b962-3570da1d5d07", size=3, country=country, program=cls.program
        )
        household_one.household_collection.save()
        household_one.program.save()
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.program = household_one.program
        household_one.registration_data_import.save()
        household_one.programs.add(program_one)

        household_two = HouseholdFactory.build(id="ac540aa1-5c7a-47d0-a013-32054e2af454", program=cls.program)
        household_two.household_collection.save()
        household_two.program.save()
        household_two.registration_data_import.imported_by.save()
        household_two.registration_data_import.program = household_two.program
        household_two.registration_data_import.save()
        household_two.programs.add(program_two)

        cls.individuals_to_create = [
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

        cls.individuals = [
            IndividualFactory(
                household=household_one if index % 2 else household_two,
                program=household_one.program if index % 2 else household_two.program,
                **individual,
            )
            for index, individual in enumerate(cls.individuals_to_create)
        ]
        household_one.head_of_household = cls.individuals[0]
        household_two.head_of_household = cls.individuals[1]
        household_one.save()
        household_two.save()
        cls.household_one = household_one

        country_pl = geo_models.Country.objects.get(iso_code2="PL")
        national_id_type = DocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]
        )
        cls.national_id = DocumentFactory.create(
            country=country_pl,
            id="d367e431-b807-4c1f-a811-ef2e0d217cc4",
            type=national_id_type,
            document_number="789-789-645",
            individual=cls.individuals[0],
        )

        unhcr, _ = Partner.objects.get_or_create(name="UNHCR", defaults={"is_un": True})
        cls.identity = IndividualIdentityFactory.create(
            id=1,
            partner=unhcr,
            individual=cls.individuals[0],
            number="1111",
            country=country_pl,
        )

        area_type_level_1 = AreaTypeFactory(name="State1", area_level=1)
        cls.area = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code="area1")

        rebuild_search_index()

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
    def test_grievance_create_individual_data_change(self, _: Any, permissions: List[Permissions]) -> None:
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
                                        "key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
                                        "country": "POL",
                                        "number": "123-123-UX-321",
                                        "photo": SimpleUploadedFile(name="test.jpg", content=b""),
                                    }
                                ],
                                "identities": [
                                    {
                                        "partner": UNHCR,
                                        "country": "POL",
                                        "number": "2222",
                                    }
                                ],
                                "paymentChannels": [
                                    {
                                        "type": "BANK_TRANSFER",
                                        "bankName": "privatbank",
                                        "bankAccountNumber": 2356789789789789,
                                        "accountHolderName": "Holder Name 132",
                                        "bankBranchName": "newName 123",
                                    },
                                ],
                            },
                        }
                    }
                },
            }
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
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
    def test_grievance_update_individual_data_change(self, _: Any, permissions: List[Permissions]) -> None:
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
                                "preferredLanguage": "pl-pl",
                                "documents": [
                                    {
                                        "key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[
                                            IDENTIFICATION_TYPE_NATIONAL_PASSPORT
                                        ],
                                        "country": "POL",
                                        "number": "321-321-XU-987",
                                        "photo": SimpleUploadedFile(name="test.jpg", content=b""),
                                    }
                                ],
                                "documentsToEdit": [
                                    {
                                        "id": self.id_to_base64(self.national_id.id, "DocumentNode"),
                                        "key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
                                        "country": "POL",
                                        "number": "321-321-XU-123",
                                        "photo": SimpleUploadedFile(name="test.jpg", content=b""),
                                    }
                                ],
                                "identities": [
                                    {
                                        "partner": UNHCR,
                                        "country": "POL",
                                        "number": "2222",
                                    }
                                ],
                                "identitiesToEdit": [
                                    {
                                        "id": self.id_to_base64(self.identity.id, "IndividualIdentityNode"),
                                        "partner": UNHCR,
                                        "country": "POL",
                                        "number": "3333",
                                    }
                                ],
                                "disability": "disabled",
                            },
                        }
                    }
                },
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
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
    def test_create_payment_channel_for_individual(self, _: Any, permissions: List[Permissions]) -> None:
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
                                "paymentChannels": [
                                    {
                                        "type": "BANK_TRANSFER",
                                        "bankName": "privatbank",
                                        "bankAccountNumber": 2356789789789789,
                                        "accountHolderName": "Holder Name 333",
                                        "bankBranchName": "New Branch Name 333",
                                    },
                                ],
                            },
                        }
                    }
                },
            }
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
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
    def test_edit_payment_channel_for_individual(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        bank_account = BankAccountInfoFactory(
            id="413b2a07-4bc1-43a7-80e6-91abb486aa9d",
            individual=self.individuals[0],
            bank_name="privatbank",
            bank_account_number=2356789789789789,
            account_holder_name="Old Holder Name",
            bank_branch_name="BranchSantander",
        )

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
                                "paymentChannelsToEdit": [
                                    {
                                        "id": self.id_to_base64(bank_account.id, "BankAccountInfoNode"),
                                        "type": "BANK_TRANSFER",
                                        "bankName": "privatbank",
                                        "bankAccountNumber": 1111222233334444,
                                        "accountHolderName": "Holder Name NEW 2",
                                        "bankBranchName": "New Name NEW 2",
                                    },
                                ],
                            },
                        }
                    }
                },
            }
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
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
    def test_grievance_delete_individual_data_change(self, _: Any, permissions: List[Permissions]) -> None:
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
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
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
    def test_grievance_update_household_data_change(self, _: Any, permissions: List[Permissions]) -> None:
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
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
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
    def test_grievance_delete_household_data_change(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        variables = {
            "input": {
                "description": "Test",
                "businessArea": "afghanistan",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "issueType": 17,
                "category": 2,
                "consent": True,
                "language": "PL",
                "extras": {
                    "issueType": {
                        "householdDeleteIssueTypeExtras": {
                            "household": self.id_to_base64(self.household_one.id, "HouseholdNode"),
                        }
                    }
                },
            }
        }
        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=variables,
        )

    def test_grievance_create_household_data_change_with_admin_area(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.business_area)

        variables = {
            "input": {
                "businessArea": self.business_area.slug,
                "description": "AreaTest",
                "category": 2,
                "issueType": 13,
                "consent": True,
                "language": "",
                "extras": {
                    "issueType": {
                        "householdDataUpdateIssueTypeExtras": {
                            "household": self.id_to_base64(self.household_one.id, "HouseholdNode"),
                            "householdData": {"adminAreaTitle": self.area.p_code, "flexFields": {}},
                        }
                    }
                },
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_DATA_CHANGE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=variables,
        )
