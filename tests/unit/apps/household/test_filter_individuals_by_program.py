from typing import Any, List
from unittest import mock

from parameterized import parameterized

from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.utils import encode_id_base64_required
from tests.extras.test_utils.factories.household import (
    HouseholdFactory,
    IndividualFactory,
    create_household,
)
from hct_mis_api.apps.household.models import DUPLICATE
from tests.extras.test_utils.factories.program import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory


@mock.patch(
    "hct_mis_api.apps.registration_data.signals.increment_registration_data_import_version_cache", return_value=None
)
class TestFilterIndividualsByProgram(APITestCase):
    QUERY = """
    query AllIndividuals($program: ID){
      allIndividuals(businessArea: "afghanistan", program: $program, rdiMergeStatus: "MERGED") {
        edges {
          node {
            program {
              name
            }
          }
        }
      }
    }
    """
    QUERY_WITH_RDI_FILTER = """
        query AllIndividuals($program: ID, $rdiId: String){
          allIndividuals(businessArea: "afghanistan", program: $program, rdiMergeStatus: "MERGED", rdiId: $rdiId) {
            edges {
              node {
                fullName
                program {
                  name
                }
                identities {
                  totalCount
                  edges {
                    node {
                      number
                    }
                  }
                }
              }
            }
          }
        }
        """
    QUERY_WITH_DUPLICATE_FILTER = """
        query AllIndividuals($program: ID, $duplicatesOnly: Boolean){
          allIndividuals(businessArea: "afghanistan", program: $program, rdiMergeStatus: "MERGED", duplicatesOnly: $duplicatesOnly) {
            edges {
              node {
                deduplicationGoldenRecordStatus
                program {
                  name
                }
              }
            }
          }
        }
        """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.partner = PartnerFactory(name="TestPartner")
        cls.user = UserFactory(partner=cls.partner)
        cls.business_area = create_afghanistan()
        cls.program1 = ProgramFactory(name="Test program ONE", business_area=cls.business_area, status="ACTIVE")
        cls.program2 = ProgramFactory(name="Test program TWO", business_area=cls.business_area, status="ACTIVE")
        cls.update_partner_access_to_program(cls.partner, cls.program1)
        cls.update_partner_access_to_program(cls.partner, cls.program2)

        household_one = HouseholdFactory.build(business_area=cls.business_area, program=cls.program1)
        household_two = HouseholdFactory.build(business_area=cls.business_area, program=cls.program2)
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.program = cls.program1
        household_one.registration_data_import.save()
        household_two.registration_data_import.imported_by.save()
        household_two.registration_data_import.program = cls.program2
        household_two.registration_data_import.save()

        individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "id": "ffb2576b-126f-42de-b0f5-ef889b7bc1fe",
                "program": cls.program1,
                "household": household_one,
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
                "id": "8ef39244-2884-459b-ad14-8d63a6fe4a4a",
                "program": cls.program2,
                "household": household_two,
            },
            {
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "phone_no": "(548)313-1700-902",
                "birth_date": "1983-12-21",
                "id": "badd2d2d-7ea0-46f1-bb7a-69f385bacdcd",
                "program": cls.program1,
                "household": household_one,
            },
            {
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "phone_no": "(228)231-5473",
                "birth_date": "1973-03-23",
                "id": "2c1a26a3-2827-4a99-9000-a88091bf017c",
                "program": cls.program2,
                "household": household_two,
            },
            {
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "phone_no": "001-296-358-5428-607",
                "birth_date": "1969-11-29",
                "id": "0fc995cc-ea72-4319-9bfe-9c9fda3ec191",
                "program": cls.program1,
                "household": household_one,
            },
        ]

        individuals = [IndividualFactory(**individual) for individual in individuals_to_create]
        household_one.head_of_household = individuals[0]
        household_two.head_of_household = individuals[1]
        household_one.household_collection.save()
        household_one.save()
        household_two.household_collection.save()
        household_two.save()

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_individual_query_all(self, _mock: Any, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program1)

        headers = {
            "Business-Area": self.business_area.slug,
            "Program": self.id_to_base64(self.program1.id, "ProgramNode"),
        }
        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user, "headers": headers},
            variables={"program": self.id_to_base64(self.program1.id, "ProgramNode")},
        )

    def test_individual_query_rdi_id(self, _mock: Any) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], self.business_area, self.program1
        )
        rdi = RegistrationDataImportFactory(imported_by=self.user, business_area=self.business_area)
        # create new HH and IND with new RDI
        household, individuals = create_household(
            {
                "registration_data_import": rdi,
                "program": self.program1,
                "size": 1,
            },
            {"full_name": "TEST User", "given_name": "TEST", "family_name": "User", "registration_data_import": rdi},
        )
        individual = individuals[0]
        self.assertEqual(individual.full_name, "TEST User")

        rdi_id_str = encode_id_base64_required(rdi.id, "RegistrationDataImport")
        headers = {
            "Business-Area": self.business_area.slug,
            "Program": self.id_to_base64(self.program1.id, "ProgramNode"),
        }
        self.snapshot_graphql_request(
            request_string=self.QUERY_WITH_RDI_FILTER,
            context={"user": self.user, "headers": headers},
            variables={
                "program": self.id_to_base64(self.program1.id, "ProgramNode"),
                "rdiId": rdi_id_str,
            },
        )

    def test_individual_query_filter_by_duplicates_only(self, _mock: Any) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], self.business_area, self.program1
        )
        rdi = RegistrationDataImportFactory(imported_by=self.user, business_area=self.business_area)
        # create new HH and IND with new RDI
        household, individuals = create_household(
            {
                "registration_data_import": rdi,
                "program": self.program1,
                "size": 2,
            },
            {"full_name": "TEST User", "given_name": "TEST", "family_name": "User", "registration_data_import": rdi},
        )
        individual = individuals[0]
        self.assertEqual(individual.full_name, "TEST User")

        headers = {
            "Business-Area": self.business_area.slug,
            "Program": self.id_to_base64(self.program1.id, "ProgramNode"),
        }
        self.snapshot_graphql_request(
            request_string=self.QUERY_WITH_DUPLICATE_FILTER,
            context={"user": self.user, "headers": headers},
            variables={
                "program": self.id_to_base64(self.program1.id, "ProgramNode"),
                "duplicatesOnly": False,
            },
        )
        # upd individual
        individual.deduplication_golden_record_status = DUPLICATE
        individual.save()

        self.snapshot_graphql_request(
            request_string=self.QUERY_WITH_DUPLICATE_FILTER,
            context={"user": self.user, "headers": headers},
            variables={
                "program": self.id_to_base64(self.program1.id, "ProgramNode"),
                "duplicatesOnly": True,
            },
        )
