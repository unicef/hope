from types import TracebackType
from typing import List, Optional

from django.db import DEFAULT_DB_ALIAS, connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.core.fixtures import generate_data_collecting_types
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
)
from hct_mis_api.apps.household.models import (
    COLLECT_TYPE_FULL,
    COLLECT_TYPE_NONE,
    COLLECT_TYPE_PARTIAL,
    COLLECT_TYPE_SIZE_ONLY,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Household,
    Individual,
)
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentRecordFactory,
    ServiceProviderFactory,
)
from hct_mis_api.apps.payment.models import ServiceProvider
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.one_time_scripts.migrate_data_to_representations import (
    copy_household_representation_for_programs_fast,
    copy_individual,
    copy_individual_fast,
    migrate_data_to_representations_per_business_area,
)


class _AssertNumQueriesContext(CaptureQueriesContext):
    def __init__(self, test_case: TestCase, num: int, connection: BaseDatabaseWrapper) -> None:
        self.test_case = test_case
        self.num = num
        super().__init__(connection)

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        super().__exit__(exc_type, exc_value, traceback)  # type: ignore
        if exc_type is not None:
            return
        executed = len(self)
        self.test_case.assertEqual(
            executed,
            self.num,
            "%d queries executed, %d expected\n"
            % (
                executed,
                self.num,
            ),
        )


class TestMigrateDataToRepresentationsPerformance(TestCase):
    def create_hh_with_ind(
        self,
        ind_data: dict,
        hh_data: dict,
        is_rdi: bool = False,
        target_populations: Optional[List[TargetPopulation]] = None,
    ) -> tuple:
        if is_rdi:
            rdi = RegistrationDataImportFactory(business_area=self.business_area)
        else:
            rdi = None
        individual = IndividualFactory(
            business_area=self.business_area,
            household=None,
            **ind_data,
        )
        household = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=individual,
            **hh_data,
        )
        if target_populations:
            household.target_populations.set(target_populations)
        else:
            household.target_populations.set([])
        individual.household = household
        individual.save()
        return individual, household, rdi

    def setUp(self) -> None:
        self.business_area = BusinessAreaFactory(name="Other BA")
        self.business_area_afghanistan = BusinessAreaFactory(name="Afghanistan")
        self.business_area_congo = BusinessAreaFactory(name="Democratic Republic of Congo")
        self.business_area_sudan = BusinessAreaFactory(name="Sudan")
        BusinessAreaFactory(name="Trinidad & Tobago")
        BusinessAreaFactory(name="Slovakia")
        BusinessAreaFactory(name="Sri Lanka")

        # collecting_types
        generate_data_collecting_types()
        self.partial = DataCollectingType.objects.get(code="partial_individuals")
        self.full = DataCollectingType.objects.get(code="full_collection")
        self.size_only = DataCollectingType.objects.get(code="size_only")
        self.no_ind_data = DataCollectingType.objects.get(code="size_age_gender_disaggregated")

        Program.objects.all().delete()
        # programs
        self.program_active = ProgramFactory(
            status=Program.ACTIVE,
            business_area=self.business_area,
            data_collecting_type=self.partial,
        )
        self.program_finished1 = ProgramFactory(
            status=Program.FINISHED,
            business_area=self.business_area,
            data_collecting_type=self.full,
        )
        self.program_finished2 = ProgramFactory(
            status=Program.FINISHED,
            business_area=self.business_area,
            data_collecting_type=self.full,
        )
        # RDIs
        self.rdi1 = RegistrationDataImportFactory(business_area=self.business_area)

        # TargetPopulations
        # TP with status open
        self.target_population1 = TargetPopulationFactory(
            program=self.program_active,
            status=TargetPopulation.STATUS_OPEN,
            business_area=self.business_area,
        )
        # TP with status ready for cash assist
        self.target_population_paid = TargetPopulationFactory(
            program=self.program_finished1,
            status=TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
            business_area=self.business_area,
        )

        self.target_population_open_in_program_finished = TargetPopulationFactory(
            program=self.program_finished1,
            status=TargetPopulation.STATUS_OPEN,
            business_area=self.business_area,
        )

        self.target_population3 = TargetPopulationFactory(
            program=self.program_finished2,
            status=TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
            business_area=self.business_area,
        )

        # Household1 and its data (no RDI, in 2 programs)
        self.individual1_1 = IndividualFactory(business_area=self.business_area, household=None)
        self.document1_1_1 = DocumentFactory(individual=self.individual1_1, program=None)
        self.document1_1_2 = DocumentFactory(individual=self.individual1_1, program=None)
        self.identity1_1 = IndividualIdentityFactory(individual=self.individual1_1)
        self.bank_account_info1_1 = BankAccountInfoFactory(individual=self.individual1_1)

        self.household1 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual1_1,
            registration_data_import=None,
            collect_individual_data=COLLECT_TYPE_NONE,
        )
        self.household1.target_populations.set([self.target_population1, self.target_population_paid])

        self.individual1_1.household = self.household1
        self.individual1_1.save()
        self.individual1_2 = IndividualFactory(business_area=self.business_area, household=self.household1)
        self.document1_2_1 = DocumentFactory(individual=self.individual1_2, program=None)

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
            target_population=self.target_population1,
            program=self.program_active,
        )

        self.payment1 = PaymentFactory(
            parent=payment_plan1,
            collector=self.individual1_2,
            household=self.household1,
            head_of_household=self.individual1_1,
            program=self.program_active,
            entitlement_quantity=103,
            currency="PLN",
        )
        cash_plan = CashPlanFactory(
            program=self.program_active,
        )

        self.payment_record1 = PaymentRecordFactory(
            target_population=self.target_population1,
            household=self.household1,
            head_of_household=self.individual1_1,
            service_provider=ServiceProvider.objects.first() or ServiceProviderFactory(),
            parent=cash_plan,
            currency="PLN",
        )

        # Household2 and its data (no RDI, in 2 programs)
        self.individual2_1 = IndividualFactory(business_area=self.business_area, household=None)
        self.document2_1_1 = DocumentFactory(individual=self.individual2_1, program=None)
        self.document2_1_2 = DocumentFactory(individual=self.individual2_1, program=None)
        self.identity2_1 = IndividualIdentityFactory(individual=self.individual2_1)
        self.bank_account_info2_1 = BankAccountInfoFactory(individual=self.individual2_1)

        self.household2 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual2_1,
            registration_data_import=None,
            collect_individual_data=COLLECT_TYPE_NONE,
        )
        self.household2.target_populations.set([self.target_population1, self.target_population_paid])

        self.individual2_1.household = self.household2
        self.individual2_1.save()
        self.individual2_2 = IndividualFactory(business_area=self.business_area, household=self.household2)
        self.document2_2_1 = DocumentFactory(individual=self.individual2_2, program=None)

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
            target_population=self.target_population_paid,
            program=self.program_active,
        )
        self.payment2 = PaymentFactory(
            parent=payment_plan2,
            collector=self.collector2_1,
            household=self.household2,
            head_of_household=self.individual2_1,
            program=self.program_active,
            currency="PLN",
        )

        self.payment_record2 = PaymentRecordFactory(
            target_population=self.target_population_paid,
            household=self.household2,
            head_of_household=self.collector2_1,
            service_provider=ServiceProvider.objects.first() or ServiceProviderFactory(),
            parent=cash_plan,
            currency="PLN",
        )

        # Household3 and its data
        # Additional helper individual that will already be enrolled into a different program
        # and is representative in the household3
        self.individual_helper3 = IndividualFactory(business_area=self.business_area, household=None)
        self.household_helper = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual_helper3,
            registration_data_import=None,
            collect_individual_data=COLLECT_TYPE_NONE,
        )
        self.individual_helper3.household = self.household_helper
        self.individual_helper3.save()
        self.document_helper = DocumentFactory(individual=self.individual_helper3, program=None)
        self.household_helper.target_populations.set([self.target_population3])

        self.individual3_1 = IndividualFactory(business_area=self.business_area, household=None)
        self.household3 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual3_1,
            collect_individual_data=COLLECT_TYPE_NONE,
        )
        self.document3_1 = DocumentFactory(individual=self.individual3_1, program=None)
        self.individual3_1.household = self.household3
        self.individual3_1.save()
        self.household3.target_populations.set([self.target_population_open_in_program_finished])
        self.role_primary3 = IndividualRoleInHouseholdFactory(
            individual=self.individual_helper3,
            household=self.household3,
            role=ROLE_PRIMARY,
        )
        self.role_alternate3 = IndividualRoleInHouseholdFactory(
            individual=self.individual3_1,
            household=self.household3,
            role=ROLE_ALTERNATE,
        )

        # Household4 and its data (without target population)
        self.rdi4_1 = RegistrationDataImportFactory(business_area=self.business_area)
        self.individual4_1 = IndividualFactory(
            business_area=self.business_area, household=None, registration_data_import=self.rdi4_1
        )
        self.household4 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual4_1,
            registration_data_import=self.rdi4_1,
            collect_individual_data=COLLECT_TYPE_FULL,
        )
        self.individual4_1.household = self.household4
        self.individual4_1.save()
        self.document4_1 = DocumentFactory(individual=self.individual4_1, program=None)
        self.role_primary4 = IndividualRoleInHouseholdFactory(
            individual=self.individual4_1,
            household=self.household4,
            role=ROLE_PRIMARY,
        )

        # Household 5, 6 and 7 and their data (has rdi with 3 households)
        self.rdi_with_3_hhs = RegistrationDataImportFactory(business_area=self.business_area)
        self.individual5_1 = IndividualFactory(
            business_area=self.business_area,
            household=None,
            registration_data_import=self.rdi_with_3_hhs,
        )
        self.household5 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual5_1,
            registration_data_import=self.rdi_with_3_hhs,
            collect_individual_data=COLLECT_TYPE_NONE,
        )
        self.individual5_1.household = self.household5
        self.individual5_1.save()
        self.household5.target_populations.set([self.target_population1, self.target_population_paid])

        self.collector5_1 = IndividualFactory(
            business_area=self.business_area, household=None, registration_data_import=self.rdi_with_3_hhs
        )
        self.role_primary5 = IndividualRoleInHouseholdFactory(
            individual=self.collector5_1,
            household=self.household5,
            role=ROLE_PRIMARY,
        )
        self.collector5_2 = IndividualFactory(
            business_area=self.business_area, household=None, registration_data_import=self.rdi_with_3_hhs
        )
        self.role_alternate5 = IndividualRoleInHouseholdFactory(
            individual=self.collector5_2,
            household=self.household5,
            role=ROLE_ALTERNATE,
        )

        self.individual6_1 = IndividualFactory(
            business_area=self.business_area, household=None, registration_data_import=self.rdi_with_3_hhs
        )
        self.household6 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual6_1,
            registration_data_import=self.rdi_with_3_hhs,
            collect_individual_data=COLLECT_TYPE_NONE,
        )
        self.individual6_1.household = self.household6
        self.individual6_1.save()
        self.collector5_1.household = self.household6
        self.collector5_1.save()
        self.role_primary6 = IndividualRoleInHouseholdFactory(
            individual=self.individual6_1,
            household=self.household6,
            role=ROLE_PRIMARY,
        )

        self.individual7_1 = IndividualFactory(
            business_area=self.business_area, household=None, registration_data_import=self.rdi_with_3_hhs
        )
        self.household7 = HouseholdFactory(
            business_area=self.business_area,
            head_of_household=self.individual7_1,
            registration_data_import=self.rdi_with_3_hhs,
            collect_individual_data=COLLECT_TYPE_NONE,
        )
        self.individual7_1.household = self.household7
        self.individual7_1.save()
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
        self.identity7_1 = IndividualIdentityFactory(individual=self.individual7_1)

        # Payments 5
        payment_plan5 = PaymentPlanFactory(
            target_population=self.target_population_paid,
            program=self.program_finished1,
        )
        self.payment5 = PaymentFactory(
            parent=payment_plan5,
            collector=self.collector5_1,
            household=self.household5,
            head_of_household=self.individual5_1,
            program=self.program_finished1,
            currency="PLN",
        )

        self.payment_record5 = PaymentRecordFactory(
            target_population=self.target_population_paid,
            household=self.household5,
            head_of_household=self.individual5_1,
            service_provider=ServiceProvider.objects.first() or ServiceProviderFactory(),
            parent=cash_plan,
        )
        # Payments 7
        payment_plan7 = PaymentPlanFactory(
            target_population=self.target_population3,
            program=self.program_finished2,
        )
        self.payment7 = PaymentFactory(
            parent=payment_plan7,
            collector=self.collector5_1,
            household=self.household7,
            head_of_household=self.individual7_1,
            program=self.program_finished2,
            currency="PLN",
        )

        self.payment_record7 = PaymentRecordFactory(
            target_population=self.target_population3,
            household=self.household7,
            head_of_household=self.individual7_1,
            service_provider=ServiceProvider.objects.first() or ServiceProviderFactory(),
            parent=cash_plan,
        )

        # Households from mixed rdi
        self.rdi_mixed = RegistrationDataImportFactory(business_area=self.business_area)

        (
            self.individual_mixed_closed_tp_paid,
            self.household_mixed_closed_tp_paid,
            _,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_mixed,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
            target_populations=[self.target_population_paid],
        )

        (
            self.individual_mixed_closed_tp_withdrawn_paid,
            self.household_mixed_closed_tp_withdrawn_paid,
            _,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_mixed,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
                "withdrawn": True,
            },
            target_populations=[self.target_population_paid],
        )

        (
            self.individual_mixed_closed_tp_withdrawn_not_paid,
            self.household_mixed_closed_tp_withdrawn_not_paid,
            _,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_mixed,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
                "withdrawn": True,
            },
            target_populations=[self.target_population_open_in_program_finished],
        )

        (
            self.individual_mixed_no_tp,
            self.household_mixed_no_tp,
            _,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_mixed,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
        )

        # Households from mixed rdi in active program
        self.rdi_mixed_active = RegistrationDataImportFactory(business_area=self.business_area)

        (
            self.individual_mixed_closed_tp_paid_active,
            self.household_mixed_closed_tp_paid_active,
            _,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_mixed_active,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
            target_populations=[self.target_population_paid],
        )

        (
            self.individual_mixed_closed_tp_withdrawn_paid_active,
            self.household_mixed_closed_tp_withdrawn_paid_active,
            _,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_mixed_active,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
                "withdrawn": True,
            },
            target_populations=[self.target_population_paid],
        )

        (
            self.individual_mixed_closed_tp_withdrawn_not_paid_active,
            self.household_mixed_closed_tp_withdrawn_not_paid_active,
            _,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_mixed_active,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
                "withdrawn": True,
            },
            target_populations=[self.target_population_open_in_program_finished],
        )

        (
            self.individual_mixed_no_tp_active,
            self.household_mixed_no_tp_active,
            _,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_mixed_active,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
        )

        (
            self.individual_mixed_active,
            self.household_mixed_active,
            _,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_mixed_active,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
            target_populations=[self.target_population1],
        )

        (
            self.individual_mixed_active_partial,
            self.household_mixed_active_partial,
            _,
        ) = self.create_hh_with_ind(
            {},
            {"collect_individual_data": COLLECT_TYPE_PARTIAL},
        )
        (
            self.individual_mixed_active_full,
            self.household_mixed_active_full,
            _,
        ) = self.create_hh_with_ind(
            {},
            {"collect_individual_data": COLLECT_TYPE_FULL},
        )
        (
            self.individual_mixed_active_full_withdrawn,
            self.household_mixed_active_full_withdrawn,
            _,
        ) = self.create_hh_with_ind(
            {},
            {"collect_individual_data": COLLECT_TYPE_FULL, "withdrawn": True},
        )
        (
            self.individual_mixed_active_size_only,
            self.household_mixed_active_size_only,
            _,
        ) = self.create_hh_with_ind(
            {},
            {"collect_individual_data": COLLECT_TYPE_SIZE_ONLY},
        )
        (
            self.individual_mixed_active_no_ind_data,
            self.household_mixed_active_no_ind_data,
            _,
        ) = self.create_hh_with_ind(
            {},
            {"collect_individual_data": COLLECT_TYPE_NONE},
        )

        (
            self.individual_full_closed,
            self.household_full_closed,
            _,
        ) = self.create_hh_with_ind(
            {},
            {
                "collect_individual_data": COLLECT_TYPE_FULL,
            },
            target_populations=[self.target_population_paid],
        )

    def refresh_objects(self) -> None:
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
        self.collector2_1.refresh_from_db()
        self.payment1.refresh_from_db()
        self.payment_record1.refresh_from_db()
        self.payment2.refresh_from_db()
        self.payment_record2.refresh_from_db()
        self.household5.refresh_from_db()
        self.individual5_1.refresh_from_db()
        self.household6.refresh_from_db()
        self.individual6_1.refresh_from_db()
        self.household7.refresh_from_db()
        self.individual7_1.refresh_from_db()
        self.collector5_1.refresh_from_db()
        self.collector5_2.refresh_from_db()
        self.payment5.refresh_from_db()
        self.payment_record5.refresh_from_db()
        self.payment7.refresh_from_db()
        self.payment_record7.refresh_from_db()
        self.rdi_with_3_hhs.refresh_from_db()
        self.individual_helper3.refresh_from_db()
        self.individual_mixed_closed_tp_paid.refresh_from_db()
        self.household_mixed_closed_tp_paid.refresh_from_db()
        self.individual_mixed_closed_tp_withdrawn_paid.refresh_from_db()
        self.household_mixed_closed_tp_withdrawn_paid.refresh_from_db()
        self.individual_mixed_closed_tp_withdrawn_not_paid.refresh_from_db()
        self.household_mixed_closed_tp_withdrawn_not_paid.refresh_from_db()
        self.individual_mixed_no_tp.refresh_from_db()
        self.household_mixed_no_tp.refresh_from_db()
        self.household_mixed_active.refresh_from_db()
        self.household_mixed_active_partial.refresh_from_db()
        self.household_mixed_active_full.refresh_from_db()
        self.household_mixed_active_size_only.refresh_from_db()
        self.household_mixed_active_no_ind_data.refresh_from_db()
        self.household_full_closed.refresh_from_db()
        self.rdi4_1.refresh_from_db()
        self.rdi_with_3_hhs.refresh_from_db()
        self.rdi_mixed.refresh_from_db()
        self.rdi_mixed_active.refresh_from_db()

    def assertNumQueries(  # type: ignore[override]
        self, num: int, func: None = None, *, using: str = DEFAULT_DB_ALIAS
    ) -> _AssertNumQueriesContext:
        conn = connections[using]

        context = _AssertNumQueriesContext(self, num, conn)
        if func is None:
            return context

    def test_migrate_data_to_representations_per_business_area_running_number_queries(self) -> None:
        self.refresh_objects()
        with self.assertNumQueries(
            377,
        ):
            migrate_data_to_representations_per_business_area(business_area=self.business_area)

    def test_copy_individual_number_of_queries(self) -> None:
        individual: Individual = Individual.objects.prefetch_related(
            "documents", "identities", "bank_account_info"
        ).get(id=self.individual1_1.id)
        program: Program = Program.objects.first()
        with self.assertNumQueries(
            4,
        ):
            copy_individual(individual, program)

    def test_copy_individual_fast_number_of_queries(self) -> None:
        individual: Individual = Individual.objects.prefetch_related(
            "documents", "identities", "bank_account_info"
        ).get(id=self.individual1_1.id)
        program: Program = Program.objects.first()
        with self.assertNumQueries(
            0,
        ):
            copy_individual_fast(individual, program)

    def test_copy_household_representation_for_programs_number_of_queries(self) -> None:
        household: Household = Household.objects.get(id=self.household1.id)
        individuals: List[Individual] = list(
            Individual.objects.filter(household=household).prefetch_related(
                "documents", "identities", "bank_account_info"
            )
        )
        program = Program.objects.first()
        with self.assertNumQueries(
            7,
        ):
            copy_household_representation_for_programs_fast(household, program, individuals)
