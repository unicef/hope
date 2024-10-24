from typing import Any

from flaky import flaky
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, RoleFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    DataCollectingTypeFactory,
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
)
from hct_mis_api.apps.core.models import FlexibleAttribute, PeriodicFieldData
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    EntitlementCardFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import (
    BankAccountInfo,
    Document,
    EntitlementCard,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough


class TestCopyProgram(APITestCase):
    COPY_PROGRAM_MUTATION = """
    mutation CopyProgram($programData: CopyProgramInput!) {
      copyProgram(programData: $programData) {
        program {
          name
          startDate
          endDate
          budget
          description
          frequencyOfPayments
          sector
          cashPlus
          populationGoal
          administrativeAreasOfImplementation
          partners {
            name
            areas {
              name
            }
            areaAccess
          }
          partnerAccess
          pduFields {
            name
            label
            pduData {
              subtype
              numberOfRounds
              roundsNames
            }
          }
        }
      validationErrors
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.partner = PartnerFactory(name="WFP")
        cls.user = UserFactory.create(partner=cls.partner)
        data_collecting_type = DataCollectingTypeFactory(
            label="Full", code="full", weight=1, business_areas=[cls.business_area]
        )
        DataCollectingTypeFactory(label="Partial", code="partial", weight=1, business_areas=[cls.business_area])
        cls.program = ProgramFactory.create(
            name="initial name",
            status=Program.ACTIVE,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
            programme_code="TEST",
        )
        cls.copy_data = {
            "programData": {
                "id": cls.id_to_base64(cls.program.id, "ProgramNode"),
                "name": "copied name",
                "startDate": "2019-12-20",
                "endDate": "2021-12-20",
                "budget": 20000000,
                "description": "my description of program",
                "frequencyOfPayments": "REGULAR",
                "sector": "EDUCATION",
                "cashPlus": True,
                "populationGoal": 150000,
                "administrativeAreasOfImplementation": "Lorem Ipsum",
                "programmeCode": "T3ST",
                "partnerAccess": Program.NONE_PARTNERS_ACCESS,
            },
        }
        cls.household1, cls.individuals1 = create_household_and_individuals(
            household_data={
                "business_area": cls.business_area,
                "program": cls.program,
            },
            individuals_data=[
                {
                    "business_area": cls.business_area,
                },
            ],
        )
        cls.entitlement_card1 = EntitlementCardFactory.create(household=cls.household1)
        cls.individual = cls.individuals1[0]
        cls.individual_role_in_household1 = IndividualRoleInHouseholdFactory(
            individual=cls.individual,
            household=cls.household1,
        )
        cls.document1 = DocumentFactory(individual=cls.individual, program=cls.individual.program)
        cls.individual_identity1 = IndividualIdentityFactory(individual=cls.individual)
        cls.bank_account_info1 = BankAccountInfoFactory(individual=cls.individual)
        cls.individual.individual_collection = None

        # Flex fields on the individual (should be copied) and PDU flex fields (should be ignored)
        pdu_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=3,
            rounds_names=["Round 1", "Round 2", "Round 3"],
        )
        pdu_field = FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field 1",
            pdu_data=pdu_data,
        )
        flex_field = FlexibleAttribute.objects.create(
            name="flex_field_1",
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        )
        cls.individual.flex_fields = {
            pdu_field.name: {
                "1": {
                    "value": "1.1",
                    "collection_date": "2021-01-01",
                }
            },
            flex_field.name: "Value 1",
        }
        cls.individual.save()
        cls.household1.household_collection = None
        cls.household1.save()
        cls.household2, individuals2 = create_household_and_individuals(
            household_data={
                "business_area": cls.business_area,
                "program": cls.program,
            },
            individuals_data=[
                {
                    "business_area": cls.business_area,
                },
            ],
        )
        # household and individuals with invalid statuses
        cls.household3, cls.individuals3 = create_household_and_individuals(
            household_data={
                "business_area": cls.business_area,
                "program": cls.program,
            },
            individuals_data=[
                {
                    "business_area": cls.business_area,
                },
                {
                    "business_area": cls.business_area,
                },
            ],
        )
        cls.household3.withdrawn = True
        cls.household3.save()
        cls.individuals3[0].withdrawn = True
        cls.individuals3[0].save()
        cls.individuals3[1].duplicate = True
        cls.individuals3[1].save()

        # create UNICEF partner - it will always be granted access while creating program
        PartnerFactory(name="UNICEF")

        # partner with role in BA - will be granted access for ALL_PARTNERS_ACCESS type
        partner_allowed_in_BA = PartnerFactory(name="Other Partner")
        partner_allowed_in_BA.allowed_business_areas.set([cls.business_area])
        role = RoleFactory(name="Role for WFP")
        cls.add_partner_role_in_business_area(partner_allowed_in_BA, cls.business_area, [role])

        PartnerFactory(name="Partner not allowed in BA")

        country_afg = CountryFactory(name="Afghanistan")
        country_afg.business_areas.set([cls.business_area])
        area_type_afg = AreaTypeFactory(name="Area Type in Afg", country=country_afg)
        country_other = CountryFactory(
            name="Other Country",
            short_name="Oth",
            iso_code2="O",
            iso_code3="OTH",
            iso_num="111",
        )
        cls.area_type_other = AreaTypeFactory(name="Area Type Other", country=country_other)

        cls.area_in_afg_1 = AreaFactory(name="Area in AFG 1", area_type=area_type_afg, p_code="AREA-IN-AFG1")
        cls.area_in_afg_2 = AreaFactory(name="Area in AFG 2", area_type=area_type_afg, p_code="AREA-IN-AFG2")
        cls.area_not_in_afg = AreaFactory(
            name="Area not in AFG", area_type=cls.area_type_other, p_code="AREA-NOT-IN-AFG"
        )

        # PDU data - on original Program - SHOULD NOT BE COPIED into new Program
        pdu_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=3,
            rounds_names=["Round 1 Original", "Round 2 Original", "Round 3 Original"],
        )
        FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field In Original Program",
            pdu_data=pdu_data,
        )

    def test_copy_program_not_authenticated(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION,
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "updated name",
                },
                "version": self.program.version,
            },
        )

    def test_copy_program_without_permissions(self) -> None:
        user = UserFactory.create()
        self.create_user_role_with_permissions(user, [], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION,
            context={"user": user},
            variables=self.copy_data,
        )

    @flaky(max_runs=3, min_passes=1)
    def test_copy_with_permissions(self) -> None:
        self.assertEqual(Household.objects.count(), 3)
        self.assertEqual(Individual.objects.count(), 4)
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_DUPLICATE], self.business_area)
        self.assertIsNone(self.household1.household_collection)
        self.assertIsNone(self.individuals1[0].individual_collection)
        with self.captureOnCommitCallbacks(execute=True):
            self.snapshot_graphql_request(
                request_string=self.COPY_PROGRAM_MUTATION,
                context={"user": self.user},
                variables=self.copy_data,
            )
        copied_program = Program.objects.exclude(id=self.program.id).order_by("created_at").last()
        self.assertEqual(copied_program.status, Program.DRAFT)
        self.assertEqual(copied_program.name, "copied name")
        self.assertEqual(copied_program.household_set.count(), 2)
        self.assertEqual(copied_program.individuals.count(), 2)
        self.assertNotIn(self.household3, copied_program.household_set.all())
        self.assertNotIn(self.individuals3[0], copied_program.individuals.all())
        self.assertNotIn(self.individuals3[1], copied_program.individuals.all())
        self.assertEqual(Household.objects.count(), 5)
        self.assertEqual(Individual.objects.count(), 6)
        self.assertEqual(EntitlementCard.objects.count(), 2)
        self.assertNotEqual(
            copied_program.household_set.filter(copied_from=self.household1).first().entitlement_cards.first().id,
            self.entitlement_card1.id,
        )
        self.assertEqual(
            copied_program.household_set.filter(copied_from=self.household1)
            .first()
            .entitlement_cards.first()
            .card_number,
            self.entitlement_card1.card_number,
        )
        self.assertNotEqual(
            copied_program.household_set.filter(copied_from=self.household1).first().first_registration_date,
            self.household1.first_registration_date,
        )
        self.assertNotEqual(
            copied_program.household_set.filter(copied_from=self.household1).first().last_registration_date,
            self.household1.last_registration_date,
        )
        self.assertEqual(Document.objects.count(), 2)
        self.assertNotEqual(
            copied_program.individuals.filter(copied_from=self.individuals1[0]).first().documents.first().id,
            self.document1.id,
        )
        self.assertEqual(
            copied_program.individuals.filter(copied_from=self.individuals1[0])
            .first()
            .documents.first()
            .document_number,
            self.document1.document_number,
        )

        self.assertEqual(IndividualIdentity.objects.count(), 2)
        self.assertNotEqual(
            copied_program.individuals.filter(copied_from=self.individuals1[0]).first().identities.first().id,
            self.individual_identity1.id,
        )
        self.assertEqual(
            copied_program.individuals.filter(copied_from=self.individuals1[0]).first().identities.first().number,
            self.individual_identity1.number,
        )

        self.assertEqual(BankAccountInfo.objects.count(), 2)
        self.assertNotEqual(
            copied_program.individuals.filter(copied_from=self.individuals1[0]).first().bank_account_info.first().id,
            self.bank_account_info1.id,
        )
        self.assertEqual(
            copied_program.individuals.filter(copied_from=self.individuals1[0])
            .first()
            .bank_account_info.first()
            .bank_account_number,
            self.bank_account_info1.bank_account_number,
        )

        self.assertEqual(IndividualRoleInHousehold.objects.count(), 2)
        self.assertNotEqual(
            copied_program.household_set.filter(copied_from=self.household1).first().representatives.first().id,
            self.individuals1[0].id,
        )
        self.assertEqual(
            copied_program.household_set.filter(copied_from=self.household1).first().representatives.first().role,
            self.individual_role_in_household1.role,
        )
        self.assertEqual(
            copied_program.household_set.filter(copied_from=self.household1)
            .first()
            .representatives.first()
            .copied_from,
            self.individual_role_in_household1.individual,
        )
        self.assertEqual(ProgramPartnerThrough.objects.filter(program=copied_program).count(), 1)

        self.individuals1[0].refresh_from_db()
        self.household1.refresh_from_db()

        self.assertIsNotNone(self.household1.household_collection)
        self.assertIsNotNone(self.individuals1[0].individual_collection)
        self.assertEqual(
            copied_program.household_set.filter(copied_from=self.household1).first().household_collection,
            self.household1.household_collection,
        )
        self.assertEqual(
            copied_program.individuals.filter(copied_from=self.individuals1[0]).first().individual_collection,
            self.individuals1[0].individual_collection,
        )
        self.assertNotEqual(
            copied_program.individuals.filter(copied_from=self.individuals1[0]).first().first_registration_date,
            self.individuals1[0].first_registration_date,
        )
        self.assertNotEqual(
            copied_program.individuals.filter(copied_from=self.individuals1[0]).first().last_registration_date,
            self.individuals1[0].last_registration_date,
        )
        # check flex fields and PDU fields on original and copied individual
        self.assertNotEqual(
            copied_program.individuals.filter(copied_from=self.individuals1[0]).first().flex_fields,
            self.individuals1[0].flex_fields,
        )
        self.assertEqual(
            self.individuals1[0].flex_fields,
            {
                "pdu_field_1": {
                    "1": {
                        "value": "1.1",
                        "collection_date": "2021-01-01",
                    }
                },
                "flex_field_1": "Value 1",
            },
        )
        self.assertEqual(
            copied_program.individuals.filter(copied_from=self.individuals1[0]).first().flex_fields,
            {"flex_field_1": "Value 1"},
        )

        self.assertIsNotNone(copied_program.cycles.first())
        self.assertEqual(copied_program.cycles.first().program_id, copied_program.pk)
        self.assertEqual(copied_program.cycles.first().title, "Default Programme Cycle")
        self.assertEqual(copied_program.cycles.first().status, "DRAFT")
        self.assertIsNone(copied_program.cycles.first().end_date)

    def test_copy_program_incompatible_collecting_type(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_DUPLICATE], self.business_area)
        copy_data_incompatible = {**self.copy_data}
        copy_data_incompatible["programData"]["dataCollectingTypeCode"] = "partial"
        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION,
            context={"user": self.user},
            variables=copy_data_incompatible,
        )

    def test_copy_program_with_existing_name(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_DUPLICATE], self.business_area)
        copy_data_existing_name = {**self.copy_data}
        copy_data_existing_name["programData"]["name"] = "initial name"
        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION,
            context={"user": self.user},
            variables=copy_data_existing_name,
        )

    @parameterized.expand(
        [
            ("valid", Program.SELECTED_PARTNERS_ACCESS),
            ("invalid_all_partner_access", Program.ALL_PARTNERS_ACCESS),
            ("invalid_none_partner_access", Program.NONE_PARTNERS_ACCESS),
        ]
    )
    def test_copy_program_with_partners(self, _: Any, partner_access: str) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_DUPLICATE], self.business_area)
        area1 = AreaFactory(name="North Brianmouth", area_type=self.area_type_other, p_code="NORTH-B")
        area2 = AreaFactory(name="South Catherine", area_type=self.area_type_other, p_code="SOUTH-C")
        partner2 = PartnerFactory(name="New Partner")
        self.copy_data["programData"]["partners"] = [
            {
                "partner": str(self.partner.id),
                "areas": [str(area1.id), str(area2.id)],
            },
            {
                "partner": str(partner2.id),
                "areas": [],
            },
        ]
        self.copy_data["programData"]["partnerAccess"] = partner_access
        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION,
            context={"user": self.user},
            variables=self.copy_data,
        )

    def test_copy_program_with_partners_all_partners_access(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_DUPLICATE], self.business_area)
        self.copy_data["programData"]["partnerAccess"] = Program.ALL_PARTNERS_ACCESS

        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION, context={"user": self.user}, variables=self.copy_data
        )

    def test_copy_program_with_partners_none_partners_access(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_DUPLICATE], self.business_area)
        self.copy_data["programData"]["partnerAccess"] = Program.NONE_PARTNERS_ACCESS

        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION, context={"user": self.user}, variables=self.copy_data
        )

    def test_copy_program_with_pdu_fields(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_DUPLICATE], self.business_area)
        self.copy_data["programData"]["pduFields"] = [
            {
                "label": "PDU Field 1",
                "pduData": {
                    "subtype": "DECIMAL",
                    "numberOfRounds": 3,
                    "roundsNames": ["Round 1", "Round 2", "Round 3"],
                },
            },
            {
                "label": "PDU Field 2",
                "pduData": {
                    "subtype": "STRING",
                    "numberOfRounds": 1,
                    "roundsNames": ["Round *"],
                },
            },
            {
                "label": "PDU Field 3",
                "pduData": {
                    "subtype": "DATE",
                    "numberOfRounds": 2,
                    "roundsNames": ["Round A", "Round B"],
                },
            },
            {
                "label": "PDU Field 4",
                "pduData": {
                    "subtype": "BOOL",
                    "numberOfRounds": 4,
                    "roundsNames": ["Round 1A", "Round 2B", "Round 3C", "Round 4D"],
                },
            },
        ]

        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION, context={"user": self.user}, variables=self.copy_data
        )
        self.assertEqual(Program.objects.get(name="copied name").pdu_fields.count(), 4)

    def test_copy_program_with_pdu_fields_invalid_data(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_DUPLICATE], self.business_area)
        # pdu data with mismatched number of rounds and rounds names
        self.copy_data["programData"]["pduFields"] = [
            {
                "label": "PDU Field 1",
                "pduData": {
                    "subtype": "DECIMAL",
                    "numberOfRounds": 3,
                    "roundsNames": ["Round 1", "Round 2", "Round 3"],
                },
            },
            {
                "label": "PDU Field 2 Invalid",
                "pduData": {
                    "subtype": "STRING",
                    "numberOfRounds": 1,
                    "roundsNames": ["Round *", "Round 2*"],
                },
            },
        ]

        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION, context={"user": self.user}, variables=self.copy_data
        )

    def test_copy_program_with_pdu_fields_duplicated_field_names_in_input(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_DUPLICATE], self.business_area)
        # pdu data with duplicated field names in the input
        self.copy_data["programData"]["pduFields"] = [
            {
                "label": "PDU Field 1",
                "pduData": {
                    "subtype": "DECIMAL",
                    "numberOfRounds": 3,
                    "roundsNames": ["Round 1", "Round 2", "Round 3"],
                },
            },
            {
                "label": "PDU Field 1",
                "pduData": {
                    "subtype": "STRING",
                    "numberOfRounds": 2,
                    "roundsNames": ["Round *", "Round 2*"],
                },
            },
        ]

        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION, context={"user": self.user}, variables=self.copy_data
        )

    def test_copy_program_with_pdu_fields_existing_field_name_in_different_program(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_DUPLICATE], self.business_area)
        # pdu data with field name that already exists in the database but in different program -> no fail
        pdu_data = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DATE,
            number_of_rounds=1,
            rounds_names=["Round 1"],
        )
        program = ProgramFactory(business_area=self.business_area, name="Test Program 1")
        FlexibleAttributeForPDUFactory(
            program=program,
            label="PDU Field 1",
            pdu_data=pdu_data,
        )
        self.copy_data["programData"]["pduFields"] = [
            {
                "label": "PDU Field 1",
                "pduData": {
                    "subtype": "DECIMAL",
                    "numberOfRounds": 3,
                    "roundsNames": ["Round 1", "Round 2", "Round 3"],
                },
            },
        ]

        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION, context={"user": self.user}, variables=self.copy_data
        )
