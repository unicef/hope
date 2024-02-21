from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
)
from hct_mis_api.apps.household.models import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    BankAccountInfo,
    Document,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.utils import enroll_household_to_program


class TestEnrolHouseholdToProgram(TestCase):
    """Test enroll household to program."""

    def setUp(self) -> None:
        create_afghanistan()
        self.program1 = ProgramFactory()
        self.program2 = ProgramFactory()

        # test for enrolment with existing repr
        self.household_original_already_enrolled = HouseholdFactory(
            program=self.program1,
            head_of_household=IndividualFactory(household=None),
        )
        self.individual_already_enrolled = IndividualFactory(household=None)
        self.household_already_enrolled = HouseholdFactory(
            program=self.program2,
            head_of_household=self.individual_already_enrolled,
            copied_from=self.household_original_already_enrolled,
            unicef_id=self.household_original_already_enrolled.unicef_id,
        )
        self.individual_already_enrolled.household = self.household_already_enrolled
        self.individual_already_enrolled.save()

        # test for enrolment with new repr creation
        self.individual_hoh = IndividualFactory(household=None, program=self.program1)
        self.individual1 = IndividualFactory(household=None, program=self.program1)
        self.individual1_document = DocumentFactory(
            individual=self.individual1,
        )
        self.individual1_identity = IndividualIdentityFactory(
            individual=self.individual1,
        )
        self.individual1_bank_account_info = BankAccountInfoFactory(
            individual=self.individual1,
        )

        self.individual_2_original = IndividualFactory(household=None, program=self.program1)
        self.individual_2_already_enrolled = IndividualFactory(household=None, program=self.program2)
        self.individual_2_already_enrolled.copied_from = self.individual_2_original
        self.individual_2_already_enrolled.save()
        self.individual_2_already_enrolled_document = DocumentFactory(
            individual=self.individual_2_already_enrolled,
        )
        self.individual_2_already_enrolled_identity = IndividualIdentityFactory(
            individual=self.individual_2_already_enrolled,
        )
        self.individual_2_already_enrolled_bank_account_info = BankAccountInfoFactory(
            individual=self.individual_2_already_enrolled,
        )

        self.household = HouseholdFactory(
            program=self.program1,
            head_of_household=self.individual_hoh,
        )
        self.household.refresh_from_db()
        self.original_household_id = self.household.id
        self.household.individuals.set([self.individual1, self.individual_2_original])

        self.individual_hoh.household = self.household
        self.individual_hoh.save()

        self.role1 = IndividualRoleInHouseholdFactory(
            individual=self.individual1,
            household=self.household,
            role=ROLE_PRIMARY,
        )

        self.role2 = IndividualRoleInHouseholdFactory(
            individual=self.individual_2_original,
            household=self.household,
            role=ROLE_ALTERNATE,
        )

        # household with external collector - collector enrolled outside of household.individuals
        self.individual_hoh_e = IndividualFactory(household=None, program=self.program1)
        self.household_external = HouseholdFactory(
            program=self.program1,
            head_of_household=self.individual_hoh_e,
        )
        self.individual_hoh_e.household = self.household_external
        self.individual_hoh_e.save()

        self.individual_external = IndividualFactory(household=None, program=self.program1)
        self.role_external = IndividualRoleInHouseholdFactory(
            individual=self.individual_external,
            household=self.household_external,
            role=ROLE_PRIMARY,
        )

    def test_enroll_household_to_program_already_enrolled(self) -> None:
        hh_count = Household.objects.count()
        ind_count = Individual.objects.count()

        hh, value = enroll_household_to_program(self.household_already_enrolled, self.program2)
        self.assertEqual(hh, self.household_already_enrolled)
        self.assertEqual(value, 0)
        self.assertEqual(hh_count, Household.objects.count())
        self.assertEqual(ind_count, Individual.objects.count())

    def test_enroll_original_household_to_program_representation_already_enrolled(self) -> None:
        hh_count = Household.objects.count()
        ind_count = Individual.objects.count()

        hh, value = enroll_household_to_program(self.household_original_already_enrolled, self.program2)
        self.assertEqual(hh, self.household_already_enrolled)
        self.assertEqual(value, 0)
        self.assertEqual(hh_count, Household.objects.count())
        self.assertEqual(ind_count, Individual.objects.count())

    def test_enroll_household_to_program(self) -> None:
        hh_count = Household.original_and_repr_objects.count()
        ind_count = Individual.original_and_repr_objects.count()
        document_count = Document.objects.count()
        identities_count = IndividualIdentity.objects.count()
        bank_account_info_count = BankAccountInfo.objects.count()
        roles_count = IndividualRoleInHousehold.objects.count()

        hh, value = enroll_household_to_program(self.household, self.program2)
        self.assertEqual(value, 1)

        self.individual_2_already_enrolled.refresh_from_db()
        # 1 new hh enrolled to program2
        self.assertEqual(hh_count + 1, Household.original_and_repr_objects.count())
        # 2 new individuals enrolled to program2, individual1 and individual_hoh, individual2 was already in program 2
        self.assertEqual(ind_count + 2, Individual.original_and_repr_objects.count())
        # 1 new object related to individual1 enrolled to program2
        self.assertEqual(document_count + 1, Document.objects.count())
        self.assertEqual(identities_count + 1, IndividualIdentity.objects.count())
        self.assertEqual(bank_account_info_count + 1, BankAccountInfo.objects.count())
        self.assertEqual(roles_count + 2, IndividualRoleInHousehold.objects.count())

        original_household = Household.objects.get(id=self.original_household_id)
        enrolled_household = original_household.copied_to.first()
        self.assertEqual(original_household.copied_to.count(), 1)
        self.assertEqual(enrolled_household.program, self.program2)
        self.assertEqual(enrolled_household.unicef_id, original_household.unicef_id)
        self.assertEqual(
            enrolled_household.head_of_household,
            self.individual_hoh.copied_to.filter(program=self.program2).first(),
        )
        self.assertEqual(
            enrolled_household.individuals.count(),
            original_household.individuals.count(),
            2,
        )
        self.assertEqual(
            enrolled_household.individuals.first().program,
            self.program2,
        )

        self.assertIsNotNone(
            IndividualRoleInHousehold.objects.filter(
                individual=self.individual1.copied_to.filter(program=self.program2).first(),
                household=enrolled_household,
                role=ROLE_PRIMARY,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.objects.filter(
                individual=self.individual_2_original.copied_to.filter(program=self.program2).first(),
                household=enrolled_household,
                role=ROLE_ALTERNATE,
            ).first()
        )

    def test_enroll_household_with_external_collector(self) -> None:
        hh_count = Household.original_and_repr_objects.count()
        ind_count = Individual.original_and_repr_objects.count()
        roles_count = IndividualRoleInHousehold.objects.count()

        hh, value = enroll_household_to_program(self.household_external, self.program2)
        self.assertEqual(value, 1)
        self.assertEqual(hh_count + 1, Household.original_and_repr_objects.count())
        # 2 new individuals enrolled - individual_external and individual_hoh
        self.assertEqual(ind_count + 2, Individual.original_and_repr_objects.count())
        self.assertEqual(roles_count + 1, IndividualRoleInHousehold.objects.count())

        self.assertEqual(
            hh.head_of_household,
            self.individual_hoh_e.copied_to.filter(program=self.program2).first(),
        )
        self.assertIsNotNone(self.individual_external.copied_to.filter(program=self.program2).first())
        self.assertIsNotNone(
            IndividualRoleInHousehold.objects.filter(
                individual=self.individual_external.copied_to.filter(program=self.program2).first(),
                household=hh,
                role=ROLE_PRIMARY,
            ).first()
        )
