from typing import Dict, Optional

from django.test import TestCase

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    EntitlementCardFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    create_individual_document,
)
from hct_mis_api.apps.household.models import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    BankAccountInfo,
    Document,
    EntitlementCard,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.fixtures import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentRecordFactory,
    ServiceProviderFactory,
)
from hct_mis_api.apps.payment.models import ServiceProvider
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import (
    HouseholdSelectionFactory,
    TargetPopulationFactory,
)
from hct_mis_api.apps.targeting.models import HouseholdSelection
from hct_mis_api.one_time_scripts.migrate_data_to_representations import (
    adjust_payment_records,
    adjust_payments,
    assign_non_program_objects_to_biggest_program,
    copy_bank_account_info_per_individual,
    copy_document_per_individual,
    copy_entitlement_card_per_household,
    copy_household_representation,
    copy_household_selections,
    copy_individual_identity_per_individual,
    copy_individual_representation,
    copy_roles,
    get_biggest_program,
    handle_rdis,
)


def create_origin_household_with_individual(
    business_area: BusinessArea,
    program_id: Optional[str],
    household_kwargs: Optional[Dict] = None,
    individual_kwargs: Optional[Dict] = None,
) -> tuple[Household, Individual]:
    if household_kwargs is None:
        household_kwargs = {}
    if individual_kwargs is None:
        individual_kwargs = {}

    individual = IndividualFactory(
        household=None,
        program_id=program_id,
        business_area=business_area,
        **individual_kwargs,
    )
    household = HouseholdFactory(
        business_area=business_area,
        head_of_household=individual,
        program_id=program_id,
        **household_kwargs,
    )
    household.copied_from = household
    household.origin_unicef_id = household.unicef_id
    household.save()

    individual.household = household
    individual.copied_from = individual
    individual.origin_unicef_id = individual.unicef_id
    individual.save()

    return household, individual


class TestCopyDocumentPerIndividual(TestCase):
    def setUp(self) -> None:
        business_area = BusinessAreaFactory()

        program = ProgramFactory()
        self.individual1 = IndividualFactory(household=None, business_area=business_area)
        self.document1_1 = create_individual_document(self.individual1)
        self.document1_2 = create_individual_document(self.individual1)
        self.individual_representation1 = IndividualFactory(
            program_id=program.id,
            copied_from=self.individual1,
            origin_unicef_id=self.individual1.unicef_id,
            household=None,
            business_area=business_area,
        )

    # def test_copy_document_per_individual(self) -> None:
    #     documents_count = Document.objects.count()
    #     copy_document_per_individual(self.individual1, self.individual_representation1)
    #
    #     assert self.individual_representation1.documents.count() == 2
    #     assert Document.objects.count() - documents_count == 2


class TestCopyIndividualIdentityPerIndividual(TestCase):
    def setUp(self) -> None:
        business_area = BusinessAreaFactory()
        program = ProgramFactory()
        self.individual1 = IndividualFactory(household=None, business_area=business_area)
        self.individual_identity1 = IndividualIdentityFactory(individual=self.individual1)
        self.individual_identity2 = IndividualIdentityFactory(individual=self.individual1)

        self.individual_representation1 = IndividualFactory(
            copied_from=self.individual1,
            origin_unicef_id=self.individual1.unicef_id,
            household=None,
            program_id=program.id,
            business_area=business_area,
        )

    # def test_copy_individual_identity_per_individual(self) -> None:
    #     individual_identities_count = IndividualIdentity.objects.count()
    #     copy_individual_identity_per_individual(self.individual1, self.individual_representation1)
    #
    #     assert self.individual_representation1.identities.count() == 2
    #     assert IndividualIdentity.objects.count() - individual_identities_count == 2

    def test_same_individual(self) -> None:
        individual_identities_count = IndividualIdentity.objects.count()
        copy_individual_identity_per_individual(self.individual_representation1, self.individual_representation1)

        assert IndividualIdentity.objects.count() == individual_identities_count


class TestCopyBankAccountInfoPerIndividual(TestCase):
    def setUp(self) -> None:
        business_area = BusinessAreaFactory()
        program = ProgramFactory()
        self.individual1 = IndividualFactory(household=None, business_area=business_area)
        self.bank_account_info1 = BankAccountInfoFactory(individual=self.individual1)
        self.bank_account_info2 = BankAccountInfoFactory(individual=self.individual1)

        self.individual_representation1 = IndividualFactory(
            copied_from=self.individual1,
            origin_unicef_id=self.individual1.unicef_id,
            household=None,
            program_id=program.id,
            business_area=business_area,
        )

    # def test_copy_bank_account_info_per_individual(self) -> None:
    #     bank_account_info_count = BankAccountInfo.objects.count()
    #     copy_bank_account_info_per_individual(self.individual1, self.individual_representation1)
    #
    #     assert self.individual_representation1.bank_account_info.count() == 2
    #     assert BankAccountInfo.objects.count() - bank_account_info_count == 2

    def test_same_individual(self) -> None:
        bank_account_info_count = BankAccountInfo.objects.count()
        copy_bank_account_info_per_individual(self.individual_representation1, self.individual_representation1)

        assert BankAccountInfo.objects.count() == bank_account_info_count


class TestCopyEntitlementCardPerHousehold(TestCase):
    def setUp(self) -> None:
        business_area = BusinessAreaFactory()
        program = ProgramFactory()
        individual1 = IndividualFactory(household=None, program_id=program.id, business_area=business_area)
        self.household1 = HouseholdFactory(head_of_household=individual1, business_area=business_area)
        self.entitlement_card1 = EntitlementCardFactory(household=self.household1)
        self.entitlement_card2 = EntitlementCardFactory(household=self.household1)

        individual2 = IndividualFactory(household=None, program_id=program.id, business_area=business_area)
        self.household_representation1 = HouseholdFactory(
            copied_from=self.household1,
            origin_unicef_id=self.household1.unicef_id,
            head_of_household=individual2,
            business_area=business_area,
            program_id=program.id,
        )

    # def test_copy_entitlement_card_per_household(self) -> None:
    #     entitlement_card_count = EntitlementCard.objects.count()
    #     copy_entitlement_card_per_household(self.household1, self.household_representation1)
    #
    #     assert self.household_representation1.entitlement_cards.count() == 2
    #     assert EntitlementCard.objects.count() - entitlement_card_count == 2

    def test_same_household(self) -> None:
        entitlement_card_count = EntitlementCard.objects.count()
        copy_entitlement_card_per_household(self.household_representation1, self.household_representation1)

        assert EntitlementCard.objects.count() == entitlement_card_count


class TestCopyIndividualRepresentation(TestCase):
    def setUp(self) -> None:
        business_area = BusinessAreaFactory()
        self.program = ProgramFactory()
        self.individual1 = IndividualFactory(household=None, business_area=business_area)
        self.document1_1 = create_individual_document(self.individual1)
        self.document1_2 = create_individual_document(self.individual1)
        self.individual_identity1 = IndividualIdentityFactory(individual=self.individual1)
        self.individual_identity2 = IndividualIdentityFactory(individual=self.individual1)
        self.bank_account_info1 = BankAccountInfoFactory(individual=self.individual1)
        self.bank_account_info2 = BankAccountInfoFactory(individual=self.individual1)

    # def test_copy_individual_representation_first_representation(self) -> None:
        # documents_count = Document.objects.count()
        # individual_identities_count = IndividualIdentity.objects.count()
        # bank_account_info_count = BankAccountInfo.objects.count()
        #
        # individual = copy_individual_representation(program=self.program, individual=self.individual1)
        #
        # assert individual.documents.count() == 2
        # assert individual.identities.count() == 2
        # assert individual.bank_account_info.count() == 2
        # assert individual.program == self.program
        # assert individual == self.individual1
        # assert individual.copied_from == self.individual1
        # assert individual.origin_unicef_id == self.individual1.unicef_id
        # assert individual.documents.first().program == self.program
        # assert individual.documents.last().program == self.program
        # assert Document.objects.count() == documents_count
        # assert IndividualIdentity.objects.count() == individual_identities_count
        # assert BankAccountInfo.objects.count() == bank_account_info_count

    # def test_copy_individual_representation_already_exists(self) -> None:
    #     individual_representation = IndividualFactory(
    #         copied_from=self.individual1,
    #         origin_unicef_id=self.individual1.unicef_id,
    #         household=None,
    #         program_id=self.program.id,
    #         business_area=self.individual1.business_area,
    #     )
    #     documents_count = Document.objects.count()
    #     individual_identities_count = IndividualIdentity.objects.count()
    #     bank_account_info_count = BankAccountInfo.objects.count()
    #
    #     individual = copy_individual_representation(program=self.program, individual=self.individual1)
    #
    #     assert individual == individual_representation
    #     assert Document.objects.count() == documents_count
    #     assert IndividualIdentity.objects.count() == individual_identities_count
    #     assert BankAccountInfo.objects.count() == bank_account_info_count

    # def test_copy_individual_representation(self) -> None:
    #     self.individual1.copied_from_id = self.individual1.id
    #     self.individual1.origin_unicef_id = self.individual1.unicef_id
    #     self.individual1.save()
    #     original_pk = self.individual1.pk
    #
    #     documents_count = Document.objects.count()
    #     individual_identities_count = IndividualIdentity.objects.count()
    #     bank_account_info_count = BankAccountInfo.objects.count()
    #     individual_count = Individual.objects.count()
    #
    #     individual = copy_individual_representation(program=self.program, individual=self.individual1)
    #
    #     self.individual1 = Individual.objects.get(pk=original_pk)
    #
    #     assert Individual.objects.count() - individual_count == 1
    #     assert individual.id != self.individual1.id
    #
    #     assert individual.pk
    #     assert individual.unicef_id
    #     assert individual.program == self.program
    #     assert individual.copied_from == self.individual1
    #     assert individual.origin_unicef_id == self.individual1.unicef_id
    #     assert individual.documents.count() == 2
    #     assert individual.identities.count() == 2
    #     assert individual.bank_account_info.count() == 2
    #
    #     assert Document.objects.count() - documents_count == 2
    #     assert IndividualIdentity.objects.count() - individual_identities_count == 2
    #     assert BankAccountInfo.objects.count() - bank_account_info_count == 2


class TestCopyHouseholdRepresentation(TestCase):
    def setUp(self) -> None:
        business_area = BusinessAreaFactory()
        self.program = ProgramFactory()

        self.individual1 = IndividualFactory(household=None, business_area=business_area)
        self.document1_1 = create_individual_document(self.individual1)
        self.document1_2 = create_individual_document(self.individual1)
        self.individual_identity1_1 = IndividualIdentityFactory(individual=self.individual1)
        self.individual_identity1_2 = IndividualIdentityFactory(individual=self.individual1)
        self.bank_account_info1_1 = BankAccountInfoFactory(individual=self.individual1)
        self.bank_account_info1_2 = BankAccountInfoFactory(individual=self.individual1)

        self.individual2 = IndividualFactory(household=None, program_id=self.program.id, business_area=business_area)
        self.document2_1 = create_individual_document(self.individual2)
        self.document2_2 = create_individual_document(self.individual2)
        self.individual_identity2_1 = IndividualIdentityFactory(individual=self.individual2)
        self.individual_identity2_2 = IndividualIdentityFactory(individual=self.individual2)
        self.bank_account_info2_1 = BankAccountInfoFactory(individual=self.individual2)
        self.bank_account_info2_2 = BankAccountInfoFactory(individual=self.individual2)

        self.household1 = HouseholdFactory(head_of_household=self.individual1, business_area=business_area)
        self.entitlement_card1 = EntitlementCardFactory(household=self.household1)
        self.entitlement_card2 = EntitlementCardFactory(household=self.household1)

        self.individual1.household = self.household1
        self.individual1.save()
        self.individual2.household = self.household1
        self.individual2.copied_from_id = self.individual2.id
        self.individual2.origin_unicef_id = self.individual2.unicef_id
        self.individual2.save()

    # def test_copy_household_representation_already_exists(self) -> None:
    #     self.household1.copied_from_id = self.household1.id
    #     self.household1.origin_unicef_id = self.household1.unicef_id
    #     self.household1.program_id = self.program.id
    #     self.household1.save()
    #
    #     household_count = Household.objects.count()
    #     entitlement_card_count = EntitlementCard.objects.count()
    #     individual_count = Individual.objects.count()
    #     documents_count = Document.objects.count()
    #     individual_identities_count = IndividualIdentity.objects.count()
    #     bank_account_info_count = BankAccountInfo.objects.count()
    #
    #     copy_household_representation(program=self.program, household=self.household1)
    #
    #     self.household1 = Household.objects.get(pk=self.household1.pk)
    #
    #     assert Household.objects.count() == household_count
    #     assert EntitlementCard.objects.count() == entitlement_card_count
    #     assert Individual.objects.count() == individual_count
    #     assert Document.objects.count() == documents_count
    #     assert IndividualIdentity.objects.count() == individual_identities_count
    #     assert BankAccountInfo.objects.count() == bank_account_info_count

    # def test_copy_household_representation(self) -> None:
    #     original_pk = self.household1.pk
    #     other_program = ProgramFactory()
    #
    #     self.household1.copied_from_id = self.household1.id
    #     self.household1.origin_unicef_id = self.household1.unicef_id
    #     self.household1.program = other_program
    #     self.household1.save()
    #
    #     self.individual1.copied_from_id = self.individual1.id
    #     self.individual1.origin_unicef_id = self.individual1.unicef_id
    #     self.individual1.program = other_program
    #     self.individual1.save()
    #
    #     self.individual2.copied_from_id = self.individual2.id
    #     self.individual2.origin_unicef_id = self.individual2.unicef_id
    #     self.individual2.program = other_program
    #     self.individual2.save()
    #
    #     household_count = Household.objects.count()
    #     entitlement_card_count = EntitlementCard.objects.count()
    #     individual_count = Individual.objects.count()
    #     documents_count = Document.objects.count()
    #     individual_identities_count = IndividualIdentity.objects.count()
    #     bank_account_info_count = BankAccountInfo.objects.count()
    #
    #     copy_household_representation(program=self.program, household=self.household1)
    #     self.household1 = Household.objects.get(pk=original_pk)
    #     household = self.household1.copied_to.filter(program=self.program).first()
    #     assert household.pk != self.household1.pk
    #     assert household.program == self.program
    #     assert household.copied_from == self.household1
    #     assert household.origin_unicef_id == self.household1.unicef_id
    #     assert household.entitlement_cards.count() == 2
    #     assert household.individuals.count() == 2
    #     assert household.individuals.first().documents.count() == 2
    #     assert household.individuals.first().identities.count() == 2
    #     assert household.individuals.first().bank_account_info.count() == 2
    #
    #     assert Household.objects.count() - household_count == 1
    #     assert EntitlementCard.objects.count() - entitlement_card_count == 2
    #
    #     assert Individual.objects.count() - individual_count == 2
    #     assert Document.objects.count() - documents_count == 4
    #     assert IndividualIdentity.objects.count() - individual_identities_count == 4
    #     assert BankAccountInfo.objects.count() - bank_account_info_count == 4


class TestAdjustPayments(TestCase):
    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory()
        self.other_program = ProgramFactory(status=Program.ACTIVE)
        self.target_population1 = TargetPopulationFactory(program=self.other_program, business_area=self.business_area)
        payment_plan = PaymentPlanFactory(target_population=self.target_population1)
        (
            self.household_other_program,
            self.individual_representation_other_program,
        ) = create_origin_household_with_individual(
            program_id=self.other_program.id,
            business_area=self.business_area,
        )
        self.payment1 = PaymentFactory(
            parent=payment_plan,
            household=self.household_other_program,
            collector=self.individual_representation_other_program,
            head_of_household=self.individual_representation_other_program,
        )

    # def test_adjust_payments_other_program(self) -> None:
    #     this_program = ProgramFactory(business_area=self.business_area, status=Program.ACTIVE)
    #
    #     individual_representation_this_program = IndividualFactory(
    #         program_id=this_program.id,
    #         business_area=self.business_area,
    #         copied_from=self.individual_representation_other_program,
    #         origin_unicef_id=self.individual_representation_other_program.unicef_id,
    #         household=None,
    #     )
    #
    #     household_this_program = HouseholdFactory(
    #         program_id=this_program.id,
    #         business_area=self.business_area,
    #         copied_from=self.household_other_program,
    #         origin_unicef_id=self.household_other_program.unicef_id,
    #         head_of_household=individual_representation_this_program,
    #     )
    #
    #     self.target_population1.program = this_program
    #     self.target_population1.save()
    #
    #     adjust_payments(self.business_area)
    #
    #     self.payment1.refresh_from_db()
    #     assert self.payment1.collector == individual_representation_this_program
    #     assert self.payment1.head_of_household == individual_representation_this_program
    #     assert self.payment1.household == household_this_program

    # def test_adjust_payment_same_program(self) -> None:
    #     adjust_payments(self.business_area)
    #
    #     self.payment1.refresh_from_db()
    #     assert self.payment1.collector == self.individual_representation_other_program
    #     assert self.payment1.head_of_household == self.individual_representation_other_program
    #     assert self.payment1.household == self.household_other_program


class TestAdjustPaymentRecords(TestCase):
    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory()
        self.other_program = ProgramFactory(status=Program.ACTIVE, business_area=self.business_area)
        self.target_population1 = TargetPopulationFactory(program=self.other_program, business_area=self.business_area)
        (
            self.household_other_program,
            self.individual_representation_other_program,
        ) = create_origin_household_with_individual(
            program_id=self.other_program.id,
            business_area=self.business_area,
        )
        self.payment_record1 = PaymentRecordFactory(
            target_population=self.target_population1,
            household=self.household_other_program,
            head_of_household=self.individual_representation_other_program,
            service_provider=ServiceProvider.objects.first() or ServiceProviderFactory(),
            business_area=self.business_area,
        )

    # def test_adjust_payment_records_other_program(self) -> None:
    #     this_program = ProgramFactory(status=Program.ACTIVE, business_area=self.business_area)
    #
    #     individual_representation_this_program = IndividualFactory(
    #         program_id=this_program.id,
    #         business_area=self.business_area,
    #         copied_from=self.individual_representation_other_program,
    #         origin_unicef_id=self.individual_representation_other_program.unicef_id,
    #         household=None,
    #     )
    #
    #     household_this_program = HouseholdFactory(
    #         program_id=this_program.id,
    #         business_area=self.business_area,
    #         copied_from=self.household_other_program,
    #         origin_unicef_id=self.household_other_program.unicef_id,
    #         head_of_household=individual_representation_this_program,
    #     )
    #
    #     self.target_population1.program = this_program
    #     self.target_population1.save()
    #
    #     adjust_payment_records(self.business_area)
    #
    #     self.payment_record1.refresh_from_db()
    #
    #     assert self.payment_record1.head_of_household == individual_representation_this_program
    #     assert self.payment_record1.household == household_this_program

    # def test_adjust_payment_record_same_program(self) -> None:
    #     adjust_payment_records(self.business_area)
    #
    #     self.payment_record1.refresh_from_db()
    #     assert self.payment_record1.head_of_household == self.individual_representation_other_program
    #     assert self.payment_record1.household == self.household_other_program


class TestAdjustHouseholdSelections(TestCase):
    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory()
        self.other_program = ProgramFactory(status=Program.ACTIVE)
        self.current_program = ProgramFactory(status=Program.ACTIVE)

        self.target_population1 = TargetPopulationFactory(
            program=self.current_program, business_area=self.business_area
        )

        self.household_other_program = HouseholdFactory(
            program_id=self.other_program.id,
            business_area=self.business_area,
            head_of_household=IndividualFactory(household=None),
        )
        self.household_current_program = HouseholdFactory(
            program_id=self.current_program.id,
            business_area=self.business_area,
            head_of_household=IndividualFactory(household=None),
            copied_from=self.household_other_program,
            origin_unicef_id=self.household_other_program.unicef_id,
        )
        self.household_selection_other_program = HouseholdSelectionFactory(
            target_population=self.target_population1,
            household=self.household_other_program,
        )

    # def test_copy_household_selections_other_program(self) -> None:
    #     household_selections_count = HouseholdSelection.objects.count()
    #     household_selections = HouseholdSelection.objects.filter(target_population=self.target_population1)
    #
    #     copy_household_selections(household_selections=household_selections, program=self.current_program)
    #
    #     self.household_selection_other_program.refresh_from_db()
    #     assert self.household_selection_other_program.household == self.household_current_program
    #     assert HouseholdSelection.objects.count() == household_selections_count

    # def test_copy_household_selections_program_no_representation(self) -> None:
    #     no_representation_program = ProgramFactory(status=Program.ACTIVE)
    #     household_selections = HouseholdSelection.objects.filter(target_population=self.target_population1)
    #
    #     copy_household_selections(household_selections=household_selections, program=no_representation_program)
    #
    #     self.household_selection_other_program.refresh_from_db()
    #     assert self.household_selection_other_program.household == self.household_other_program

    # def test_adjust_household_selection_same_program(self) -> None:
    #     household_selections = HouseholdSelection.objects.filter(target_population=self.target_population1)
    #
    #     copy_household_selections(household_selections=household_selections, program=self.other_program)
    #
    #     self.household_selection_other_program.refresh_from_db()
    #     assert self.household_selection_other_program.household == self.household_other_program


class TestCopyRoles(TestCase):
    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory()

        self.other_program = ProgramFactory(status=Program.ACTIVE)
        self.current_program = ProgramFactory(status=Program.ACTIVE)

        self.household_other_program = HouseholdFactory(
            program_id=self.other_program.id,
            business_area=self.business_area,
            head_of_household=IndividualFactory(household=None),
        )
        self.household_current_program = HouseholdFactory(
            program_id=self.current_program.id,
            business_area=self.business_area,
            head_of_household=IndividualFactory(household=None),
            copied_from=self.household_other_program,
            origin_unicef_id=self.household_other_program.unicef_id,
        )

        self.individual_representation_other_program = IndividualFactory(
            program_id=self.other_program.id,
            business_area=self.business_area,
            household=None,
        )

        self.individual_representation_no_program = IndividualFactory(
            business_area=self.business_area,
            household=None,
        )
        self.individual_representation_no_program.copied_from = self.individual_representation_no_program
        self.individual_representation_no_program.origin_unicef_id = self.individual_representation_no_program.unicef_id
        self.individual_representation_no_program.save()

        self.role_individual_representation_other_program = IndividualRoleInHouseholdFactory(
            individual=self.individual_representation_other_program,
            household=self.household_other_program,
            role=ROLE_ALTERNATE,
        )
        self.role_individual_representation_no_program = IndividualRoleInHouseholdFactory(
            individual=self.individual_representation_no_program,
            household=self.household_other_program,
            role=ROLE_PRIMARY,
        )

    # def test_copy_roles(self) -> None:
    #     roles_count = IndividualRoleInHousehold.objects.count()
    #     individual_count = Individual.objects.count()
    #     households = Household.objects.filter(program=self.other_program)
    #
    #     assert self.household_current_program.representatives.count() == 0
    #
    #     copy_roles(households=households, program=self.current_program)
    #
    #     assert self.household_current_program.representatives.count() == 2
    #     assert IndividualRoleInHousehold.objects.count() - roles_count == 2
    #     assert Individual.objects.count() - individual_count == 1


class TestGetBiggestProgram(TestCase):
    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory()
        small_program = ProgramFactory(status=Program.ACTIVE, business_area=self.business_area)
        self.biggest_program = ProgramFactory(status=Program.ACTIVE, business_area=self.business_area)

        HouseholdFactory(
            program_id=small_program.id,
            business_area=self.business_area,
            head_of_household=IndividualFactory(household=None),
        )
        HouseholdFactory(
            program_id=self.biggest_program.id,
            business_area=self.business_area,
            head_of_household=IndividualFactory(household=None),
        )
        HouseholdFactory(
            program_id=self.biggest_program.id,
            business_area=self.business_area,
            head_of_household=IndividualFactory(household=None),
        )

    def test_get_biggest_program(self) -> None:
        assert get_biggest_program(self.business_area) == self.biggest_program


class TestAssignNonProgramRDIToBiggestProgram(TestCase):
    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory.create()
        self.program = ProgramFactory(status=Program.ACTIVE, business_area=self.business_area)
        self.rdi1 = RegistrationDataImportFactory(business_area=self.business_area)
        self.rdi2 = RegistrationDataImportFactory(business_area=self.business_area)
        self.rdi3 = RegistrationDataImportFactory(business_area=self.business_area)

        individual_rdi1 = IndividualFactory(household=None, business_area=self.business_area)
        self.household_rdi1 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=individual_rdi1,
            registration_data_import=self.rdi1,
        )
        individual_rdi1.household = self.household_rdi1
        individual_rdi1.save()

        individual_rdi2 = IndividualFactory(household=None, business_area=self.business_area)
        self.household_rdi2 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=individual_rdi2,
            registration_data_import=self.rdi2,
        )
        individual_rdi2.household = self.household_rdi2
        individual_rdi2.save()

        individual_rdi3 = IndividualFactory(household=None, business_area=self.business_area)
        self.household_rdi3 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=individual_rdi3,
            registration_data_import=self.rdi3,
        )
        individual_rdi3.household = self.household_rdi3
        individual_rdi3.save()

        individual_rdi4 = IndividualFactory(household=None, business_area=self.business_area)
        self.household_rdi4 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=individual_rdi4,
            registration_data_import=self.rdi3,
        )
        individual_rdi4.household = self.household_rdi4
        individual_rdi4.save()

    # def test_assign_non_program_rdi_to_biggest_program(self) -> None:
    #     assert self.rdi1.programs.count() == 0
    #     assert self.rdi2.programs.count() == 0
    #     assert self.rdi3.programs.count() == 0
    #
    #     assign_non_program_objects_to_biggest_program(self.business_area)
    #
    #     self.rdi1.refresh_from_db()
    #     self.rdi2.refresh_from_db()
    #     self.rdi3.refresh_from_db()
    #
    #     assert self.rdi1.programs.count() == 1
    #     assert self.rdi2.programs.count() == 1
    #     assert self.rdi3.programs.count() == 1
    #
    #     assert self.rdi1.programs.first() == get_biggest_program(self.business_area)
    #     assert self.rdi2.programs.first() == get_biggest_program(self.business_area)
    #     assert self.rdi3.programs.first() == get_biggest_program(self.business_area)
    #
    #     self.household_rdi1.refresh_from_db()
    #     self.household_rdi2.refresh_from_db()
    #     self.household_rdi3.refresh_from_db()
    #     self.household_rdi4.refresh_from_db()
    #
    #     assert self.household_rdi1.copied_from == self.household_rdi1
    #     assert self.household_rdi2.copied_from == self.household_rdi2
    #     assert self.household_rdi3.copied_from == self.household_rdi3
    #     assert self.household_rdi4.copied_from == self.household_rdi4


class TestHandleRDIs(TestCase):
    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory()
        self.program1 = ProgramFactory(status=Program.ACTIVE)
        self.program2 = ProgramFactory(status=Program.ACTIVE)
        self.rdi1 = RegistrationDataImportFactory()
        self.rdi2 = RegistrationDataImportFactory()

        self.household_rdi1_1, self.individual_rdi1_1 = create_origin_household_with_individual(
            program_id=self.program1.id,
            business_area=self.business_area,
            household_kwargs={"registration_data_import": self.rdi1},
        )

        IndividualRoleInHouseholdFactory(
            individual=self.individual_rdi1_1,
            household=self.household_rdi1_1,
            role=ROLE_PRIMARY,
        )
        collector_rdi1_1 = IndividualFactory(
            household=None,
            program_id=self.program1.id,
            business_area=self.business_area,
        )
        IndividualRoleInHouseholdFactory(
            individual=collector_rdi1_1,
            household=self.household_rdi1_1,
            role=ROLE_ALTERNATE,
        )

        self.household_rdi1_2, self.individual_rdi1_2 = create_origin_household_with_individual(
            program_id=self.program1.id,
            business_area=self.business_area,
            household_kwargs={"registration_data_import": self.rdi1},
        )

        # data for program 2
        self.household_rdi1_3, self.individual_rdi1_3 = create_origin_household_with_individual(
            program_id=self.program2.id,
            business_area=self.business_area,
            household_kwargs={"registration_data_import": self.rdi1},
        )

        IndividualRoleInHouseholdFactory(
            individual=self.individual_rdi1_3,
            household=self.household_rdi1_3,
            role=ROLE_PRIMARY,
        )
        self.collector_rdi1_3 = IndividualFactory(
            household=None,
            program_id=self.program2.id,
            business_area=self.business_area,
        )
        self.collector_rdi1_3.copied_from = self.collector_rdi1_3
        self.collector_rdi1_3.origin_unicef_id = self.collector_rdi1_3.unicef_id
        self.collector_rdi1_3.save()

        IndividualRoleInHouseholdFactory(
            individual=self.collector_rdi1_3,
            household=self.household_rdi1_3,
            role=ROLE_ALTERNATE,
        )
        # data for objects not yet handled (not assigned to program)
        self.individual_rdi1_4 = IndividualFactory(
            household=None,
            program_id=None,
            business_area=self.business_area,
        )
        self.household_rdi1_4 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual_rdi1_4,
            registration_data_import=self.rdi1,
            program_id=None,
        )
        self.individual_rdi1_4.household = self.household_rdi1_4
        self.individual_rdi1_4.save()

        # data for objects that were already copied and are in the RDI
        self.household_rdi1_5_origin, self.individual_rdi1_5_origin = create_origin_household_with_individual(
            program_id=self.program2.id,
            business_area=self.business_area,
            household_kwargs={"registration_data_import": self.rdi1},
        )
        IndividualRoleInHouseholdFactory(
            individual=self.individual_rdi1_5_origin,
            household=self.household_rdi1_5_origin,
            role=ROLE_PRIMARY,
        )

        self.individual_rdi1_5_representation = IndividualFactory(
            household=None,
            program_id=self.program1.id,
            business_area=self.business_area,
        )
        self.household_rdi1_5_representation = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual_rdi1_5_representation,
            registration_data_import=self.rdi1,
            program_id=self.program1.id,
        )
        self.individual_rdi1_5_representation.household = self.household_rdi1_5_representation
        self.individual_rdi1_5_representation.copied_from = self.individual_rdi1_5_origin
        self.individual_rdi1_5_representation.origin_unicef_id = self.individual_rdi1_5_origin.unicef_id
        self.individual_rdi1_5_representation.save()

        self.household_rdi1_5_representation.copied_from = self.household_rdi1_5_origin
        self.household_rdi1_5_representation.origin_unicef_id = self.household_rdi1_5_origin.unicef_id
        self.household_rdi1_5_representation.save()

        IndividualRoleInHouseholdFactory(
            individual=self.individual_rdi1_5_representation,
            household=self.household_rdi1_5_representation,
            role=ROLE_PRIMARY,
        )
        self.household_rdi1_5_origin.refresh_from_db()
        self.individual_rdi1_5_origin.refresh_from_db()

    # def test_handle_rdis(self) -> None:
    #     household_count = Household.objects.count()
    #     individual_count = Individual.objects.count()
    #     roles_count = IndividualRoleInHousehold.objects.count()
    #
    #     assert self.rdi1.programs.count() == 0
    #
    #     assert self.household_rdi1_5_origin.copied_to.count() == 2
    #     assert self.individual_rdi1_5_origin.copied_to.count() == 2
    #
    #     handle_rdis(
    #         households=Household.objects.filter(business_area=self.business_area),
    #         program=self.program1,
    #     )
    #
    #     self.rdi1.refresh_from_db()
    #
    #     self.household_rdi1_1.refresh_from_db()
    #     self.household_rdi1_2.refresh_from_db()
    #     self.household_rdi1_3.refresh_from_db()
    #     self.household_rdi1_4.refresh_from_db()
    #     self.household_rdi1_5_origin.refresh_from_db()
    #
    #     self.individual_rdi1_4.refresh_from_db()
    #     self.individual_rdi1_5_origin.refresh_from_db()
    #
    #     assert self.rdi1.programs.count() == 1
    #     assert self.rdi1.programs.first() == self.program1
    #
    #     assert Household.objects.count() - household_count == 1
    #     assert Individual.objects.count() - individual_count == 2
    #     assert IndividualRoleInHousehold.objects.count() - roles_count == 2
    #
    #     assert self.household_rdi1_3.copied_to.count() == 2
    #     household_rdi1_3_representation = self.household_rdi1_3.copied_to.exclude(pk=self.household_rdi1_3.pk).first()
    #
    #     assert household_rdi1_3_representation.program_id == self.program1.id
    #     assert household_rdi1_3_representation.registration_data_import == self.rdi1
    #     assert household_rdi1_3_representation.individuals.count() == 1
    #
    #     individual_rdi1_3_representation = household_rdi1_3_representation.individuals.first()
    #     assert individual_rdi1_3_representation.program_id == self.program1.id
    #     assert individual_rdi1_3_representation.household == household_rdi1_3_representation
    #     assert individual_rdi1_3_representation.copied_from == self.individual_rdi1_3
    #     assert individual_rdi1_3_representation.copied_to.count() == 0
    #
    #     # testing representatives
    #     assert household_rdi1_3_representation.representatives.count() == 2
    #     roles_rdi1_3 = IndividualRoleInHousehold.objects.filter(household=household_rdi1_3_representation)
    #
    #     role_primary = roles_rdi1_3.filter(role=ROLE_PRIMARY).first()
    #     assert role_primary.individual == individual_rdi1_3_representation
    #
    #     role_alternate = roles_rdi1_3.filter(role=ROLE_ALTERNATE).first()
    #     assert role_alternate.individual.copied_from == self.collector_rdi1_3
    #     assert role_alternate.individual.program == self.program1
    #
    #     # testing household from rdi that was not in program
    #     assert self.household_rdi1_4.copied_to.count() == 1
    #     assert self.household_rdi1_4.copied_from == self.household_rdi1_4
    #     assert self.household_rdi1_4.program == self.program1
    #     assert self.household_rdi1_4.registration_data_import == self.rdi1
    #
    #     assert self.individual_rdi1_4.copied_to.count() == 1
    #     assert self.individual_rdi1_4.copied_from == self.individual_rdi1_4
    #     assert self.individual_rdi1_4.program == self.program1
    #
    #     # test representation already present in rdi
    #     assert self.household_rdi1_5_representation.copied_to.count() == 0
    #     assert self.individual_rdi1_5_representation.copied_to.count() == 0
    #     assert self.household_rdi1_5_representation.representatives.count() == 1
    #
    #     assert self.household_rdi1_5_origin.copied_to.count() == 2
    #     assert self.individual_rdi1_5_origin.copied_to.count() == 2
