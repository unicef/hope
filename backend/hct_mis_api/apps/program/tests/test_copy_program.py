from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
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
          scope
          cashPlus
          populationGoal
          administrativeAreasOfImplementation
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory.create(name="initial name", status=Program.ACTIVE, business_area=cls.business_area)
        cls.household1, cls.individuals1 = create_household_and_individuals(
            household_data={
                "business_area": cls.business_area,
                "program_id": cls.program.pk,
            },
            individuals_data=[
                {
                    "business_area": cls.business_area,
                    "program_id": cls.program.pk,
                },
            ],
        )
        cls.entitlement_card1 = EntitlementCardFactory.create(household=cls.household1)
        individual = cls.individuals1[0]
        cls.individual_role_in_household1 = IndividualRoleInHouseholdFactory(
            individual=individual,
            household=cls.household1,
        )
        cls.document1 = DocumentFactory(individual=individual)
        cls.individual_identity1 = IndividualIdentityFactory(individual=individual)
        cls.bank_account_info1 = BankAccountInfoFactory(individual=individual)
        cls.household2, individuals2 = create_household_and_individuals(
            household_data={
                "business_area": cls.business_area,
                "program_id": cls.program.pk,
            },
            individuals_data=[
                {
                    "business_area": cls.business_area,
                    "program_id": cls.program.pk,
                },
            ],
        )
        # household and individuals with invalid statuses
        cls.household3, cls.individuals3 = create_household_and_individuals(
            household_data={
                "business_area": cls.business_area,
                "program_id": cls.program.pk,
            },
            individuals_data=[
                {
                    "business_area": cls.business_area,
                    "program_id": cls.program.pk,
                },
                {
                    "business_area": cls.business_area,
                    "program_id": cls.program.pk,
                },
            ],
        )
        cls.household3.withdrawn = True
        cls.household3.save()
        cls.individuals3[0].withdrawn = True
        cls.individuals3[0].save()
        cls.individuals3[1].duplicate = True
        cls.individuals3[1].save()

    def test_update_program_not_authenticated(self) -> None:
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

    @parameterized.expand(
        [
            ("with_permissions", [Permissions.PROGRAMME_DUPLICATE], True),
            ("without_permissions", [], False),
        ]
    )
    def test_update_program_authenticated(self, _: Any, permissions: List[Permissions], should_be_copied: bool) -> None:
        user = UserFactory.create()
        self.create_user_role_with_permissions(user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.COPY_PROGRAM_MUTATION,
            context={"user": user},
            variables={
                "programData": {
                    "id": self.id_to_base64(self.program.id, "ProgramNode"),
                    "name": "copied name",
                    "startDate": "2019-12-20",
                    "endDate": "2021-12-20",
                    "budget": 20000000,
                    "description": "my description of program",
                    "frequencyOfPayments": "REGULAR",
                    "sector": "EDUCATION",
                    "scope": "UNICEF",
                    "cashPlus": True,
                    "populationGoal": 150000,
                    "administrativeAreasOfImplementation": "Lorem Ipsum",
                },
            },
        )
        if should_be_copied:
            copied_program = Program.objects.exclude(id=self.program.id).first()
            assert copied_program.status == Program.DRAFT
            assert copied_program.name == "copied name"
            assert copied_program.household_set.count() == 2
            assert copied_program.individuals.count() == 2
            assert self.household3 not in copied_program.household_set.all()
            assert self.individuals3[0] not in copied_program.individuals.all()
            assert self.individuals3[1] not in copied_program.individuals.all()
            assert Household.objects.count() == 5
            assert Individual.objects.count() == 6
            assert EntitlementCard.objects.count() == 2
            assert (
                copied_program.household_set.filter(copied_from=self.household1).first().entitlement_cards.first().id
                != self.entitlement_card1.id
            )
            assert (
                copied_program.household_set.filter(copied_from=self.household1).first().entitlement_cards.first().card_number
                == self.entitlement_card1.card_number
            )

            assert Document.objects.count() == 2
            assert copied_program.individuals.filter(copied_from=self.individuals1[0]).first().documents.first().id != self.document1.id
            assert (
                copied_program.individuals.filter(copied_from=self.individuals1[0]).first().documents.first().document_number
                == self.document1.document_number
            )

            assert IndividualIdentity.objects.count() == 2
            assert (
                copied_program.individuals.filter(copied_from=self.individuals1[0]).first().identities.first().id
                != self.individual_identity1.id
            )
            assert (
                copied_program.individuals.filter(copied_from=self.individuals1[0]).first().identities.first().number
                == self.individual_identity1.number
            )

            assert BankAccountInfo.objects.count() == 2
            assert (
                copied_program.individuals.filter(copied_from=self.individuals1[0]).first().bank_account_info.first().id
                != self.bank_account_info1.id
            )
            assert (
                copied_program.individuals.filter(copied_from=self.individuals1[0]).first().bank_account_info.first().bank_account_number
                == self.bank_account_info1.bank_account_number
            )

            assert IndividualRoleInHousehold.objects.count() == 2
            assert (
                copied_program.household_set.filter(copied_from=self.household1).first().representatives.first().id
                != self.individuals1[0].id
            )
            assert (
                copied_program.household_set.filter(copied_from=self.household1).first().representatives.first().role
                == self.individual_role_in_household1.role
            )
            assert (
                copied_program.household_set.filter(copied_from=self.household1).first().representatives.first().copied_from
                == self.individual_role_in_household1.individual
            )
