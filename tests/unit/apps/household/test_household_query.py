from typing import Any, List

from django.conf import settings

import pytest
from constance.test import override_config
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    RoleFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    create_afghanistan,
    generate_data_collecting_types,
)
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    HouseholdFactory,
    create_household,
)
from hct_mis_api.apps.household.models import DocumentType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index
from hct_mis_api.apps.utils.models import MergeStatusModel

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


ALL_HOUSEHOLD_QUERY = """
      query AllHouseholds($search: String, $documentType: String, $documentNumber: String, $program: ID) {
        allHouseholds(search: $search, documentType: $documentType, documentNumber: $documentNumber, orderBy: "size", program: $program, businessArea: "afghanistan", rdiMergeStatus: "MERGED") {
          edges {
            node {
              size
              countryOrigin
              address
            }
          }
        }
      }
    """

ALL_HOUSEHOLD_QUERY_RANGE = """
    query AllHouseholds($program: ID){
      allHouseholds(
        orderBy: "size",
        size: "{\\"min\\": 3, \\"max\\": 9}",
        businessArea: "afghanistan",
        program: $program,
        rdiMergeStatus: "MERGED"
      ) {
        edges {
          node {
            size
            countryOrigin
            address
          }
        }
      }
    }
    """

ALL_HOUSEHOLD_QUERY_MIN = """
    query AllHouseholds($program: ID){
      allHouseholds(orderBy: "size", size: "{\\"min\\": 3}", businessArea: "afghanistan", program: $program, rdiMergeStatus: "MERGED") {
        edges {
          node {
            size
            countryOrigin
            address
          }
        }
      }
    }
    """
ALL_HOUSEHOLD_QUERY_MAX = """
    query AllHouseholds($program: ID){
      allHouseholds(orderBy: "size", size: "{\\"max\\": 9}", businessArea: "afghanistan", program: $program, rdiMergeStatus: "MERGED") {
        edges {
          node {
            size
            countryOrigin
            address
          }
        }
      }
    }
    """

ALL_HOUSEHOLD_FILTER_PROGRAMS_QUERY = """
    query AllHouseholds {
      allHouseholds(businessArea: "afghanistan") {
        edges {
          node {
            size
            countryOrigin
            address
            programs {
              totalCount
            }
          }
        }
      }
    }
    """

HOUSEHOLD_QUERY = """
    query Household($id: ID!) {
      household(id: $id) {
        size
        countryOrigin
        address
        adminArea {
          pCode
        }
        adminAreaTitle
        admin1 {
          pCode
        }
        admin2 {
          pCode
        }
      }
    }
    """


@override_config(USE_ELASTICSEARCH_FOR_HOUSEHOLDS_SEARCH=True)
class TestHouseholdQuery(APITestCase):
    databases = "__all__"
    fixtures = (
        f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",
        f"{settings.PROJECT_ROOT}/apps/household/fixtures/documenttype.json",
    )

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.partner = PartnerFactory(name="NOT_UNICEF")
        cls.user = UserFactory.create(partner=cls.partner)
        cls.business_area = create_afghanistan()

        cls.partner_no_access = PartnerFactory(name="Partner No Access")
        cls.user_with_no_access = UserFactory(partner=cls.partner_no_access)

        family_sizes_list = (2, 4, 5, 1, 3, 11, 14)
        generate_data_collecting_types()
        partial = DataCollectingType.objects.get(code="partial_individuals")
        cls.program_one = ProgramFactory(
            name="Test program ONE",
            business_area=cls.business_area,
            status=Program.ACTIVE,
            data_collecting_type=partial,
        )
        cls.program_two = ProgramFactory(
            name="Test program TWO",
            business_area=cls.business_area,
            status=Program.ACTIVE,
            data_collecting_type=partial,
        )
        cls.program_draft = ProgramFactory(
            name="Test program DRAFT",
            business_area=cls.business_area,
            status=Program.DRAFT,
        )
        cls.program_other = ProgramFactory(
            name="Test program OTHER",
            business_area=cls.business_area,
            status=Program.ACTIVE,
        )

        cls.households = []
        country_origin = geo_models.Country.objects.filter(iso_code2="PL").first()

        for index, family_size in enumerate(family_sizes_list):
            if index % 2:
                program = cls.program_one
            else:
                program = cls.program_two

            (household, individuals) = create_household(
                {
                    "size": family_size,
                    "address": f"Lorem Ipsum {family_size}",
                    "country_origin": country_origin,
                    "program": program,
                },
            )
            household.save()

            area_type_level_1 = AreaTypeFactory(
                name="State1",
                area_level=1,
            )
            area_type_level_2 = AreaTypeFactory(
                name="State2",
                area_level=2,
            )
            cls.area1 = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code="area1")
            cls.area2 = AreaFactory(name="City Test2", area_type=area_type_level_2, p_code="area2", parent=cls.area1)
            household.set_admin_areas(cls.area2)

            cls.households.append(household)

        household = cls.households[0]
        household.detail_id = 123
        household.save()
        household.refresh_from_db()
        household.head_of_household.phone_no = "+18663567905"
        household.head_of_household.save()
        household.head_of_household.refresh_from_db()

        # household in program that cls.user does not have access to
        create_household(
            {
                "size": 5,
                "address": "Lorem Ipsumm 5",
                "country_origin": country_origin,
                "program": cls.program_other,
            },
        )

        DocumentFactory(
            document_number="123-456-789",
            type=DocumentType.objects.get(key="national_id"),
            individual=household.head_of_household,
        )

        role = RoleFactory(name="Test Role", permissions=[Permissions.PROGRAMME_CREATE])
        cls.add_partner_role_in_business_area(
            cls.partner,
            cls.business_area,
            [role],
        )
        for program in [cls.program_one, cls.program_two, cls.program_draft]:
            cls.update_partner_access_to_program(cls.partner, program, [cls.households[0].admin_area])

        # just add one PENDING HH to be sure filters works correctly
        HouseholdFactory(
            size=2,
            address="Lorem Ipsum",
            rdi_merge_status=MergeStatusModel.PENDING,
            program=cls.program_one,
        )

        # remove after data migration
        BusinessAreaFactory(name="Democratic Republic of Congo")
        BusinessAreaFactory(name="Sudan")
        BusinessAreaFactory(name="Trinidad & Tobago")
        BusinessAreaFactory(name="Slovakia")
        BusinessAreaFactory(name="Sri Lanka")
        rebuild_search_index()

    @parameterized.expand(
        [
            ("all_with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], ALL_HOUSEHOLD_QUERY),
            ("all_without_permission", [], ALL_HOUSEHOLD_QUERY),
            (
                "all_range_with_permission",
                [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
                ALL_HOUSEHOLD_QUERY_RANGE,
            ),
            ("all_range_without_permission", [], ALL_HOUSEHOLD_QUERY_RANGE),
            ("all_min_with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], ALL_HOUSEHOLD_QUERY_MIN),
            ("all_max_with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], ALL_HOUSEHOLD_QUERY_MAX),
        ]
    )
    def test_household_query_all(self, _: Any, permissions: List[Permissions], query_string: str) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=query_string,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"program": self.id_to_base64(self.program_two.id, "ProgramNode")},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS]),
            ("without_permission", []),
        ]
    )
    def test_household_query_single(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.households[0].id, "HouseholdNode")},
        )

    @parameterized.expand(
        [
            (None, None),
            ("detail_id", "test1"),
            ("enumerator_rec_id", 123),
        ]
    )
    def test_household_query_single_import_id(self, field_name: str, field_value: str) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS], self.business_area
        )
        household = self.households[0]

        query = """
        query Household($id: ID!) {
          household(id: $id) {
            importId
          }
        }
        """
        household.detail_id = None
        household.enumerator_rec_id = None

        if field_name is not None:
            setattr(household, field_name, field_value)

        household.unicef_id = "HH-123123"
        household.save()

        self.snapshot_graphql_request(
            request_string=query,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(household.id, "HouseholdNode")},
        )

    def test_household_query_single_different_program_in_header(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_one.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.households[0].id, "HouseholdNode")},
        )

    def test_household_query_draft(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_draft.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_households_by_search_household_id_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        household = self.households[0]

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={
                "search": f"{household.unicef_id}",
                "program": self.id_to_base64(self.program_two.id, "ProgramNode"),
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_households_by_search_individual_id_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        household = self.households[0]

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": f"{household.head_of_household.unicef_id}"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_households_by_search_full_name_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        household = self.households[0]

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": f"{household.head_of_household.full_name}"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_households_by_search_phone_no_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": "+18663567905"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_households_by_national_id_no_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"documentNumber": "123-456-789", "documentType": "national_id"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_households_search_without_search_type(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={
                "search": "123-456-789",
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_households_search_incorrect_kobo_asset_id(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": "qwerty12345"},
        )

    def test_household_query_all_for_all_programs(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
        )

    def test_household_query_all_for_all_programs_user_with_no_program_access(self) -> None:
        self.create_user_role_with_permissions(
            self.user_with_no_access, [Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=ALL_HOUSEHOLD_QUERY,
            context={
                "user": self.user_with_no_access,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
        )
