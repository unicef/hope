from typing import Any, List
from unittest import skip

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    create_afghanistan,
    generate_data_collecting_types,
)
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
)
from hct_mis_api.apps.household.models import DocumentType, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.one_time_scripts.migrate_data_to_representations import (
    migrate_data_to_representations,
)


class TestIndividualQuery(APITestCase):
    databases = "__all__"

    ALL_INDIVIDUALS_QUERY = """
    query AllIndividuals($search: String, $searchType: String, $program: ID) {
      allIndividuals(businessArea: "afghanistan", search: $search, searchType: $searchType, program: $program, orderBy:"id") {
        edges {
          node {
            fullName
            givenName
            familyName
            phoneNo
            phoneNoValid
            birthDate
          }
        }
      }
    }
    """

    INDIVIDUAL_QUERY = """
    query Individual($id: ID!) {
      individual(id: $id) {
        fullName
        givenName
        familyName
        phoneNo
        birthDate
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.partner = PartnerFactory()
        cls.user = UserFactory(partner=cls.partner)

        cls.business_area = create_afghanistan()
        BusinessAreaFactory(name="Democratic Republic of Congo")
        BusinessAreaFactory(name="Sudan")
        # Unknown unassigned rules setup
        BusinessAreaFactory(name="Trinidad & Tobago")
        BusinessAreaFactory(name="Slovakia")
        BusinessAreaFactory(name="Sri Lanka")

        generate_data_collecting_types()
        partial = DataCollectingType.objects.get(code="partial_individuals")

        cls.program = ProgramFactory(
            name="Test program ONE",
            business_area=cls.business_area,
            status=Program.ACTIVE,
            data_collecting_type=partial,
        )
        cls.program_draft = ProgramFactory(
            name="Test program DRAFT",
            business_area=cls.business_area,
            status=Program.ACTIVE,
            data_collecting_type=partial,
        )
        cls.update_user_partner_perm_for_program(cls.user, cls.business_area, cls.program)
        cls.update_user_partner_perm_for_program(cls.user, cls.business_area, cls.program_draft)

        cls.household_one = HouseholdFactory.build(business_area=cls.business_area)
        cls.household_one.household_collection.save()
        cls.household_one.registration_data_import.imported_by.save()
        cls.household_one.registration_data_import.save()

        cls.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "id": "ffb2576b-126f-42de-b0f5-ef889b7bc1fe",
                "program": cls.program,
                "registration_id": 1,
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
                "id": "8ef39244-2884-459b-ad14-8d63a6fe4a4a",
                "program": cls.program,
            },
            {
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "phone_no": "(548)313-1700-902",
                "birth_date": "1983-12-21",
                "id": "badd2d2d-7ea0-46f1-bb7a-69f385bacdcd",
                "program": cls.program,
            },
            {
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "phone_no": "(228)231-5473",
                "birth_date": "1973-03-23",
                "id": "2c1a26a3-2827-4a99-9000-a88091bf017c",
                "program": cls.program,
            },
            {
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "phone_no": "001-296-358-5428-607",
                "birth_date": "1969-11-29",
                "id": "0fc995cc-ea72-4319-9bfe-9c9fda3ec191",
                "program": cls.program,
            },
            {
                "full_name": "James Bond",
                "given_name": "James",
                "family_name": "Bond",
                "phone_no": "(007)682-4596",
                "birth_date": "1965-06-26",
                "id": "972fdac5-d1bf-44ed-a4a5-14805b5dc606",
                "program": cls.program,
            },
            {
                "full_name": "Peter Parker",
                "given_name": "Peter",
                "family_name": "Parker",
                "phone_no": "(666)682-2345",
                "birth_date": "1978-01-02",
                "id": "430924a6-273e-4018-95e7-b133afa5e1b9",
                "program": cls.program,
            },
        ]

        cls.individuals = [
            IndividualFactory(household=cls.household_one, **individual)
            for index, individual in enumerate(cls.individuals_to_create)
        ]
        cls.household_one.head_of_household = cls.individuals[0]
        cls.household_one.program = cls.program
        cls.individuals_from_hh_one = [ind for ind in cls.individuals if ind.household == cls.household_one]
        # cls.individuals_from_hh_two = [ind for ind in cls.individuals if ind.household == household_two]
        cls.household_one.head_of_household = cls.individuals_from_hh_one[0]
        # household_two.head_of_household = cls.individuals_from_hh_two[1]
        cls.household_one.save()

        cls.bank_account_info = BankAccountInfoFactory(
            individual=cls.individuals[5], bank_name="ING", bank_account_number=11110000222255558888999925
        )

        cls.individual_unicef_id_to_search = Individual.objects.get(full_name="Benjamin Butler").unicef_id
        cls.household_unicef_id_to_search = Individual.objects.get(full_name="Benjamin Butler").household.unicef_id

        DocumentTypeFactory(key="national_id")
        DocumentTypeFactory(key="national_passport")
        DocumentTypeFactory(key="tax_id")
        DocumentTypeFactory(key="birth_certificate")
        DocumentTypeFactory(key="disability_card")
        DocumentTypeFactory(key="drivers_license")

        cls.bank_account_info = BankAccountInfoFactory(
            individual=cls.individuals[5], bank_name="ING", bank_account_number=11110000222255558888999925
        )

        cls.individual_unicef_id_to_search = Individual.objects.get(full_name="Benjamin Butler").unicef_id
        cls.household_unicef_id_to_search = Individual.objects.get(full_name="Benjamin Butler").household.unicef_id

        DocumentTypeFactory(key="national_id")
        DocumentTypeFactory(key="national_passport")
        DocumentTypeFactory(key="tax_id")
        DocumentTypeFactory(key="birth_certificate")
        DocumentTypeFactory(key="disability_card")
        DocumentTypeFactory(key="drivers_license")

        cls.national_id = DocumentFactory(
            document_number="123-456-789",
            type=DocumentType.objects.get(key="national_id"),
            individual=cls.individuals[0],
        )

        cls.national_passport = DocumentFactory(
            document_number="111-222-333",
            type=DocumentTypeFactory(key="national_passport"),
            individual=cls.individuals[1],
        )

        cls.birth_certificate = DocumentFactory(
            document_number="111222333",
            type=DocumentType.objects.get(key="birth_certificate"),
            individual=cls.individuals[4],
        )

        cls.disability_card = DocumentFactory(
            document_number="10000000000",
            type=DocumentType.objects.get(key="disability_card"),
            individual=cls.individuals[6],
        )

        cls.drivers_license = DocumentFactory(
            document_number="1234567890",
            type=DocumentType.objects.get(key="drivers_license"),
            individual=cls.individuals[0],
        )

        cls.tax_id = DocumentFactory(
            document_number="666-777-888", type=DocumentType.objects.get(key="tax_id"), individual=cls.individuals[2]
        )

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

        cls.household_one.set_admin_areas(cls.area2)

        cls.partner.permissions = {
            str(cls.business_area.id): {
                "programs": {
                    str(cls.program.id): [str(cls.household_one.admin_area.id)],
                    str(cls.program_draft.id): [str(cls.household_one.admin_area.id)],
                }
            }
        }
        cls.partner.save()

        # remove after data migration
        migrate_data_to_representations()

        super().setUpTestData()

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    @skip(reason="Remove 2nd program after merging to develop")
    def test_individual_query_all(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS]),
            ("without_permission", []),
        ]
    )
    def test_individual_query_single(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.INDIVIDUAL_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.individuals[0].id, "IndividualNode")},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    @skip("After merging GPF, remove 2nd program")
    def test_individual_programme_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_BY_PROGRAMME_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_two.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"programs": [self.program_two.id]},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_full_name_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        # Should be Jenna Franklin
        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": "Jenna Franklin", "searchType": "full_name"},
        )

    def test_individual_query_draft(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], self.business_area
        )

        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_draft.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"program": self.id_to_base64(self.program_draft.id, "ProgramNode")},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_phone_no_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        # Should be Robin Ford
        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": "(953)682-4596", "searchType": "phone_no"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_national_id_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        # Should be Benjamin Butler
        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": f"{self.national_id.document_number}", "searchType": "national_id"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_national_passport_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        # Should be Robin Ford
        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": f"{self.national_passport.document_number}", "searchType": "national_passport"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_tax_id_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        # Should be Timothy Perry
        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": "666-777-888", "searchType": "tax_id"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_registration_id_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": "1", "searchType": "registration_id"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_without_search_type(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={
                "search": "1",
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_bank_account_number_filter(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        # Should be James Bond
        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": self.bank_account_info.bank_account_number, "searchType": "bank_account_number"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_birth_certificate_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        # Should be Jenna Franklin
        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": self.birth_certificate.document_number, "searchType": "birth_certificate"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_disability_card_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        # Should be Peter Parker
        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": self.disability_card.document_number, "searchType": "disability_card"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_drivers_license_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        # Should be Benjamin Butler
        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": self.drivers_license.document_number, "searchType": "drivers_license"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_registration_id_filter_with_search_type(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"search": "1", "searchType": "registration_id"},
        )
