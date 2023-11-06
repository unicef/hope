from typing import Dict, Optional
from unittest import skip

from django.test import TestCase

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.core.fixtures import generate_data_collecting_types
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
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
    COLLECT_TYPE_FULL,
    COLLECT_TYPE_NONE,
    COLLECT_TYPE_PARTIAL,
    COLLECT_TYPE_SIZE_ONLY,
    COLLECT_TYPE_UNKNOWN,
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
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.targeting.fixtures import (
    HouseholdSelectionFactory,
    TargetPopulationFactory,
)
from hct_mis_api.apps.targeting.models import HouseholdSelection
from hct_mis_api.one_time_scripts.migrate_data_to_representations import (
    adjust_payment_records,
    adjust_payments,
    copy_bank_account_info_per_individual,
    copy_document_per_individual,
    copy_entitlement_card_per_household,
    copy_household_representation,
    copy_household_selections,
    copy_individual_identity_per_individual,
    copy_individual_representation,
    copy_roles,
    handle_non_program_objects,
    handle_rdis,
)


def create_origin_household_with_individual(
    business_area: BusinessArea,
    household_kwargs: Optional[Dict] = None,
    individual_kwargs: Optional[Dict] = None,
) -> tuple[Household, Individual]:
    if household_kwargs is None:
        household_kwargs = {}
    if individual_kwargs is None:
        individual_kwargs = {}

    individual = IndividualFactory(
        household=None,
        business_area=business_area,
        **individual_kwargs,
    )
    household = HouseholdFactory(
        business_area=business_area,
        head_of_household=individual,
        **household_kwargs,
    )
    individual.household = household
    individual.save()

    return household, individual


@skip(reason="Skip this test for GPF")
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

    def test_copy_document_per_individual(self) -> None:
        documents_count = Document.original_and_repr_objects.count()
        copy_document_per_individual(self.individual1, self.individual_representation1)

        self.assertEqual(self.individual_representation1.documents(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(Document.original_and_repr_objects.count() - documents_count, 2)


@skip(reason="Skip this test for GPF")
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

    def test_copy_individual_identity_per_individual(self) -> None:
        individual_identities_count = IndividualIdentity.original_and_repr_objects.count()
        copy_individual_identity_per_individual(self.individual1, self.individual_representation1)

        self.assertEqual(self.individual_representation1.identities(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(IndividualIdentity.original_and_repr_objects.count() - individual_identities_count, 2)


@skip(reason="Skip this test for GPF")
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

    def test_copy_bank_account_info_per_individual(self) -> None:
        bank_account_info_count = BankAccountInfo.original_and_repr_objects.count()
        copy_bank_account_info_per_individual(self.individual1, self.individual_representation1)

        self.assertEqual(
            self.individual_representation1.bank_account_info(manager="original_and_repr_objects").count(), 2
        )
        self.assertEqual(BankAccountInfo.original_and_repr_objects.count() - bank_account_info_count, 2)


@skip(reason="Skip this test for GPF")
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

    def test_copy_entitlement_card_per_household(self) -> None:
        entitlement_card_count = EntitlementCard.original_and_repr_objects.count()
        copy_entitlement_card_per_household(self.household1, self.household_representation1)

        self.assertEqual(
            self.household_representation1.entitlement_cards(manager="original_and_repr_objects").count(), 2
        )
        self.assertEqual(EntitlementCard.original_and_repr_objects.count() - entitlement_card_count, 2)


@skip(reason="Skip this test for GPF")
class TestCopyIndividualRepresentation(TestCase):
    def setUp(self) -> None:
        business_area = BusinessAreaFactory()
        self.program = ProgramFactory()
        self.individual1 = IndividualFactory(household=None, business_area=business_area)
        self.individual1.refresh_from_db()
        self.individual1_id = self.individual1.id
        self.document1_1 = create_individual_document(self.individual1)
        self.document1_2 = create_individual_document(self.individual1)
        self.individual_identity1 = IndividualIdentityFactory(individual=self.individual1)
        self.individual_identity2 = IndividualIdentityFactory(individual=self.individual1)
        self.bank_account_info1 = BankAccountInfoFactory(individual=self.individual1)
        self.bank_account_info2 = BankAccountInfoFactory(individual=self.individual1)

    def test_copy_individual_representation_already_exists(self) -> None:
        individual_representation = IndividualFactory(
            copied_from=self.individual1,
            origin_unicef_id=self.individual1.unicef_id,
            household=None,
            program_id=self.program.id,
            business_area=self.individual1.business_area,
            is_original=False,
        )
        documents_count = Document.original_and_repr_objects.count()
        individual_identities_count = IndividualIdentity.original_and_repr_objects.count()
        bank_account_info_count = BankAccountInfo.original_and_repr_objects.count()

        individual = copy_individual_representation(program=self.program, individual=self.individual1)

        self.individual1 = Individual.original_and_repr_objects.get(id=self.individual1_id)

        self.assertEqual(self.individual1.is_original, True)
        self.assertEqual(individual, individual_representation)
        self.assertEqual(Document.original_and_repr_objects.count(), documents_count)
        self.assertEqual(IndividualIdentity.original_and_repr_objects.count(), individual_identities_count)
        self.assertEqual(BankAccountInfo.original_and_repr_objects.count(), bank_account_info_count)

    def test_copy_individual_representation(self) -> None:
        documents_count = Document.original_and_repr_objects.count()
        individual_identities_count = IndividualIdentity.original_and_repr_objects.count()
        bank_account_info_count = BankAccountInfo.original_and_repr_objects.count()
        individual_count = Individual.original_and_repr_objects.count()

        individual = copy_individual_representation(program=self.program, individual=self.individual1)

        self.individual1 = Individual.original_and_repr_objects.get(id=self.individual1_id)

        self.assertEqual(Individual.original_and_repr_objects.count() - individual_count, 1)
        self.assertNotEqual(self.individual1.id, individual.id)
        self.assertEqual(self.individual1.is_original, True)
        self.assertEqual(individual.is_original, False)
        self.assertEqual(individual.copied_from, self.individual1)
        self.assertEqual(individual.origin_unicef_id, self.individual1.unicef_id)
        self.assertEqual(individual.program, self.program)
        self.assertIsNotNone(individual.pk)
        self.assertIsNotNone(individual.unicef_id)
        self.assertEqual(individual.documents(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(
            self.individual1.documents.first().copied_to(manager="original_and_repr_objects").first().individual,
            individual,
        )

        self.assertEqual(individual.identities(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(individual.bank_account_info(manager="original_and_repr_objects").count(), 2)

        self.assertEqual(Document.original_and_repr_objects.count() - documents_count, 2)
        self.assertEqual(IndividualIdentity.original_and_repr_objects.count() - individual_identities_count, 2)
        self.assertEqual(BankAccountInfo.original_and_repr_objects.count() - bank_account_info_count, 2)


@skip(reason="Skip this test for GPF")
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
        self.household1_id = self.household1.id
        # self.entitlement_card1 = EntitlementCardFactory(household=self.household1)
        # self.entitlement_card2 = EntitlementCardFactory(household=self.household1)

        self.individual1.household = self.household1
        self.individual1.save()
        self.individual2.household = self.household1
        self.individual2.copied_from_id = self.individual2.id
        self.individual2.origin_unicef_id = self.individual2.unicef_id
        self.individual2.save()

        self.individual1.refresh_from_db()
        self.individual2.refresh_from_db()
        self.household1.refresh_from_db()

    def test_copy_household_representation_already_exists(self) -> None:
        individual_representation = IndividualFactory(
            copied_from=self.individual1,
            origin_unicef_id=self.individual1.unicef_id,
            household=None,
            program_id=self.program.id,
            business_area=self.individual1.business_area,
            is_original=False,
        )
        # self.household1 representation already in self.program
        household_representation = HouseholdFactory(
            copied_from=self.household1,
            head_of_household=individual_representation,
            origin_unicef_id=self.household1.unicef_id,
            program_id=self.program.id,
            business_area=self.household1.business_area,
            is_original=False,
        )
        household_count = Household.original_and_repr_objects.count()
        # entitlement_card_count = EntitlementCard.original_and_repr_objects.count()
        individual_count = Individual.original_and_repr_objects.count()
        documents_count = Document.original_and_repr_objects.count()
        individual_identities_count = IndividualIdentity.original_and_repr_objects.count()
        bank_account_info_count = BankAccountInfo.original_and_repr_objects.count()

        copy_household_representation(
            program=self.program, household=self.household1, individuals=[self.individual1, self.individual2]
        )

        self.household1 = Household.original_and_repr_objects.get(id=self.household1_id)

        self.assertEqual(Household.original_and_repr_objects.count(), household_count)
        # self.assertEqual(EntitlementCard.original_and_repr_objects.count(), entitlement_card_count)
        self.assertEqual(Individual.original_and_repr_objects.count(), individual_count)
        self.assertEqual(Document.original_and_repr_objects.count(), documents_count)
        self.assertEqual(IndividualIdentity.original_and_repr_objects.count(), individual_identities_count)
        self.assertEqual(BankAccountInfo.original_and_repr_objects.count(), bank_account_info_count)
        self.assertEqual(
            Household.original_and_repr_objects.filter(copied_from=self.household1, program=self.program).first().id,
            household_representation.id,
        )

    def test_copy_household_representation(self) -> None:
        household_count = Household.original_and_repr_objects.count()
        # entitlement_card_count = EntitlementCard.original_and_repr_objects.count()
        individual_count = Individual.original_and_repr_objects.count()
        documents_count = Document.original_and_repr_objects.count()
        individual_identities_count = IndividualIdentity.original_and_repr_objects.count()
        bank_account_info_count = BankAccountInfo.original_and_repr_objects.count()

        copy_household_representation(
            program=self.program, household=self.household1, individuals=[self.individual1, self.individual2]
        )

        self.household1 = Household.original_and_repr_objects.get(id=self.household1_id)

        household_representation = (
            self.household1.copied_to(manager="original_and_repr_objects").filter(program=self.program).first()
        )

        self.assertEqual(household_representation.copied_from, self.household1)
        self.assertEqual(self.household1.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertNotEqual(household_representation.pk, self.household1.pk)
        self.assertEqual(household_representation.copied_from, self.household1)
        self.assertEqual(household_representation.origin_unicef_id, self.household1.unicef_id)
        # self.assertEqual(household_representation.entitlement_cards(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(household_representation.individuals(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(
            household_representation.individuals(manager="original_and_repr_objects")
            .first()
            .documents(manager="original_and_repr_objects")
            .count(),
            2,
        )
        self.assertEqual(
            household_representation.individuals(manager="original_and_repr_objects")
            .first()
            .identities(manager="original_and_repr_objects")
            .count(),
            2,
        )
        self.assertEqual(
            household_representation.individuals(manager="original_and_repr_objects")
            .first()
            .bank_account_info(manager="original_and_repr_objects")
            .count(),
            2,
        )

        self.assertEqual(Household.original_and_repr_objects.count() - household_count, 1)
        # self.assertEqual(EntitlementCard.original_and_repr_objects.count() - entitlement_card_count, 2)
        self.assertEqual(Individual.original_and_repr_objects.count() - individual_count, 2)
        self.assertEqual(Document.original_and_repr_objects.count() - documents_count, 4)
        self.assertEqual(IndividualIdentity.original_and_repr_objects.count() - individual_identities_count, 4)
        self.assertEqual(BankAccountInfo.original_and_repr_objects.count() - bank_account_info_count, 4)


@skip(reason="Skip this test for GPF")
class TestAdjustPayments(TestCase):
    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory()
        self.other_program = ProgramFactory(status=Program.ACTIVE)
        self.target_population1 = TargetPopulationFactory(program=self.other_program, business_area=self.business_area)
        payment_plan = PaymentPlanFactory(target_population=self.target_population1)
        (
            self.household_original,
            self.individual_original,
        ) = create_origin_household_with_individual(business_area=self.business_area)
        self.payment1 = PaymentFactory(
            parent=payment_plan,
            household=self.household_original,
            collector=self.individual_original,
            head_of_household=self.individual_original,
            currency="PLN",
        )

    def test_adjust_payments(self) -> None:
        this_program = ProgramFactory(business_area=self.business_area, status=Program.ACTIVE)

        individual_representation_this_program = IndividualFactory(
            program_id=this_program.id,
            business_area=self.business_area,
            copied_from=self.individual_original,
            origin_unicef_id=self.individual_original.unicef_id,
            household=None,
            is_original=False,
        )

        household_this_program = HouseholdFactory(
            program_id=this_program.id,
            business_area=self.business_area,
            copied_from=self.household_original,
            origin_unicef_id=self.household_original.unicef_id,
            head_of_household=individual_representation_this_program,
            is_original=False,
        )

        self.target_population1.program = this_program
        self.target_population1.save()

        adjust_payments(self.business_area)

        self.payment1.refresh_from_db()
        self.assertEqual(self.payment1.collector, individual_representation_this_program)
        self.assertEqual(self.payment1.head_of_household, individual_representation_this_program)
        self.assertEqual(self.payment1.household, household_this_program)


@skip(reason="Skip this test for GPF")
class TestAdjustPaymentRecords(TestCase):
    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory()
        self.other_program = ProgramFactory(status=Program.ACTIVE, business_area=self.business_area)
        self.target_population1 = TargetPopulationFactory(program=self.other_program, business_area=self.business_area)
        (
            self.household_original,
            self.individual_original,
        ) = create_origin_household_with_individual(
            business_area=self.business_area,
        )
        self.payment_record1 = PaymentRecordFactory(
            target_population=self.target_population1,
            household=self.household_original,
            head_of_household=self.individual_original,
            service_provider=ServiceProvider.objects.first() or ServiceProviderFactory(),
            business_area=self.business_area,
        )

    def test_adjust_payment_records(self) -> None:
        this_program = ProgramFactory(status=Program.ACTIVE, business_area=self.business_area)

        individual_representation_this_program = IndividualFactory(
            program_id=this_program.id,
            business_area=self.business_area,
            copied_from=self.individual_original,
            origin_unicef_id=self.individual_original.unicef_id,
            household=None,
            is_original=False,
        )

        household_this_program = HouseholdFactory(
            program_id=this_program.id,
            business_area=self.business_area,
            copied_from=self.household_original,
            origin_unicef_id=self.household_original.unicef_id,
            head_of_household=individual_representation_this_program,
            is_original=False,
        )

        self.target_population1.program = this_program
        self.target_population1.save()

        adjust_payment_records(self.business_area)

        self.payment_record1.refresh_from_db()

        self.assertEqual(self.payment_record1.head_of_household, individual_representation_this_program)
        self.assertEqual(self.payment_record1.household, household_this_program)


@skip(reason="Skip this test for GPF")
class TestCopyHouseholdSelections(TestCase):
    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory()
        self.program = ProgramFactory(status=Program.ACTIVE)

        self.target_population1 = TargetPopulationFactory(program=self.program, business_area=self.business_area)

        self.household_original = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=IndividualFactory(household=None),
        )
        self.household_selection_original = HouseholdSelectionFactory(
            target_population=self.target_population1,
            household=self.household_original,
            is_original=True,
        )
        self.household_selection_original_id = self.household_selection_original.id
        self.household_representation = HouseholdFactory(
            program_id=self.program.id,
            business_area=self.business_area,
            head_of_household=IndividualFactory(household=None),
            copied_from=self.household_original,
            origin_unicef_id=self.household_original.unicef_id,
            is_original=False,
        )

    def test_copy_household_selections(self) -> None:
        household_selections_count = HouseholdSelection.original_and_repr_objects.count()
        household_selections = HouseholdSelection.original_and_repr_objects.filter(
            target_population=self.target_population1
        )

        copy_household_selections(household_selections=household_selections, program=self.program)

        household_selection_original = HouseholdSelection.original_and_repr_objects.get(
            id=self.household_selection_original_id
        )
        household_selection = HouseholdSelection.original_and_repr_objects.filter(
            is_original=False, household__copied_from=self.household_original
        ).first()

        self.assertEqual(
            household_selection_original.household.copied_to(manager="original_and_repr_objects").first(),
            household_selection.household,
        )
        self.assertEqual(HouseholdSelection.original_and_repr_objects.count() - household_selections_count, 1)
        self.assertEqual(household_selection.household, self.household_representation)
        self.assertNotEqual(household_selection.household, household_selection_original.household)


@skip(reason="Skip this test for GPF")
class TestCopyRoles(TestCase):
    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory()

        self.program = ProgramFactory(status=Program.ACTIVE)

        self.household_original = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=IndividualFactory(household=None),
        )
        self.household_original_id = self.household_original.id
        self.household_representation = HouseholdFactory(
            program_id=self.program.id,
            business_area=self.business_area,
            head_of_household=IndividualFactory(household=None),
            copied_from=self.household_original,
            origin_unicef_id=self.household_original.unicef_id,
            is_original=False,
        )

        self.individual_original = IndividualFactory(
            business_area=self.business_area,
            household=self.household_original,
        )
        self.individual_representation = IndividualFactory(
            program_id=self.program.id,
            business_area=self.business_area,
            household=self.household_representation,
            copied_from=self.individual_original,
            origin_unicef_id=self.individual_original.unicef_id,
            is_original=False,
        )

        # individual not handled yet (not a part of any household in processed program but an external collector in one)
        self.external_collector = IndividualFactory(
            business_area=self.business_area,
            household=None,
        )

        self.role_individual_representation_processed_individual = IndividualRoleInHouseholdFactory(
            individual=self.individual_original,
            household=self.household_original,
            role=ROLE_ALTERNATE,
        )
        self.role_individual_representation_not_processed_individual = IndividualRoleInHouseholdFactory(
            individual=self.external_collector,
            household=self.household_original,
            role=ROLE_PRIMARY,
        )

    def test_copy_roles(self) -> None:
        roles_count = IndividualRoleInHousehold.original_and_repr_objects.count()
        individual_count = Individual.original_and_repr_objects.count()
        households = Household.original_and_repr_objects.filter(id=self.household_original_id)

        self.assertEqual(
            IndividualRoleInHousehold.original_and_repr_objects.filter(household__in=households).count(), 2
        )
        self.assertEqual(self.household_representation.representatives(manager="original_and_repr_objects").count(), 0)

        copy_roles(households=households, program=self.program)

        # new individual copy for the external collector
        self.assertEqual(Individual.original_and_repr_objects.count() - individual_count, 1)
        self.assertEqual(IndividualRoleInHousehold.original_and_repr_objects.count() - roles_count, 2)
        self.assertEqual(self.household_representation.representatives(manager="original_and_repr_objects").count(), 2)


@skip(reason="Skip this test for GPF")
class TestCreateStorageProgramForCollectingType(TestCase):
    def setUp(self) -> None:
        generate_data_collecting_types()
        self.partial = DataCollectingType.objects.get(code="partial_individuals")
        self.full = DataCollectingType.objects.get(code="full_collection")
        self.size_only = DataCollectingType.objects.get(code="size_only")
        self.no_ind_data = DataCollectingType.objects.get(code="size_age_gender_disaggregated")

        self.business_area = BusinessAreaFactory.create()
        self.rdi1 = RegistrationDataImportFactory(business_area=self.business_area)
        self.rdi2 = RegistrationDataImportFactory(business_area=self.business_area)
        self.rdi3 = RegistrationDataImportFactory(business_area=self.business_area)

        self.individual_rdi_1 = IndividualFactory(household=None, business_area=self.business_area)
        self.household_rdi_1 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual_rdi_1,
            registration_data_import=self.rdi1,
            collect_individual_data=COLLECT_TYPE_PARTIAL,
        )
        self.individual_rdi_1.household = self.household_rdi_1
        self.individual_rdi_1.save()

        self.individual_rdi_2 = IndividualFactory(household=None, business_area=self.business_area)
        self.household_rdi_2 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual_rdi_2,
            registration_data_import=self.rdi2,
            collect_individual_data=COLLECT_TYPE_FULL,
        )
        self.individual_rdi_2.household = self.household_rdi_2
        self.individual_rdi_2.save()

        self.individual_rdi_3 = IndividualFactory(household=None, business_area=self.business_area)
        self.household_rdi_3 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual_rdi_3,
            registration_data_import=self.rdi3,
            collect_individual_data=COLLECT_TYPE_SIZE_ONLY,
        )
        self.individual_rdi_3.household = self.household_rdi_3
        self.individual_rdi_3.save()

        self.individual_rdi_4 = IndividualFactory(household=None, business_area=self.business_area)
        self.household_rdi_4 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual_rdi_4,
            registration_data_import=self.rdi3,
            collect_individual_data=COLLECT_TYPE_NONE,
        )
        self.individual_rdi_4.household = self.household_rdi_4
        self.individual_rdi_4.save()

        self.individual_rdi_5 = IndividualFactory(household=None, business_area=self.business_area)
        self.household_rdi_5 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual_rdi_5,
            collect_individual_data=COLLECT_TYPE_NONE,
        )
        self.individual_rdi_5.household = self.household_rdi_5
        self.individual_rdi_5.save()

        self.individual_6 = IndividualFactory(household=None, business_area=self.business_area)
        self.household_6 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual_6,
            collect_individual_data=COLLECT_TYPE_UNKNOWN,
        )
        self.individual_6.household = self.household_6
        self.individual_6.save()

    def test_create_storage_program_for_collecting_type(self) -> None:
        self.assertIsNone(self.rdi1.program)
        self.assertIsNone(self.rdi2.program)
        self.assertIsNone(self.rdi3.program)

        self.assertEqual(self.rdi1.households(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(self.rdi2.households(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(self.rdi3.households(manager="original_and_repr_objects").count(), 2)

        households_count = Household.original_and_repr_objects.count()
        individuals_count = Individual.original_and_repr_objects.count()

        handle_non_program_objects(self.business_area)

        assert (
            Program.all_objects.filter(
                business_area=self.business_area,
                data_collecting_type=self.partial,
            ).count()
            == 1
        )

        assert (
            Program.all_objects.filter(
                business_area=self.business_area,
                data_collecting_type=self.full,
            ).count()
            == 1
        )
        assert (
            Program.all_objects.filter(
                business_area=self.business_area,
                data_collecting_type=self.size_only,
            ).count()
            == 1
        )
        assert (
            Program.all_objects.filter(
                business_area=self.business_area,
                data_collecting_type=self.no_ind_data,
            ).count()
            == 1
        )

        partial_program = Program.all_objects.filter(
            business_area=self.business_area,
            data_collecting_type=self.partial,
        ).first()
        full_program = Program.all_objects.filter(
            business_area=self.business_area,
            data_collecting_type=self.full,
        ).first()
        size_only_program = Program.all_objects.filter(
            business_area=self.business_area,
            data_collecting_type=self.size_only,
        ).first()
        no_ind_data_program = Program.all_objects.filter(
            business_area=self.business_area,
            data_collecting_type=self.no_ind_data,
        ).first()
        self.unknown = DataCollectingType.objects.get(code="unknown")
        unknown_program = Program.all_objects.filter(
            business_area=self.business_area,
            data_collecting_type=self.unknown,
        ).first()

        for void_storage_program in [
            partial_program,
            full_program,
            size_only_program,
            no_ind_data_program,
            unknown_program,
        ]:
            self.assertFalse(void_storage_program.is_visible)

        self.rdi1.refresh_from_db()
        self.rdi2.refresh_from_db()
        self.rdi3.refresh_from_db()

        self.assertEqual(
            self.rdi1.program,
            partial_program,
        )
        self.assertEqual(
            self.rdi2.program,
            full_program,
        )
        self.assertIn(self.rdi3.program, [size_only_program, no_ind_data_program])

        self.household_rdi_1.refresh_from_db()
        self.household_rdi_2.refresh_from_db()
        self.household_rdi_3.refresh_from_db()
        self.household_rdi_4.refresh_from_db()
        self.household_rdi_5.refresh_from_db()
        self.household_6.refresh_from_db()

        # check if original households are not changed
        for hh in [
            self.household_rdi_1,
            self.household_rdi_2,
            self.household_rdi_3,
            self.household_rdi_4,
            self.household_rdi_5,
            self.household_6,
        ]:
            self.assertEqual(hh.program_id, None)
            self.assertEqual(hh.is_original, True)
            self.assertEqual(hh.copied_from, None)

        # check if new households were created from original households and assigned to corresponding programs
        self.assertEqual(self.rdi1.households(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.rdi2.households(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.rdi3.households(manager="original_and_repr_objects").count(), 4)

        household_representation1 = (
            self.rdi1.households(manager="original_and_repr_objects").filter(is_original=False).first()
        )
        household_representation2 = (
            self.rdi2.households(manager="original_and_repr_objects").filter(is_original=False).first()
        )
        household_representation3 = (
            self.rdi3.households(manager="original_and_repr_objects")
            .filter(is_original=False, copied_from=self.household_rdi_3)
            .first()
        )
        household_representation4 = (
            self.rdi3.households(manager="original_and_repr_objects")
            .filter(is_original=False, copied_from=self.household_rdi_4)
            .first()
        )
        household_representation5 = self.household_rdi_5.copied_to(manager="original_and_repr_objects").first()
        household_representation6 = self.household_6.copied_to(manager="original_and_repr_objects").first()

        self.assertEqual(household_representation1.program, partial_program)
        self.assertEqual(household_representation1.copied_from, self.household_rdi_1)
        self.assertEqual(household_representation2.program, full_program)
        self.assertEqual(household_representation2.copied_from, self.household_rdi_2)
        self.assertEqual(household_representation3.program, size_only_program)
        self.assertEqual(household_representation4.program, no_ind_data_program)
        self.assertEqual(household_representation5.program, no_ind_data_program)
        self.assertEqual(household_representation6.program, unknown_program)

        self.assertEqual(Household.original_and_repr_objects.count() - households_count, 6)

        individual_representation1 = household_representation1.head_of_household
        individual_representation2 = household_representation2.head_of_household
        individual_representation3 = household_representation3.head_of_household
        individual_representation4 = household_representation4.head_of_household
        individual_representation5 = household_representation5.head_of_household
        individual_representation6 = household_representation6.head_of_household

        self.assertEqual(individual_representation1.program, partial_program)
        self.assertEqual(individual_representation1.copied_from, self.individual_rdi_1)
        self.assertEqual(individual_representation2.program, full_program)
        self.assertEqual(individual_representation2.copied_from, self.individual_rdi_2)
        self.assertEqual(individual_representation3.program, size_only_program)
        self.assertEqual(individual_representation3.copied_from, self.individual_rdi_3)
        self.assertEqual(individual_representation4.program, no_ind_data_program)
        self.assertEqual(individual_representation4.copied_from, self.individual_rdi_4)
        self.assertEqual(individual_representation5.program, no_ind_data_program)
        self.assertEqual(individual_representation5.copied_from, self.individual_rdi_5)
        self.assertEqual(individual_representation6.program, unknown_program)
        self.assertEqual(individual_representation6.copied_from, self.individual_6)

        self.assertEqual(Individual.original_and_repr_objects.count() - individuals_count, 6)


@skip(reason="Skip this test for GPF")
class TestHandleRDIs(TestCase):
    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory()
        self.program1 = ProgramFactory(status=Program.ACTIVE)
        self.program2 = ProgramFactory(status=Program.ACTIVE)
        self.rdi1 = RegistrationDataImportFactory()
        self.rdi2 = RegistrationDataImportFactory()

        # original household and individual
        self.household_rdi1_1, self.individual_rdi1_1 = create_origin_household_with_individual(
            business_area=self.business_area,
            household_kwargs={"registration_data_import": self.rdi1},
            individual_kwargs={"registration_data_import": self.rdi1},
        )
        # representations already exist in program1
        self.household_rdi1_1_repr, self.individual_rdi1_1_repr = create_origin_household_with_individual(
            business_area=self.business_area,
            household_kwargs={
                "registration_data_import": self.rdi1,
                "program": self.program1,
                "is_original": False,
                "copied_from": self.household_rdi1_1,
            },
            individual_kwargs={
                "registration_data_import": self.rdi1,
                "program": self.program1,
                "is_original": False,
                "copied_from": self.individual_rdi1_1,
            },
        )
        # at the point of handling rdis, roles are not handled yet - so only roles for original objects exist
        IndividualRoleInHouseholdFactory(
            individual=self.individual_rdi1_1,
            household=self.household_rdi1_1,
            role=ROLE_PRIMARY,
        )
        # external collector individual
        self.collector_rdi1_1 = IndividualFactory(
            household=None,
            business_area=self.business_area,
        )
        # collector individual was already copied into representation for program1 when handling its household
        self.collector_rdi1_1_repr = IndividualFactory(
            household=None,
            program_id=self.program1.id,
            business_area=self.business_area,
            is_original=False,
            copied_from=self.collector_rdi1_1,
        )
        IndividualRoleInHouseholdFactory(
            individual=self.collector_rdi1_1,
            household=self.household_rdi1_1,
            role=ROLE_ALTERNATE,
        )

        self.household_rdi1_2, self.individual_rdi1_2 = create_origin_household_with_individual(
            business_area=self.business_area,
            household_kwargs={"registration_data_import": self.rdi1},
            individual_kwargs={"registration_data_import": self.rdi1},
        )
        # representations already exist in program2
        self.household_rdi1_2_repr, self.individual_rdi1_2_repr = create_origin_household_with_individual(
            business_area=self.business_area,
            household_kwargs={
                "registration_data_import": self.rdi1,
                "program": self.program2,
                "is_original": False,
                "copied_from": self.household_rdi1_2,
            },
            individual_kwargs={
                "registration_data_import": self.rdi1,
                "program": self.program2,
                "is_original": False,
                "copied_from": self.individual_rdi1_2,
            },
        )
        IndividualRoleInHouseholdFactory(
            individual=self.individual_rdi1_2,
            household=self.household_rdi1_2,
            role=ROLE_PRIMARY,
        )

        # household and individual that did were not copied to any program as they did not fulfill the criteria - they will be copied while handling their RDI
        self.household_rdi1_3, self.individual_rdi1_3 = create_origin_household_with_individual(
            business_area=self.business_area,
            household_kwargs={"registration_data_import": self.rdi1},
            individual_kwargs={"registration_data_import": self.rdi1},
        )
        self.individual_rdi1_3_1 = IndividualFactory(
            household=self.household_rdi1_3,
            business_area=self.business_area,
            registration_data_import=self.rdi1,
        )

        IndividualRoleInHouseholdFactory(
            individual=self.individual_rdi1_3,
            household=self.household_rdi1_3,
            role=ROLE_PRIMARY,
        )
        # external collector individual
        self.collector_rdi1_3 = IndividualFactory(
            household=None,
            business_area=self.business_area,
        )
        # collector individual was already copied into representation for program2 when handling its household
        self.collector_rdi1_3_repr = IndividualFactory(
            household=None,
            program_id=self.program2.id,
            business_area=self.business_area,
            is_original=False,
            copied_from=self.collector_rdi1_3,
        )

        IndividualRoleInHouseholdFactory(
            individual=self.collector_rdi1_3,
            household=self.household_rdi1_3,
            role=ROLE_ALTERNATE,
        )

    def test_handle_rdis(self) -> None:
        households_count = Household.original_and_repr_objects.count()
        individual_count = Individual.original_and_repr_objects.count()
        roles_count = IndividualRoleInHousehold.original_and_repr_objects.count()

        self.assertIsNone(self.rdi1.program)

        self.assertEqual(self.household_rdi1_1.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(self.individual_rdi1_1.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(self.collector_rdi1_1.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(self.household_rdi1_2.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(self.individual_rdi1_2.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(self.household_rdi1_3.copied_to(manager="original_and_repr_objects").count(), 0)
        self.assertEqual(self.individual_rdi1_3.copied_to(manager="original_and_repr_objects").count(), 0)
        self.assertEqual(self.individual_rdi1_3_1.copied_to(manager="original_and_repr_objects").count(), 0)
        self.assertEqual(self.collector_rdi1_3.copied_to(manager="original_and_repr_objects").count(), 1)

        self.assertEqual(self.rdi1.households(manager="original_and_repr_objects").count(), 5)
        self.assertEqual(self.rdi1.individuals(manager="original_and_repr_objects").count(), 6)

        handle_rdis(
            rdis=RegistrationDataImport.objects.filter(business_area=self.business_area),
            program=self.program1,
        )
        self.rdi1.refresh_from_db()
        self.assertEqual(self.rdi1.program, self.program1)
        # 5 initial households, 1 household_rdi1_2 copy for program1, 1 household_rdi1_3 copy for program1
        self.assertEqual(self.rdi1.households(manager="original_and_repr_objects").count(), 7)
        # 6 initial individuals, 1 individual_rdi1_2 copy for program1, 1 individual_rdi1_3 copy for program1, 1 individual_rdi1_3_1 copy for program1
        self.assertEqual(self.rdi1.individuals(manager="original_and_repr_objects").count(), 9)
        # additional 1 household_rdi1_2 copy for program1, 1 household_rdi1_3 copy for program1
        self.assertEqual(Household.original_and_repr_objects.count() - households_count, 2)
        # additional 1 individual_rdi1_2 copy for program1, 1 individual_rdi1_3 copy for program1, 1 collector_rdi1_3 copy for program1, 1 individual_rdi1_3_1 copy for program1
        self.assertEqual(Individual.original_and_repr_objects.count() - individual_count, 4)
        # additional 2 roles for household_rdi1_1 in program1, 1 role for household_rdi1_2 in program1, 2 roles for household_rdi1_3 in program1
        self.assertEqual(IndividualRoleInHousehold.original_and_repr_objects.count() - roles_count, 5)

        handle_rdis(
            rdis=RegistrationDataImport.objects.filter(business_area=self.business_area),
            program=self.program2,
        )

        self.assertIn(self.rdi1.program, [self.program1, self.program2])

        # 5 initial households, 1 household_rdi1_2 copy for program1, 1 household_rdi1_1 copy for program2, 1 household_rdi1_3 copy for program1, 1 household_rdi1_3 copy for program2
        self.assertEqual(self.rdi1.households(manager="original_and_repr_objects").count(), 9)
        # 6 initial individuals, 1 individual_rdi1_2 copy for program1, 1 individual_rdi1_1 copy for program2, 2 individual_rdi1_3 copies for program1 and progam2, 2 individual_rdi1_3_1 copies for program1 and program2
        self.assertEqual(self.rdi1.individuals(manager="original_and_repr_objects").count(), 12)
        # additional 1 household_rdi1_1 copy for program2, 1 household_rdi1_2 copy for program1, 1 household_rdi1_3 copy for program1, 1 household_rdi1_3 copy for program2
        self.assertEqual(Household.original_and_repr_objects.count() - households_count, 4)
        # additional 1 individual_rdi1_1 copy for program2, 1 collector_rdi1_1 copy for program2, 1 individual_rdi1_2 copy for program1, 1 individual_rdi1_3 copy for program1, 1 individual_rdi1_3 copy for program2, 1 collector_rdi1_3 copy for program1, 2 individual_rdi1_3_1 copies for program1 and program2
        self.assertEqual(Individual.original_and_repr_objects.count() - individual_count, 8)
        # additional 4 roles for household_rdi1_1 in program1 and program2, 2 roles for household_rdi1_2 in program1 and program2, 4 roles for household_rdi1_3 in program1 and program2
        self.assertEqual(IndividualRoleInHousehold.original_and_repr_objects.count() - roles_count, 10)

        self.assertEqual(self.household_rdi1_1.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.individual_rdi1_1.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.collector_rdi1_1.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.household_rdi1_2.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.individual_rdi1_2.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.household_rdi1_3.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.individual_rdi1_3.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.individual_rdi1_3_1.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.collector_rdi1_3.copied_to(manager="original_and_repr_objects").count(), 2)

        self.assertIsNotNone(
            Household.original_and_repr_objects.filter(copied_from=self.household_rdi1_1, program=self.program1).first()
        )
        self.assertIsNotNone(
            Household.original_and_repr_objects.filter(copied_from=self.household_rdi1_1, program=self.program2).first()
        )
        self.assertIsNotNone(
            Individual.original_and_repr_objects.filter(
                copied_from=self.individual_rdi1_1, program=self.program1
            ).first()
        )
        self.assertIsNotNone(
            Individual.original_and_repr_objects.filter(
                copied_from=self.individual_rdi1_1, program=self.program2
            ).first()
        )
        self.assertIsNotNone(
            Individual.original_and_repr_objects.filter(
                copied_from=self.collector_rdi1_1, program=self.program1
            ).first()
        )
        self.assertIsNotNone(
            Individual.original_and_repr_objects.filter(
                copied_from=self.collector_rdi1_1, program=self.program2
            ).first()
        )
        self.assertIsNotNone(
            Household.original_and_repr_objects.filter(copied_from=self.household_rdi1_2, program=self.program1).first()
        )
        self.assertIsNotNone(
            Household.original_and_repr_objects.filter(copied_from=self.household_rdi1_2, program=self.program2).first()
        )
        self.assertIsNotNone(
            Individual.original_and_repr_objects.filter(
                copied_from=self.individual_rdi1_2, program=self.program1
            ).first()
        )
        self.assertIsNotNone(
            Individual.original_and_repr_objects.filter(
                copied_from=self.individual_rdi1_2, program=self.program2
            ).first()
        )
        self.assertIsNotNone(
            Household.original_and_repr_objects.filter(copied_from=self.household_rdi1_3, program=self.program1).first()
        )
        self.assertIsNotNone(
            Household.original_and_repr_objects.filter(copied_from=self.household_rdi1_3, program=self.program2).first()
        )
        self.assertIsNotNone(
            Individual.original_and_repr_objects.filter(
                copied_from=self.individual_rdi1_3, program=self.program1
            ).first()
        )
        self.assertIsNotNone(
            Individual.original_and_repr_objects.filter(
                copied_from=self.individual_rdi1_3, program=self.program2
            ).first()
        )
        self.assertIsNotNone(
            Individual.original_and_repr_objects.filter(
                copied_from=self.individual_rdi1_3_1, program=self.program1
            ).first()
        )
        self.assertIsNotNone(
            Individual.original_and_repr_objects.filter(
                copied_from=self.individual_rdi1_3_1, program=self.program2
            ).first()
        )
        self.assertIsNotNone(
            Individual.original_and_repr_objects.filter(
                copied_from=self.collector_rdi1_3, program=self.program1
            ).first()
        )
        self.assertIsNotNone(
            Individual.original_and_repr_objects.filter(
                copied_from=self.collector_rdi1_3, program=self.program2
            ).first()
        )

        self.assertEqual(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                household__copied_from=self.household_rdi1_1, individual__copied_from=self.individual_rdi1_1
            ).count(),
            2,
        )
        self.assertEqual(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                household__copied_from=self.household_rdi1_1, individual__copied_from=self.collector_rdi1_1
            ).count(),
            2,
        )
        self.assertEqual(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                household__copied_from=self.household_rdi1_2, individual__copied_from=self.individual_rdi1_2
            ).count(),
            2,
        )
        self.assertEqual(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                household__copied_from=self.household_rdi1_3, individual__copied_from=self.individual_rdi1_3
            ).count(),
            2,
        )
        self.assertEqual(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                household__copied_from=self.household_rdi1_3, individual__copied_from=self.collector_rdi1_3
            ).count(),
            2,
        )
