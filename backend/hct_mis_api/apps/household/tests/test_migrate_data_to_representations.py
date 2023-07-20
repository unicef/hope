from unittest import TestCase

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
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
from hct_mis_api.apps.household.utils import migrate_data_to_representations
from hct_mis_api.apps.payment.fixtures import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentRecordFactory,
    ServiceProviderFactory,
)
from hct_mis_api.apps.payment.models import Payment, PaymentRecord, ServiceProvider
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation


class TestMigrateDataToRepresentations(TestCase):
    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory()
        Program.objects.filter(business_area=self.business_area).delete()
        # programs
        self.program_active = ProgramFactory(
            business_area=self.business_area,
            status=Program.ACTIVE,
        )
        self.program_finished1 = ProgramFactory(
            business_area=self.business_area,
            status=Program.FINISHED,
        )
        self.program_finished2 = ProgramFactory(
            business_area=self.business_area,
            status=Program.FINISHED,
        )
        # RDIs
        self.rdi1 = RegistrationDataImportFactory(business_area=self.business_area)

        # TargetPopulations
        # for active programs target population status does not matter
        self.target_population1 = TargetPopulationFactory(
            business_area=self.business_area,
            program=self.program_active,
            status=TargetPopulation.STATUS_OPEN,
        )

        self.target_population2 = TargetPopulationFactory(
            business_area=self.business_area,
            program=self.program_finished1,
            status=TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
        )

        self.target_population_wrong = TargetPopulationFactory(
            business_area=self.business_area,
            program=self.program_finished1,
            status=TargetPopulation.STATUS_OPEN,
        )

        self.target_population3 = TargetPopulationFactory(
            business_area=self.business_area,
            program=self.program_finished2,
            status=TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
        )
        # Make sure that program_active is the biggest
        for _ in range(10):
            individual = IndividualFactory(business_area=self.business_area, household=None)
            household = HouseholdFactory(
                business_area=self.business_area,
                head_of_household=individual,
            )
            individual.household = household
            individual.save()
            household.target_populations.set([self.target_population1])

        # Household1 and its data (no RDI, in 2 programs)
        self.individual1_1 = IndividualFactory(business_area=self.business_area, household=None)
        self.document1_1_1 = DocumentFactory(individual=self.individual1_1)
        self.document1_1_2 = DocumentFactory(individual=self.individual1_1)
        self.identity1_1 = IndividualIdentityFactory(individual=self.individual1_1)
        self.bank_account_info1_1 = BankAccountInfoFactory(individual=self.individual1_1)

        self.household1 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual1_1,
        )
        self.household1.target_populations.set([self.target_population1, self.target_population2])

        self.individual1_1.household = self.household1
        self.individual1_1.save()
        self.individual1_2 = IndividualFactory(business_area=self.business_area, household=self.household1)
        self.document1_2_1 = DocumentFactory(individual=self.individual1_2)

        self.individual1_3 = IndividualFactory(business_area=self.business_area, household=self.household1)

        self.role1_1 = IndividualRoleInHouseholdFactory(
            individual=self.individual1_2,
            household=self.household1,
            role=ROLE_PRIMARY,
        )
        self.role1_2 = IndividualRoleInHouseholdFactory(
            individual=self.individual1_3,
            household=self.household1,
            role=ROLE_ALTERNATE,
        )

        # Payments 1
        payment_plan1 = PaymentPlanFactory(
            business_area=self.business_area,
            target_population=self.target_population1,
        )
        self.payment1 = PaymentFactory(
            business_area=self.business_area,
            parent=payment_plan1,
            collector=self.individual1_2,
            household=self.household1,
            head_of_household=self.individual1_1,
        )

        self.payment_record1 = PaymentRecordFactory(
            business_area=self.business_area,
            target_population=self.target_population1,
            household=self.household1,
            head_of_household=self.individual1_1,
            service_provider=ServiceProvider.objects.first() or ServiceProviderFactory() or ServiceProviderFactory(),
        )

        # Household2 and its data (no RDI, in 2 programs)
        self.individual2_1 = IndividualFactory(business_area=self.business_area, household=None)
        self.document2_1_1 = DocumentFactory(individual=self.individual2_1)
        self.document2_1_2 = DocumentFactory(individual=self.individual2_1)
        self.identity2_1 = IndividualIdentityFactory(individual=self.individual2_1)
        self.bank_account_info2_1 = BankAccountInfoFactory(individual=self.individual2_1)

        self.household2 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual2_1,
        )
        self.household2.target_populations.set([self.target_population1, self.target_population2])

        self.individual2_1.household = self.household2
        self.individual2_1.save()
        self.individual2_2 = IndividualFactory(business_area=self.business_area, household=self.household2)
        self.document2_2_1 = DocumentFactory(individual=self.individual1_2)

        self.collector2_1 = IndividualFactory(business_area=self.business_area, household=None)

        # external collector
        IndividualRoleInHouseholdFactory(
            individual=self.collector2_1,
            household=self.household2,
            role=ROLE_PRIMARY,
        )
        # external collector from household1
        IndividualRoleInHouseholdFactory(
            individual=self.individual1_1,
            household=self.household2,
            role=ROLE_ALTERNATE,
        )

        # Payments 2
        payment_plan2 = PaymentPlanFactory(
            business_area=self.business_area,
            target_population=self.target_population2,
        )
        self.payment2 = PaymentFactory(
            business_area=self.business_area,
            parent=payment_plan2,
            collector=self.collector2_1,
            household=self.household2,
            head_of_household=self.individual2_1,
        )

        self.payment_record2 = PaymentRecordFactory(
            business_area=self.business_area,
            target_population=self.target_population2,
            household=self.household2,
            head_of_household=self.collector2_1,
            service_provider=ServiceProvider.objects.first() or ServiceProviderFactory(),
        )

        # Household3 and its data (in wrong target population)
        self.individual3_1 = IndividualFactory(business_area=self.business_area, household=None)
        self.household3 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual3_1,
        )
        self.household3.target_populations.set([self.target_population_wrong])

        # Household4 and its data (without target population)
        self.rdi4_1 = RegistrationDataImportFactory(business_area=self.business_area)
        self.individual4_1 = IndividualFactory(business_area=self.business_area, household=None)
        self.household4 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual4_1,
            registration_data_import=self.rdi4_1,
        )

        # Household 5, 6 and 7 and their data (has rdi with 3 households)
        self.rdi_with_3_hhs = RegistrationDataImportFactory(business_area=self.business_area)
        self.individual5_1 = IndividualFactory(business_area=self.business_area, household=None)
        self.household5 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual5_1,
            registration_data_import=self.rdi_with_3_hhs,
        )
        self.household5.target_populations.set([self.target_population1, self.target_population2])

        self.collector5_1 = IndividualFactory(business_area=self.business_area, household=None)
        self.role_primary5 = IndividualRoleInHouseholdFactory(
            individual=self.collector5_1,
            household=self.household5,
            role=ROLE_PRIMARY,
        )
        self.collector5_2 = IndividualFactory(business_area=self.business_area, household=None)
        self.role_alternate5 = IndividualRoleInHouseholdFactory(
            individual=self.collector5_2,
            household=self.household5,
            role=ROLE_ALTERNATE,
        )

        self.individual6_1 = IndividualFactory(business_area=self.business_area, household=None)
        self.household6 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual6_1,
            registration_data_import=self.rdi_with_3_hhs,
        )
        self.collector5_1.household = self.household6
        self.collector5_1.save()

        self.individual7_1 = IndividualFactory(business_area=self.business_area, household=None)
        self.household7 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual7_1,
            registration_data_import=self.rdi_with_3_hhs,
        )
        self.household7.target_populations.set([self.target_population3])
        self.role_primary7 = IndividualRoleInHouseholdFactory(
            individual=self.collector5_1,
            household=self.household7,
            role=ROLE_PRIMARY,
        )

        self.role_alternate7 = IndividualRoleInHouseholdFactory(
            individual=self.collector5_2,
            household=self.household7,
            role=ROLE_ALTERNATE,
        )

        # Payments 5
        payment_plan5 = PaymentPlanFactory(
            business_area=self.business_area,
            target_population=self.target_population2,
        )
        self.payment5 = PaymentFactory(
            business_area=self.business_area,
            parent=payment_plan5,
            collector=self.collector5_1,
            household=self.household5,
            head_of_household=self.individual5_1,
        )

        self.payment_record5 = PaymentRecordFactory(
            business_area=self.business_area,
            target_population=self.target_population2,
            household=self.household5,
            head_of_household=self.individual5_1,
            service_provider=ServiceProvider.objects.first() or ServiceProviderFactory(),
        )
        # Payments 7
        payment_plan7 = PaymentPlanFactory(
            business_area=self.business_area,
            target_population=self.target_population3,
        )
        self.payment7 = PaymentFactory(
            business_area=self.business_area,
            parent=payment_plan7,
            collector=self.collector5_1,
            household=self.household7,
            head_of_household=self.individual7_1,
        )

        self.payment_record7 = PaymentRecordFactory(
            business_area=self.business_area,
            target_population=self.target_population3,
            household=self.household7,
            head_of_household=self.individual7_1,
            service_provider=ServiceProvider.objects.first() or ServiceProviderFactory(),
        )

    def refresh_objects(self):
        self.household1.refresh_from_db()
        self.individual1_1.refresh_from_db()
        self.individual1_2.refresh_from_db()
        self.individual1_3.refresh_from_db()
        self.household2.refresh_from_db()
        self.individual2_1.refresh_from_db()
        self.individual2_2.refresh_from_db()
        self.household3.refresh_from_db()
        self.individual3_1.refresh_from_db()
        self.household4.refresh_from_db()
        self.individual4_1.refresh_from_db()
        self.rdi4_1.refresh_from_db()
        self.role1_1.refresh_from_db()
        self.role1_2.refresh_from_db()
        self.collector2_1.refresh_from_db()
        self.payment1.refresh_from_db()
        self.payment_record1.refresh_from_db()
        self.payment2.refresh_from_db()
        self.payment_record2.refresh_from_db()
        self.target_population_wrong.refresh_from_db()
        self.household5.refresh_from_db()
        self.individual5_1.refresh_from_db()
        self.household6.refresh_from_db()
        self.individual6_1.refresh_from_db()
        self.household7.refresh_from_db()
        self.individual7_1.refresh_from_db()
        self.collector5_1.refresh_from_db()
        self.collector5_2.refresh_from_db()
        self.role_primary5.refresh_from_db()
        self.role_alternate5.refresh_from_db()
        self.role_primary7.refresh_from_db()
        self.role_alternate7.refresh_from_db()
        self.payment5.refresh_from_db()
        self.payment_record5.refresh_from_db()
        self.payment7.refresh_from_db()
        self.payment_record7.refresh_from_db()
        self.rdi_with_3_hhs.refresh_from_db()

    def test_migrate_data_to_representations(self):
        household_count = Household.objects.filter(business_area=self.business_area).count()
        individual_count = Individual.objects.filter(business_area=self.business_area).count()
        document_count = Document.objects.filter(individual__business_area=self.business_area).count()
        identity_count = IndividualIdentity.objects.filter(individual__business_area=self.business_area).count()
        bank_account_info_count = BankAccountInfo.objects.filter(individual__business_area=self.business_area).count()
        household_selection_count = HouseholdSelection.objects.filter(
            household__business_area=self.business_area
        ).count()
        payment_count = Payment.objects.filter(business_area=self.business_area).count()
        payment_record_count = PaymentRecord.objects.filter(business_area=self.business_area).count()

        migrate_data_to_representations(business_area=self.business_area)

        assert Household.objects.filter(business_area=self.business_area).count() - household_count == 8
        assert Individual.objects.filter(business_area=self.business_area).count() - individual_count == 16
        assert Document.objects.filter(individual__business_area=self.business_area).count() - document_count == 6
        assert (
            IndividualIdentity.objects.filter(individual__business_area=self.business_area).count() - identity_count
            == 2
        )
        assert (
            BankAccountInfo.objects.filter(individual__business_area=self.business_area).count()
            - bank_account_info_count
            == 2
        )
        assert (
            HouseholdSelection.objects.filter(household__business_area=self.business_area).count()
            - household_selection_count
            == 0
        )
        assert Payment.objects.filter(business_area=self.business_area).count() - payment_count == 0
        assert PaymentRecord.objects.filter(business_area=self.business_area).count() - payment_record_count == 0

        self.refresh_objects()

        # Test household1
        assert self.household1.program == self.program_active
        assert self.household1.target_populations.count() == 1
        assert self.household1.target_populations.first() == self.target_population1
        assert self.household1.head_of_household == self.individual1_1
        assert self.household1.copied_from == self.household1
        assert self.household1.origin_unicef_id == self.household1.unicef_id
        assert self.household1.copied_to.count() == 2
        assert self.household1.individuals.count() == 3
        assert self.household1.representatives.count() == 2

        household1_representation = self.household1.copied_to.exclude(id=self.household1.id).first()
        individual_representation1_1 = self.individual1_1.copied_to.exclude(id=self.individual1_1.id).first()

        assert household1_representation.program == self.program_finished1
        assert household1_representation.target_populations.count() == 1
        assert household1_representation.target_populations.first() == self.target_population2
        assert household1_representation.head_of_household == individual_representation1_1
        assert household1_representation.copied_from == self.household1
        assert household1_representation.origin_unicef_id == self.household1.unicef_id
        assert household1_representation.copied_to.count() == 0
        assert household1_representation.individuals.count() == 3
        assert household1_representation.representatives.count() == 2

        assert individual_representation1_1.household == household1_representation
        assert individual_representation1_1.copied_from == self.individual1_1
        assert individual_representation1_1.origin_unicef_id == self.individual1_1.unicef_id
        assert individual_representation1_1.copied_to.count() == 0
        assert individual_representation1_1.documents.count() == 2
        assert individual_representation1_1.identities.count() == 1
        assert individual_representation1_1.bank_account_info.count() == 1

        representation_document_ids = list(individual_representation1_1.documents.values_list("id", flat=True))
        origin_document_ids = list(self.individual1_1.documents.values_list("id", flat=True))
        for uuid in representation_document_ids:
            assert uuid != origin_document_ids[0]
            assert uuid != origin_document_ids[1]

        assert individual_representation1_1.documents.filter(
            document_number=self.individual1_1.documents.first().document_number
        ).exists()
        assert individual_representation1_1.documents.filter(
            document_number=self.individual1_1.documents.last().document_number
        ).exists()

        assert individual_representation1_1.identities.first().number == self.individual1_1.identities.first().number
        assert individual_representation1_1.identities.first().id != self.individual1_1.identities.first().id

        assert (
            individual_representation1_1.bank_account_info.first().bank_account_number
            == self.individual1_1.bank_account_info.first().bank_account_number
        )
        assert (
            individual_representation1_1.bank_account_info.first().id != self.individual1_1.bank_account_info.first().id
        )

        assert self.role1_1.household == self.household1
        assert self.role1_1.individual == self.individual1_2

        representation_role_primary1 = IndividualRoleInHousehold.objects.get(
            household=household1_representation,
            role=ROLE_PRIMARY,
        )
        assert representation_role_primary1.pk != self.role1_1.pk
        assert representation_role_primary1.household.copied_from == self.role1_1.household
        assert representation_role_primary1.individual.copied_from == self.role1_1.individual

        representation_role_alternate1 = IndividualRoleInHousehold.objects.get(
            household=household1_representation,
            role=ROLE_ALTERNATE,
        )
        assert representation_role_alternate1.pk != self.role1_2.pk
        assert representation_role_alternate1.household.copied_from == self.role1_2.household
        assert representation_role_alternate1.individual.copied_from == self.role1_2.individual

        assert self.payment1.collector == self.individual1_2
        assert self.payment1.household == self.household1
        assert self.payment1.head_of_household == self.individual1_1

        assert self.payment_record1.household == self.household1
        assert self.payment_record1.head_of_household == self.individual1_1

        # Test household2
        household2_representation = self.household2.copied_to.exclude(id=self.household2.id).first()
        representation_role_primary2 = IndividualRoleInHousehold.objects.get(
            household=household2_representation,
            role=ROLE_PRIMARY,
        )

        assert representation_role_primary2.individual.copied_from == self.collector2_1
        assert self.collector2_1.copied_from == self.collector2_1
        assert self.collector2_1.origin_unicef_id == self.collector2_1.unicef_id
        assert self.collector2_1.copied_to.count() == 2

        representation_role_alternate2 = IndividualRoleInHousehold.objects.get(
            household=household2_representation,
            role=ROLE_ALTERNATE,
        )
        assert representation_role_alternate2.individual == individual_representation1_1

        assert self.payment2.collector == representation_role_primary2.individual
        assert self.payment2.household == household2_representation
        assert self.payment2.head_of_household == self.individual2_1.copied_to.exclude(id=self.individual2_1.id).first()

        assert self.payment_record2.household == household2_representation
        assert self.payment_record2.head_of_household == representation_role_primary2.individual

        # Household3
        assert self.household3.program == self.program_active
        assert self.household3.copied_from == self.household3
        assert self.household3.origin_unicef_id == self.household3.unicef_id
        assert self.household3.copied_to.count() == 1

        assert self.individual3_1.program == self.program_active
        assert self.individual3_1.copied_from == self.individual3_1
        assert self.individual3_1.origin_unicef_id == self.individual3_1.unicef_id
        assert self.individual3_1.copied_to.count() == 1

        assert self.target_population_wrong.is_removed is True

        # Household4
        assert self.household4.program == self.program_active
        assert self.household4.copied_from == self.household4
        assert self.household4.origin_unicef_id == self.household4.unicef_id
        assert self.household4.copied_to.count() == 1

        assert self.individual4_1.program == self.program_active
        assert self.individual4_1.copied_from == self.individual4_1
        assert self.individual4_1.origin_unicef_id == self.individual4_1.unicef_id
        assert self.individual4_1.copied_to.count() == 1

        assert self.rdi4_1.programs.count() == 1
        assert self.rdi4_1.programs.first() == self.program_active

        # Household 5, 6, 7
        assert self.household5.program == self.program_active
        assert self.household5.copied_from == self.household5
        assert self.household5.origin_unicef_id == self.household5.unicef_id
        assert self.household5.copied_to.count() == 3

        assert self.household6.copied_to.count() == 3
        assert self.household7.copied_to.count() == 3

        assert self.collector5_1.copied_to.count() == 3
        assert (
            IndividualRoleInHousehold.objects.get(
                household=self.household5,
                role=ROLE_PRIMARY,
            ).individual
            == self.collector5_1
        )
        assert (
            IndividualRoleInHousehold.objects.get(
                household=self.household7,
                role=ROLE_PRIMARY,
            ).individual
            == self.collector5_1
        )
        assert self.collector5_1.household == self.household6

        representation1_household5 = Household.objects.get(program=self.program_finished1, copied_from=self.household5)
        representation1_household6 = Household.objects.get(program=self.program_finished1, copied_from=self.household6)
        representation1_household7 = Household.objects.get(program=self.program_finished1, copied_from=self.household7)
        representation1_collector5_1 = Individual.objects.get(
            program=self.program_finished1,
            copied_from=self.collector5_1,
        )
        assert representation1_collector5_1.copied_to.count() == 0
        assert (
            IndividualRoleInHousehold.objects.get(
                household=representation1_household5,
                role=ROLE_PRIMARY,
            ).individual
            == representation1_collector5_1
        )
        assert (
            IndividualRoleInHousehold.objects.get(
                household=representation1_household7,
                role=ROLE_PRIMARY,
            ).individual
            == representation1_collector5_1
        )
        assert representation1_collector5_1.household == representation1_household6

        representation2_household5 = Household.objects.get(program=self.program_finished2, copied_from=self.household5)
        representation2_household6 = Household.objects.get(program=self.program_finished2, copied_from=self.household6)
        representation2_household7 = Household.objects.get(program=self.program_finished2, copied_from=self.household7)
        representation2_collector5_1 = Individual.objects.get(
            program=self.program_finished2,
            copied_from=self.collector5_1,
        )
        assert representation2_collector5_1.copied_to.count() == 0
        assert (
            IndividualRoleInHousehold.objects.get(
                household=representation2_household5,
                role=ROLE_PRIMARY,
            ).individual
            == representation2_collector5_1
        )
        assert (
            IndividualRoleInHousehold.objects.get(
                household=representation2_household7,
                role=ROLE_PRIMARY,
            ).individual
            == representation2_collector5_1
        )
        assert representation2_collector5_1.household == representation2_household6

        assert self.collector5_2.copied_to.count() == 3
        assert (
            IndividualRoleInHousehold.objects.get(
                household=self.household5,
                role=ROLE_ALTERNATE,
            ).individual.copied_from
            == self.collector5_2
        )
        assert (
            IndividualRoleInHousehold.objects.get(
                household=self.household7,
                role=ROLE_ALTERNATE,
            ).individual.copied_from
            == self.collector5_2
        )
        assert self.collector5_2.household is None

        assert list(self.collector5_2.copied_to.values_list("household", flat=True).distinct()) == [None]

        assert self.payment5.collector == Individual.objects.get(
            program=self.program_finished1, copied_from=self.collector5_1
        )
        assert self.payment5.household == Household.objects.get(
            program=self.program_finished1, copied_from=self.household5
        )
        assert self.payment5.head_of_household == Individual.objects.get(
            program=self.program_finished1,
            copied_from=self.individual5_1,
        )

        assert self.payment_record5.household == Household.objects.get(
            program=self.program_finished1, copied_from=self.household5
        )
        assert self.payment_record5.head_of_household == Individual.objects.get(
            program=self.program_finished1,
            copied_from=self.individual5_1,
        )

        assert self.payment7.collector == Individual.objects.get(
            program=self.program_finished2, copied_from=self.collector5_1
        )
        assert self.payment7.household == Household.objects.get(
            program=self.program_finished2, copied_from=self.household7
        )
        assert self.payment7.head_of_household == Individual.objects.get(
            program=self.program_finished2,
            copied_from=self.individual7_1,
        )

        assert self.payment_record7.household == Household.objects.get(
            program=self.program_finished2, copied_from=self.household7
        )
        assert self.payment_record7.head_of_household == Individual.objects.get(
            program=self.program_finished2,
            copied_from=self.individual7_1,
        )

        assert self.rdi_with_3_hhs.programs.count() == 3
        assert self.program_active in self.rdi_with_3_hhs.programs.all()
        assert self.program_finished1 in self.rdi_with_3_hhs.programs.all()
        assert self.program_finished2 in self.rdi_with_3_hhs.programs.all()
