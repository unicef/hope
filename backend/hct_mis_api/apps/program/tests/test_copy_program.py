from flaky import flaky

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory, create_afghanistan
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
from hct_mis_api.apps.program.models import Program


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
        }
      validationErrors
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()
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
        individual = cls.individuals1[0]
        cls.individual_role_in_household1 = IndividualRoleInHouseholdFactory(
            individual=individual,
            household=cls.household1,
        )
        cls.document1 = DocumentFactory(individual=individual, program=individual.program)
        cls.individual_identity1 = IndividualIdentityFactory(individual=individual)
        cls.bank_account_info1 = BankAccountInfoFactory(individual=individual)
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
        user = UserFactory.create()
        self.assertEqual(Household.objects.count(), 3)
        self.assertEqual(Individual.objects.count(), 4)
        self.create_user_role_with_permissions(user, [Permissions.PROGRAMME_DUPLICATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION,
            context={"user": user},
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

    def test_copy_program_incompatible_collecting_type(self) -> None:
        user = UserFactory.create()
        self.create_user_role_with_permissions(user, [Permissions.PROGRAMME_DUPLICATE], self.business_area)
        copy_data_incompatible = {**self.copy_data}
        copy_data_incompatible["programData"]["dataCollectingTypeCode"] = "partial"
        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION,
            context={"user": user},
            variables=copy_data_incompatible,
        )

    def test_copy_program_with_existing_name(self) -> None:
        user = UserFactory.create()
        self.create_user_role_with_permissions(user, [Permissions.PROGRAMME_DUPLICATE], self.business_area)
        copy_data_existing_name = {**self.copy_data}
        copy_data_existing_name["programData"]["name"] = "initial name"
        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION,
            context={"user": user},
            variables=copy_data_existing_name,
        )
