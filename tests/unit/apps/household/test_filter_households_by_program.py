from typing import Any, List

from django.conf import settings

from parameterized import parameterized

from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.utils import encode_id_base64_required
from tests.extras.test_utils.factories.household import create_household
from tests.extras.test_utils.factories.program import ProgramFactory
from tests.extras.test_utils.factories.registration_data import RegistrationDataImportFactory


class TestFilterHouseholdsByProgram(APITestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    QUERY = """
        query AllHouseholds($program: ID){
          allHouseholds(program: $program, orderBy: "size", businessArea: "afghanistan", rdiMergeStatus: "MERGED") {
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
        query AllHouseholds($program: ID, $rdiId: String){
          allHouseholds(program: $program, orderBy: "size", businessArea: "afghanistan", rdiMergeStatus: "MERGED", rdiId: $rdiId) {
            edges {
              node {
                headOfHousehold {
                  fullName
                }
                program {
                  name
                }
                hasDuplicatesForRdi
              }
            }
          }
        }
        """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.partner = PartnerFactory(name="Partner")
        cls.user = UserFactory(partner=cls.partner)
        cls.business_area = create_afghanistan()
        cls.program1 = ProgramFactory(name="Test program ONE", business_area=cls.business_area, status="ACTIVE")
        cls.program2 = ProgramFactory(name="Test program TWO", business_area=cls.business_area, status="ACTIVE")
        cls.update_partner_access_to_program(cls.partner, cls.program1)
        cls.update_partner_access_to_program(cls.partner, cls.program2)
        create_household({"program": cls.program1})
        create_household({"program": cls.program1})
        create_household({"program": cls.program2})

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_filter_households(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        headers = {
            "Business-Area": self.business_area.slug,
            "Program": self.id_to_base64(self.program1.id, "ProgramNode"),
        }
        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user, "headers": headers},
            variables={
                "program": self.id_to_base64(self.program1.id, "ProgramNode"),
            },
        )

    def test_filter_household_query_by_rdi_id(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], self.business_area, self.program1
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
        self.assertEqual(household.head_of_household.full_name, "TEST User")

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
