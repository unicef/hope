from typing import Any, List
from unittest import skip

import pytest
from constance.test import override_config
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
    generate_data_collecting_types,
)
from hct_mis_api.apps.core.models import DataCollectingType, PeriodicFieldData
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import DocumentType, Individual
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismDataFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import DeliveryMechanism
from hct_mis_api.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index
from hct_mis_api.apps.utils.models import MergeStatusModel

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@override_config(USE_ELASTICSEARCH_FOR_INDIVIDUALS_SEARCH=True)
class TestIndividualQuery(APITestCase):
    databases = "__all__"

    ALL_INDIVIDUALS_QUERY = """
    query AllIndividuals($search: String, $documentType: String, $documentNumber: String, $program: ID) {
      allIndividuals(businessArea: "afghanistan", search: $search, documentType: $documentType, documentNumber: $documentNumber, program: $program, orderBy:"id", rdiMergeStatus: "MERGED") {
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
        super().setUpTestData()
        cls.partner = PartnerFactory(name="Test123")
        cls.user = UserFactory(partner=cls.partner)

        cls.partner_no_access = PartnerFactory(name="Partner No Access")
        cls.user_with_no_access = UserFactory(partner=cls.partner_no_access)

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
            status=Program.DRAFT,
            data_collecting_type=partial,
        )
        cls.program_other = ProgramFactory(
            name="Test program OTHER",
            business_area=cls.business_area,
            status=Program.ACTIVE,
            data_collecting_type=partial,
        )

        cls.household_one = HouseholdFactory.build(business_area=cls.business_area, program=cls.program)
        cls.household_one.household_collection.save()
        cls.household_one.registration_data_import.imported_by.save()
        cls.household_one.registration_data_import.program = cls.program
        cls.household_one.registration_data_import.save()

        cls.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "id": "ffb2576b-126f-42de-b0f5-ef889b7bc1fe",
                "registration_id": 1,
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
                "id": "8ef39244-2884-459b-ad14-8d63a6fe4a4a",
            },
            {
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "phone_no": "(548)313-1700-902",
                "birth_date": "1983-12-21",
                "id": "badd2d2d-7ea0-46f1-bb7a-69f385bacdcd",
            },
            {
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "phone_no": "(228)231-5473",
                "birth_date": "1973-03-23",
                "id": "2c1a26a3-2827-4a99-9000-a88091bf017c",
            },
            {
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "phone_no": "001-296-358-5428-607",
                "birth_date": "1969-11-29",
                "id": "0fc995cc-ea72-4319-9bfe-9c9fda3ec191",
            },
            {
                "full_name": "James Bond",
                "given_name": "James",
                "family_name": "Bond",
                "phone_no": "(007)682-4596",
                "birth_date": "1965-06-26",
                "id": "972fdac5-d1bf-44ed-a4a5-14805b5dc606",
            },
            {
                "full_name": "Peter Parker",
                "given_name": "Peter",
                "family_name": "Parker",
                "phone_no": "(666)682-2345",
                "birth_date": "1978-01-02",
                "id": "430924a6-273e-4018-95e7-b133afa5e1b9",
            },
        ]

        cls.individuals = [
            IndividualFactory(household=cls.household_one, program=cls.program, **individual)
            for index, individual in enumerate(cls.individuals_to_create)
        ]
        cls.individuals_from_hh_one = [ind for ind in cls.individuals if ind.household == cls.household_one]
        # cls.individuals_from_hh_two = [ind for ind in cls.individuals if ind.household == household_two]
        cls.household_one.head_of_household = cls.individuals_from_hh_one[0]
        # household_two.head_of_household = cls.individuals_from_hh_two[1]
        cls.household_one.save()

        # individual in program that cls.user does not have access to
        cls.household_2 = HouseholdFactory.build(business_area=cls.business_area, program=cls.program)
        cls.household_2.household_collection.save()
        cls.household_2.registration_data_import.imported_by.save()
        cls.household_2.registration_data_import.program = cls.program
        cls.household_2.registration_data_import.save()
        cls.individual_to_create_2_data = {
            "full_name": "Tester Test",
            "given_name": "Tester",
            "family_name": "Test",
            "phone_no": "(953)681-4591",
            "birth_date": "1943-07-30",
            "id": "8ff39244-2884-459b-ad14-8d63a6fe4a4a",
        }
        cls.individual_2 = IndividualFactory(
            household=cls.household_2,
            program=cls.program_other,
            **cls.individual_to_create_2_data,
        )
        cls.household_2.head_of_household = cls.individual_2
        cls.household_2.save()

        cls.bank_account_info = BankAccountInfoFactory(
            individual=cls.individuals[5],
            bank_name="ING",
            bank_account_number=11110000222255558888999925,
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
            program=cls.individuals[0].program,
        )

        cls.national_passport = DocumentFactory(
            document_number="111-222-333",
            type=DocumentTypeFactory(key="national_passport"),
            individual=cls.individuals[1],
            program=cls.individuals[1].program,
        )

        cls.birth_certificate = DocumentFactory(
            document_number="111222333",
            type=DocumentType.objects.get(key="birth_certificate"),
            individual=cls.individuals[4],
            program=cls.individuals[4].program,
        )

        cls.disability_card = DocumentFactory(
            document_number="10000000000",
            type=DocumentType.objects.get(key="disability_card"),
            individual=cls.individuals[6],
            program=cls.individuals[6].program,
        )

        cls.drivers_license = DocumentFactory(
            document_number="1234567890",
            type=DocumentType.objects.get(key="drivers_license"),
            individual=cls.individuals[0],
            program=cls.individuals[0].program,
        )

        cls.tax_id = DocumentFactory(
            document_number="666-777-888",
            type=DocumentType.objects.get(key="tax_id"),
            individual=cls.individuals[2],
            program=cls.individuals[2].program,
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
        cls.area2 = AreaFactory(
            name="City Test2",
            area_type=area_type_level_2,
            p_code="area2",
            parent=cls.area1,
        )

        cls.household_one.set_admin_areas(cls.area2)

        cls.update_partner_access_to_program(cls.partner, cls.program, [cls.household_one.admin_area])
        cls.update_partner_access_to_program(cls.partner, cls.program_draft, [cls.household_one.admin_area])
        # just add one PENDING Ind to be sure filters works correctly
        IndividualFactory(
            **{
                "full_name": "Tester Test",
                "given_name": "Tester",
                "family_name": "Test",
                "phone_no": "(953)681-4123",
                "birth_date": "1943-07-23",
            },
            rdi_merge_status=MergeStatusModel.PENDING,
        )

        rebuild_search_index()

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_individual_query_all(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

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
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

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

    def test_individual_query_single_different_program_in_header(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS],
            self.business_area,
            self.program,
        )

        self.snapshot_graphql_request(
            request_string=self.INDIVIDUAL_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program_draft.id, "ProgramNode"),
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
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program_two)

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
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

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
            variables={"search": "Jenna Franklin", "program": self.id_to_base64(self.program.id, "ProgramNode")},
        )

    def test_individual_query_draft(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
            self.business_area,
            self.program_draft,
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
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

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
            variables={"search": "(953)682-4596"},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_national_id_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

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
            variables={
                "documentNumber": f"{self.national_id.document_number}",
                "documentType": "national_id",
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_national_passport_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

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
            variables={
                "documentNumber": f"{self.national_passport.document_number}",
                "documentType": "national_passport",
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_tax_id_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

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
            variables={"documentNumber": "666-777-888", "documentType": "tax_id"},
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
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

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
            variables={"search": self.bank_account_info.bank_account_number},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_birth_certificate_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

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
            variables={
                "documentNumber": self.birth_certificate.document_number,
                "documentType": "birth_certificate",
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_disability_card_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

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
            variables={
                "documentNumber": self.disability_card.document_number,
                "documentType": "disability_card",
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_search_drivers_license_filter(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

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
            variables={
                "documentNumber": self.drivers_license.document_number,
                "documentType": "drivers_license",
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST]),
            ("without_permission", []),
        ]
    )
    def test_query_individuals_by_admin2(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"admin2": [encode_id_base64(self.area2.id, "AreaNode")]},
        )

    def test_individual_query_all_for_all_programs(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
            self.business_area,
        )

        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
        )

    def test_individual_query_all_for_all_programs_user_with_no_program_access(
        self,
    ) -> None:
        self.create_user_role_with_permissions(
            self.user_with_no_access,
            [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
            self.business_area,
        )
        self.snapshot_graphql_request(
            request_string=self.ALL_INDIVIDUALS_QUERY,
            context={
                "user": self.user_with_no_access,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
        )


class TestIndividualWithFlexFieldsQuery(APITestCase):
    databases = "__all__"

    INDIVIDUAL_QUERY = """
    query Individual($id: ID!) {
      individual(id: $id) {
        fullName
        givenName
        familyName
        phoneNo
        birthDate
        flexFields
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory()
        cls.business_area = create_afghanistan()

        cls.program = ProgramFactory(
            name="Test Program for Individual Query",
            business_area=cls.business_area,
            status=Program.ACTIVE,
        )

        household, individuals = create_household_and_individuals(
            household_data={"business_area": cls.business_area, "program": cls.program},
            individuals_data=[
                {
                    "full_name": "Benjamin Butler",
                    "given_name": "Benjamin",
                    "family_name": "Butler",
                    "phone_no": "(953)682-4596",
                    "birth_date": "1943-07-30",
                    "id": "ffb2576b-126f-42de-b0f5-ef889b7bc1fe",
                    "business_area": cls.business_area,
                },
            ],
        )
        pdu_data_1 = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=3,
            rounds_names=["Round 1", "Round 2", "Round 3"],
        )
        FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field 1",
            pdu_data=pdu_data_1,
        )
        pdu_data_2 = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=4,
            rounds_names=["Round A", "Round B", "Round C", "Round D"],
        )
        FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field 2",
            pdu_data=pdu_data_2,
        )

        cls.individual = individuals[0]
        # populate pdu fields with null values
        cls.individual.flex_fields = populate_pdu_with_null_values(cls.program, {})
        # populate some values - in the Individual Query only populated values should be returned
        cls.individual.flex_fields["pdu_field_1"]["1"] = {
            "value": 123.45,
            "collection_date": "2021-01-01",
        }
        cls.individual.flex_fields["pdu_field_1"]["2"] = {
            "value": 234.56,
            "collection_date": "2021-01-01",
        }
        cls.individual.flex_fields["pdu_field_2"]["4"] = {
            "value": "Value D",
            "collection_date": "2021-01-01",
        }
        cls.individual.save()

    def test_individual_query_single_with_flex_fields(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS],
            self.business_area,
            self.program,
        )

        self.snapshot_graphql_request(
            request_string=self.INDIVIDUAL_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.individual.id, "IndividualNode")},
        )
        self.assertEqual(
            self.individual.flex_fields,
            {
                "pdu_field_1": {
                    "1": {"value": 123.45, "collection_date": "2021-01-01"},
                    "2": {"value": 234.56, "collection_date": "2021-01-01"},
                    "3": {"value": None},
                },
                "pdu_field_2": {
                    "1": {"value": None},
                    "2": {"value": None},
                    "3": {"value": None},
                    "4": {"value": "Value D", "collection_date": "2021-01-01"},
                },
            },
        )


class TestIndividualWithDeliveryMechanismsDataQuery(APITestCase):
    databases = "__all__"

    INDIVIDUAL_QUERY = """
    query Individual($id: ID!) {
      individual(id: $id) {
        fullName
        givenName
        familyName
        phoneNo
        birthDate
        deliveryMechanismsData {
            name
            isValid
            individualTabData
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory()
        cls.business_area = create_afghanistan()
        generate_delivery_mechanisms()
        cls.dm_atm_card = DeliveryMechanism.objects.get(code="atm_card")
        cls.dm_mobile_money = DeliveryMechanism.objects.get(code="mobile_money")

        cls.program = ProgramFactory(
            name="Test Program for Individual Query",
            business_area=cls.business_area,
            status=Program.ACTIVE,
        )

        household, individuals = create_household_and_individuals(
            household_data={"business_area": cls.business_area, "program": cls.program},
            individuals_data=[
                {
                    "full_name": "Benjamin Butler",
                    "given_name": "Benjamin",
                    "family_name": "Butler",
                    "phone_no": "(953)682-4596",
                    "birth_date": "1943-07-30",
                    "id": "ffb2576b-126f-42de-b0f5-ef889b7bc1fe",
                    "business_area": cls.business_area,
                },
            ],
        )
        cls.individual = individuals[0]
        DeliveryMechanismDataFactory(
            individual=cls.individual,
            delivery_mechanism=cls.dm_atm_card,
            data={
                "card_number__atm_card": "123",
                "card_expiry_date__atm_card": "2022-01-01",
                "name_of_cardholder__atm_card": "Marek",
            },
            is_valid=True,
        )
        DeliveryMechanismDataFactory(
            individual=cls.individual,
            delivery_mechanism=cls.dm_mobile_money,
            data={
                "service_provider_code__mobile_money": "ABC",
                "delivery_phone_number__mobile_money": "123456789",
                "provider__mobile_money": "Provider",
            },
            is_valid=False,
        )

    @parameterized.expand(
        [
            (
                "with_permissions",
                [
                    Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
                    Permissions.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION,
                ],
            ),
            (
                "without_permissions",
                [
                    Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
                ],
            ),
        ]
    )
    def test_individual_query_delivery_mechanisms_data(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area, self.program)

        self.snapshot_graphql_request(
            request_string=self.INDIVIDUAL_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.individual.id, "IndividualNode")},
        )
