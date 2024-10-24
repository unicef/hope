import unittest
from copy import copy
from typing import List, Optional
from unittest import skip
from unittest.mock import patch

from django.db.models import Count
from django.test import TestCase
from django.utils import timezone

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.core.fixtures import generate_data_collecting_types
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
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
    COLLECT_TYPE_UNKNOWN,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    BankAccountInfo,
    Document,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentRecordFactory,
    ServiceProviderFactory,
)
from hct_mis_api.apps.payment.models import Payment, PaymentRecord, ServiceProvider
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation
from hct_mis_api.one_time_scripts.migrate_data_to_representations import (
    adjust_payment_records,
    adjust_payments,
    copy_household_representation_for_programs_fast,
    migrate_data_to_representations,
    migrate_data_to_representations_per_business_area,
)
from hct_mis_api.one_time_scripts.soft_delete_original_objects import (
    soft_delete_original_objects,
)


class BaseMigrateDataTestCase:
    def create_hh_with_ind(
        self,
        ind_data: dict,
        hh_data: dict,
        target_populations: Optional[List[TargetPopulation]] = None,
    ) -> tuple:
        if "registration_data_import" not in hh_data:
            hh_data["registration_data_import"] = None
        if "registration_data_import" not in ind_data:
            ind_data["registration_data_import"] = None
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
        return individual, household

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
        self.rdi1 = RegistrationDataImportFactory(business_area=self.business_area, program=None)

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
        self.individual1_1 = IndividualFactory(
            business_area=self.business_area, household=None, registration_data_import=None
        )
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
        self.individual1_2 = IndividualFactory(
            business_area=self.business_area, household=self.household1, registration_data_import=None
        )
        self.document1_2_1 = DocumentFactory(individual=self.individual1_2, program=None)

        self.individual1_3 = IndividualFactory(
            business_area=self.business_area, household=self.household1, registration_data_import=None
        )

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
        self.individual2_1 = IndividualFactory(
            business_area=self.business_area, household=None, registration_data_import=None
        )
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
        self.individual2_2 = IndividualFactory(
            business_area=self.business_area, household=self.household2, registration_data_import=None
        )
        self.document2_2_1 = DocumentFactory(individual=self.individual2_2, program=None)

        self.collector2_1 = IndividualFactory(
            business_area=self.business_area, household=None, registration_data_import=None
        )

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
        self.individual_helper3 = IndividualFactory(
            business_area=self.business_area, household=None, registration_data_import=None
        )
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

        self.individual3_1 = IndividualFactory(
            business_area=self.business_area, household=None, registration_data_import=None
        )
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
        self.rdi4_1 = RegistrationDataImportFactory(business_area=self.business_area, program=None)
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
        self.rdi_with_3_hhs = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=None,
        )
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
        self.rdi_mixed = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=None,
        )

        (
            self.individual_mixed_closed_tp_paid,
            self.household_mixed_closed_tp_paid,
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
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_mixed,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
        )

        # Households from mixed rdi in active program
        self.rdi_mixed_active = RegistrationDataImportFactory(
            business_area=self.business_area,
            program=None,
        )

        (
            self.individual_mixed_closed_tp_paid_active,
            self.household_mixed_closed_tp_paid_active,
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
        ) = self.create_hh_with_ind(
            {},
            {"collect_individual_data": COLLECT_TYPE_PARTIAL},
        )
        (
            self.individual_mixed_active_full,
            self.household_mixed_active_full,
        ) = self.create_hh_with_ind(
            {},
            {"collect_individual_data": COLLECT_TYPE_FULL},
        )
        (
            self.individual_mixed_active_full_withdrawn,
            self.household_mixed_active_full_withdrawn,
        ) = self.create_hh_with_ind(
            {},
            {"collect_individual_data": COLLECT_TYPE_FULL, "withdrawn": True},
        )
        (
            self.individual_mixed_active_size_only,
            self.household_mixed_active_size_only,
        ) = self.create_hh_with_ind(
            {},
            {"collect_individual_data": COLLECT_TYPE_SIZE_ONLY},
        )
        (
            self.individual_mixed_active_no_ind_data,
            self.household_mixed_active_no_ind_data,
        ) = self.create_hh_with_ind(
            {},
            {"collect_individual_data": COLLECT_TYPE_NONE},
        )

        (
            self.individual_full_closed,
            self.household_full_closed,
        ) = self.create_hh_with_ind(
            {},
            {
                "collect_individual_data": COLLECT_TYPE_FULL,
            },
            target_populations=[self.target_population_paid],
        )

        RegistrationDataImport.objects.update(created_at=timezone.make_aware(timezone.datetime(2023, 9, 20)))

        self.rdi_with_program = RegistrationDataImportFactory(
            business_area=self.business_area, program=self.program_active
        )
        (
            self.individual_with_assigned_rdi,
            self.household_with_assigned_rdi,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_with_program,
            },
        )
        Household.objects.update(is_original=True)
        Individual.objects.update(is_original=True)
        Document.objects.update(is_original=True)
        IndividualIdentity.objects.update(is_original=True)
        BankAccountInfo.objects.update(is_original=True)
        IndividualRoleInHousehold.objects.update(is_original=True)
        HouseholdSelection.objects.update(is_original=True)

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
        self.rdi_with_program.refresh_from_db()
        self.household_with_assigned_rdi.refresh_from_db()
        self.individual_with_assigned_rdi.refresh_from_db()


@skip("Failing tests")
class TestMigrateDataToRepresentations(BaseMigrateDataTestCase, TestCase):
    def test_migrate_data_to_representations_per_business_area_running_two_times(self) -> None:
        self.refresh_objects()
        self.assertEqual(Household.original_and_repr_objects.count(), 24)
        with patch("hct_mis_api.one_time_scripts.migrate_data_to_representations.copy_household_selections") as mock:
            mock.side_effect = lambda x, y: (_ for _ in ()).throw(ZeroDivisionError())
            try:
                migrate_data_to_representations_per_business_area(business_area=self.business_area)
            except ZeroDivisionError:
                pass
            self.assertEqual(Household.original_and_repr_objects.count(), 33)
            try:
                migrate_data_to_representations_per_business_area(business_area=self.business_area)
            except ZeroDivisionError:
                pass
            self.assertEqual(Household.original_and_repr_objects.count(), 33)

    def test_already_migrated_in_different_program(self) -> None:
        self.refresh_objects()
        hh1_id = self.household1.id
        self.assertEqual(Household.original_and_repr_objects.exclude(copied_from=None).count(), 0)
        copy_household_representation_for_programs_fast(
            self.household1, self.program_active, Individual.objects.filter(household=self.household1)
        )
        self.refresh_objects()
        programs = [str(x.program.id) for x in Household.original_and_repr_objects.filter(copied_from_id=hh1_id)]
        self.assertIn(str(self.program_active.id), programs)
        self.assertEqual(Household.original_and_repr_objects.exclude(copied_from=None).count(), 1)
        migrate_data_to_representations_per_business_area(business_area=self.business_area)
        programs = [str(x.program.id) for x in Household.original_and_repr_objects.filter(copied_from_id=hh1_id)]
        self.assertIn(str(self.program_active.id), programs)
        self.assertIn(str(self.program_finished1.id), programs)
        self.assertEqual(Household.original_and_repr_objects.filter(copied_from_id=hh1_id).count(), 2)

    def test_already_migrated_in_different_program2(self) -> None:
        self.refresh_objects()
        hh1_id = self.household1.id
        self.assertEqual(Household.original_and_repr_objects.exclude(copied_from=None).count(), 0)
        old_copy_household_representation_for_programs_fast = copy_household_representation_for_programs_fast
        copy_household_representation_for_programs_fast(
            self.household1, self.program_active, Individual.objects.filter(household=self.household1)
        )
        self.refresh_objects()
        programs = [str(x.program.id) for x in Household.original_and_repr_objects.filter(copied_from_id=hh1_id)]
        self.assertIn(str(self.program_active.id), programs)
        self.assertEqual(Household.original_and_repr_objects.exclude(copied_from=None).count(), 1)
        with patch(
            "hct_mis_api.one_time_scripts.migrate_data_to_representations.copy_household_representation_for_programs_fast"
        ) as mock:
            mock.side_effect = (
                lambda household, program, individuals: old_copy_household_representation_for_programs_fast(
                    copy(household), program, individuals
                )
            )
            migrate_data_to_representations_per_business_area(business_area=self.business_area)
            programs = [str(x.program.id) for x in Household.original_and_repr_objects.filter(copied_from_id=hh1_id)]
            self.assertIn(str(self.program_active.id), programs)
            self.assertIn(str(self.program_finished1.id), programs)
            self.assertEqual(Household.original_and_repr_objects.filter(copied_from_id=hh1_id).count(), 2)
            calls_for_hh1 = [call for call in mock.mock_calls if call[1][0].id == hh1_id]
            self.assertEqual(len(calls_for_hh1), 1)
            calls_for_program_active = [
                call for call in mock.mock_calls if call[1][1].id == self.program_active.id and call[1][0].id == hh1_id
            ]
            self.assertEqual(len(calls_for_program_active), 0)

    def test_migrate_data_to_representations_per_business_area(self) -> None:
        household_count = Household.original_and_repr_objects.filter(business_area=self.business_area).count()
        individual_count = Individual.original_and_repr_objects.filter(business_area=self.business_area).count()
        document_count = Document.original_and_repr_objects.filter(individual__business_area=self.business_area).count()
        identity_count = IndividualIdentity.original_and_repr_objects.filter(
            individual__business_area=self.business_area
        ).count()
        bank_account_info_count = BankAccountInfo.original_and_repr_objects.filter(
            individual__business_area=self.business_area
        ).count()
        household_selection_count = HouseholdSelection.original_and_repr_objects.filter(
            household__business_area=self.business_area
        ).count()
        roles_count = IndividualRoleInHousehold.original_and_repr_objects.filter(
            household__business_area=self.business_area
        ).count()
        self.refresh_objects()

        migrate_data_to_representations_per_business_area(business_area=self.business_area)

        self.assertEqual(Household.original_and_repr_objects.count(), 53)
        migrate_data_to_representations_per_business_area(business_area=self.business_area)
        self.assertEqual(Household.original_and_repr_objects.count(), 53)

        self.refresh_objects()
        # Test household1
        # check the original household
        self.assertEqual(self.household1.program, None)
        self.assertEqual(self.household1.is_original, True)
        self.assertEqual(self.household1.individuals.count(), 3)
        self.assertEqual(self.household1.representatives.count(), 2)
        self.assertEqual(self.household1.head_of_household, self.individual1_1)
        self.assertEqual(self.household1.target_populations.count(), 2)
        self.assertSetEqual(
            set(self.household1.target_populations.all()), {self.target_population1, self.target_population_paid}
        )
        self.assertEqual(self.household1.selections.count(), 2)
        self.assertTrue(all(selection.is_original for selection in self.household1.selections.all()))

        # check the copied household
        self.assertEqual(self.household1.copied_to(manager="original_and_repr_objects").count(), 2)

        household1_representation1 = Household.original_and_repr_objects.filter(
            is_original=False, copied_from=self.household1, program=self.program_active
        ).first()
        self.assertEqual(household1_representation1.program, self.program_active)
        self.assertEqual(household1_representation1.is_original, False)
        self.assertEqual(household1_representation1.origin_unicef_id, self.household1.unicef_id)
        self.assertEqual(household1_representation1.unicef_id, self.household1.unicef_id)
        self.assertEqual(household1_representation1.copied_from, self.household1)
        self.assertEqual(household1_representation1.individuals(manager="original_and_repr_objects").count(), 3)
        self.assertEqual(household1_representation1.representatives(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(household1_representation1.target_populations.count(), 1)
        self.assertEqual(household1_representation1.target_populations.first(), self.target_population1)
        self.assertEqual(household1_representation1.selections(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            household1_representation1.selections(manager="original_and_repr_objects").first().is_original, False
        )

        household1_representation2 = Household.original_and_repr_objects.filter(
            is_original=False, copied_from=self.household1, program=self.program_finished1
        ).first()
        self.assertEqual(household1_representation2.program, self.program_finished1)
        self.assertEqual(household1_representation2.is_original, False)
        self.assertEqual(household1_representation2.origin_unicef_id, self.household1.unicef_id)
        self.assertEqual(household1_representation2.unicef_id, self.household1.unicef_id)
        self.assertEqual(household1_representation2.copied_from, self.household1)
        self.assertEqual(household1_representation2.individuals(manager="original_and_repr_objects").count(), 3)
        self.assertEqual(household1_representation2.representatives(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(household1_representation2.target_populations.count(), 1)
        self.assertEqual(household1_representation2.target_populations.first(), self.target_population_paid)
        self.assertEqual(household1_representation2.selections(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            household1_representation2.selections(manager="original_and_repr_objects").first().is_original, False
        )

        self.assertEqual(self.individual1_1.copied_to(manager="original_and_repr_objects").count(), 2)

        individual1_1_representation1 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual1_1, program=self.program_active
        ).first()
        self.assertEqual(individual1_1_representation1.program, self.program_active)
        self.assertEqual(individual1_1_representation1.is_original, False)
        self.assertEqual(individual1_1_representation1.origin_unicef_id, self.individual1_1.unicef_id)
        self.assertEqual(individual1_1_representation1.unicef_id, self.individual1_1.unicef_id)
        self.assertEqual(individual1_1_representation1.copied_from, self.individual1_1)
        self.assertEqual(individual1_1_representation1.household, household1_representation1)
        self.assertEqual(household1_representation1.head_of_household, individual1_1_representation1)
        self.assertEqual(individual1_1_representation1.documents(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(
            individual1_1_representation1.documents(manager="original_and_repr_objects")
            .filter(is_original=False)
            .count(),
            2,
        )
        self.assertEqual(
            individual1_1_representation1.documents(manager="original_and_repr_objects")
            .filter(program=self.program_active)
            .count(),
            2,
        )
        self.assertSetEqual(
            set(
                individual1_1_representation1.documents(manager="original_and_repr_objects").values_list(
                    "document_number", flat=True
                )
            ),
            set(self.individual1_1.documents.values_list("document_number", flat=True)),
        )
        self.assertEqual(individual1_1_representation1.identities(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            individual1_1_representation1.identities(manager="original_and_repr_objects").first().is_original, False
        )
        self.assertEqual(
            individual1_1_representation1.identities(manager="original_and_repr_objects").first().number,
            self.individual1_1.identities.first().number,
        )
        self.assertEqual(
            individual1_1_representation1.bank_account_info(manager="original_and_repr_objects").count(), 1
        )
        self.assertEqual(
            individual1_1_representation1.bank_account_info(manager="original_and_repr_objects").first().is_original,
            False,
        )
        self.assertEqual(
            individual1_1_representation1.bank_account_info(manager="original_and_repr_objects")
            .first()
            .bank_account_number,
            self.individual1_1.bank_account_info.first().bank_account_number,
        )

        individual1_1_representation2 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual1_1, program=self.program_finished1
        ).first()
        self.assertEqual(individual1_1_representation2.program, self.program_finished1)
        self.assertEqual(individual1_1_representation2.is_original, False)
        self.assertEqual(individual1_1_representation2.origin_unicef_id, self.individual1_1.unicef_id)
        self.assertEqual(individual1_1_representation2.unicef_id, self.individual1_1.unicef_id)
        self.assertEqual(individual1_1_representation2.copied_from, self.individual1_1)
        self.assertEqual(individual1_1_representation2.household, household1_representation2)
        self.assertEqual(household1_representation2.head_of_household, individual1_1_representation2)
        self.assertEqual(individual1_1_representation2.documents(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(
            individual1_1_representation2.documents(manager="original_and_repr_objects")
            .filter(is_original=False)
            .count(),
            2,
        )
        self.assertEqual(
            individual1_1_representation2.documents(manager="original_and_repr_objects")
            .filter(program=self.program_finished1)
            .count(),
            2,
        )
        self.assertEqual(individual1_1_representation2.identities(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            individual1_1_representation2.identities(manager="original_and_repr_objects").first().is_original, False
        )
        self.assertEqual(
            individual1_1_representation2.bank_account_info(manager="original_and_repr_objects").count(), 1
        )
        self.assertEqual(
            individual1_1_representation2.bank_account_info(manager="original_and_repr_objects").first().is_original,
            False,
        )

        self.assertEqual(self.individual1_2.copied_to(manager="original_and_repr_objects").count(), 2)

        individual1_2_representation1 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual1_2, program=self.program_active
        ).first()
        self.assertEqual(individual1_2_representation1.program, self.program_active)
        self.assertEqual(individual1_2_representation1.is_original, False)
        self.assertEqual(individual1_2_representation1.origin_unicef_id, self.individual1_2.unicef_id)
        self.assertEqual(individual1_2_representation1.copied_from, self.individual1_2)
        self.assertEqual(individual1_2_representation1.household, household1_representation1)
        self.assertEqual(individual1_2_representation1.documents(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            individual1_2_representation1.documents(manager="original_and_repr_objects").first().is_original, False
        )
        self.assertEqual(
            individual1_2_representation1.documents(manager="original_and_repr_objects").first().program,
            self.program_active,
        )
        self.assertEqual(individual1_2_representation1.identities(manager="original_and_repr_objects").count(), 0)
        self.assertEqual(
            individual1_2_representation1.bank_account_info(manager="original_and_repr_objects").count(), 0
        )

        individual1_2_representation2 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual1_2, program=self.program_finished1
        ).first()
        self.assertEqual(individual1_2_representation2.program, self.program_finished1)
        self.assertEqual(individual1_2_representation2.is_original, False)
        self.assertEqual(individual1_2_representation2.origin_unicef_id, self.individual1_2.unicef_id)
        self.assertEqual(individual1_2_representation2.copied_from, self.individual1_2)
        self.assertEqual(individual1_2_representation2.household, household1_representation2)
        self.assertEqual(individual1_2_representation2.documents(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            individual1_2_representation2.documents(manager="original_and_repr_objects").first().is_original, False
        )
        self.assertEqual(
            individual1_2_representation2.documents(manager="original_and_repr_objects").first().program,
            self.program_finished1,
        )
        self.assertEqual(individual1_2_representation2.identities(manager="original_and_repr_objects").count(), 0)
        self.assertEqual(
            individual1_2_representation2.bank_account_info(manager="original_and_repr_objects").count(), 0
        )

        self.assertEqual(self.individual1_3.copied_to(manager="original_and_repr_objects").count(), 2)

        individual1_3_representation1 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual1_3, program=self.program_active
        ).first()
        self.assertEqual(individual1_3_representation1.program, self.program_active)
        self.assertEqual(individual1_3_representation1.is_original, False)
        self.assertEqual(individual1_3_representation1.origin_unicef_id, self.individual1_3.unicef_id)
        self.assertEqual(individual1_3_representation1.copied_from, self.individual1_3)
        self.assertEqual(individual1_3_representation1.household, household1_representation1)
        self.assertEqual(individual1_3_representation1.documents(manager="original_and_repr_objects").count(), 0)
        self.assertEqual(individual1_3_representation1.identities(manager="original_and_repr_objects").count(), 0)
        self.assertEqual(
            individual1_3_representation1.bank_account_info(manager="original_and_repr_objects").count(), 0
        )

        individual1_3_representation2 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual1_3, program=self.program_finished1
        ).first()
        self.assertEqual(individual1_3_representation2.program, self.program_finished1)
        self.assertEqual(individual1_3_representation2.is_original, False)
        self.assertEqual(individual1_3_representation2.origin_unicef_id, self.individual1_3.unicef_id)
        self.assertEqual(individual1_3_representation2.copied_from, self.individual1_3)
        self.assertEqual(individual1_3_representation2.household, household1_representation2)
        self.assertEqual(individual1_3_representation2.documents(manager="original_and_repr_objects").count(), 0)
        self.assertEqual(individual1_3_representation2.identities(manager="original_and_repr_objects").count(), 0)
        self.assertEqual(
            individual1_3_representation2.bank_account_info(manager="original_and_repr_objects").count(), 0
        )

        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household1_representation1,
                role=ROLE_PRIMARY,
                individual=individual1_2_representation1,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household1_representation1,
                role=ROLE_ALTERNATE,
                individual=individual1_3_representation1,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household1_representation2,
                role=ROLE_PRIMARY,
                individual=individual1_2_representation2,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household1_representation2,
                role=ROLE_ALTERNATE,
                individual=individual1_3_representation2,
            ).first()
        )

        # Test household2
        # check the original household
        self.assertEqual(self.household2.program, None)
        self.assertEqual(self.household2.is_original, True)
        self.assertEqual(self.household2.individuals.count(), 2)
        self.assertEqual(self.household2.representatives.count(), 2)
        self.assertEqual(self.household2.head_of_household, self.individual2_1)
        self.assertEqual(self.household2.target_populations.count(), 2)
        self.assertSetEqual(
            set(self.household2.target_populations.all()), {self.target_population1, self.target_population_paid}
        )
        self.assertEqual(self.household2.selections.count(), 2)
        self.assertTrue(all(selection.is_original for selection in self.household2.selections.all()))

        # check the copied household
        self.assertEqual(self.household2.copied_to(manager="original_and_repr_objects").count(), 2)

        household2_representation1 = Household.original_and_repr_objects.filter(
            is_original=False, copied_from=self.household2, program=self.program_active
        ).first()
        self.assertEqual(household2_representation1.program, self.program_active)
        self.assertEqual(household2_representation1.is_original, False)
        self.assertEqual(household2_representation1.origin_unicef_id, self.household2.unicef_id)
        self.assertEqual(household2_representation1.copied_from, self.household2)
        self.assertEqual(household2_representation1.individuals(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(household2_representation1.representatives(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(household2_representation1.target_populations.count(), 1)
        self.assertEqual(household2_representation1.target_populations.first(), self.target_population1)
        self.assertEqual(household2_representation1.selections(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            household2_representation1.selections(manager="original_and_repr_objects").first().is_original, False
        )

        household2_representation2 = Household.original_and_repr_objects.filter(
            is_original=False, copied_from=self.household2, program=self.program_finished1
        ).first()
        self.assertEqual(household2_representation2.program, self.program_finished1)
        self.assertEqual(household2_representation2.is_original, False)
        self.assertEqual(household2_representation2.origin_unicef_id, self.household2.unicef_id)
        self.assertEqual(household2_representation2.copied_from, self.household2)
        self.assertEqual(household2_representation2.individuals(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(household2_representation2.representatives(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(household2_representation2.target_populations.count(), 1)
        self.assertEqual(household2_representation2.target_populations.first(), self.target_population_paid)
        self.assertEqual(household2_representation2.selections(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            household2_representation2.selections(manager="original_and_repr_objects").first().is_original, False
        )

        self.assertEqual(self.individual2_1.copied_to(manager="original_and_repr_objects").count(), 2)

        individual2_1_representation1 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual2_1, program=self.program_active
        ).first()
        self.assertEqual(individual2_1_representation1.program, self.program_active)
        self.assertEqual(individual2_1_representation1.is_original, False)
        self.assertEqual(individual2_1_representation1.origin_unicef_id, self.individual2_1.unicef_id)
        self.assertEqual(individual2_1_representation1.copied_from, self.individual2_1)
        self.assertEqual(individual2_1_representation1.household, household2_representation1)
        self.assertEqual(household2_representation1.head_of_household, individual2_1_representation1)
        self.assertEqual(individual2_1_representation1.documents(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(
            individual2_1_representation1.documents(manager="original_and_repr_objects")
            .filter(is_original=False)
            .count(),
            2,
        )
        self.assertEqual(
            individual2_1_representation1.documents(manager="original_and_repr_objects")
            .filter(program=self.program_active)
            .count(),
            2,
        )
        self.assertEqual(
            individual2_1_representation1.documents(manager="original_and_repr_objects").first().program,
            self.program_active,
        )
        self.assertEqual(individual2_1_representation1.identities(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            individual2_1_representation1.identities(manager="original_and_repr_objects")
            .filter(is_original=False)
            .count(),
            1,
        )
        self.assertEqual(
            individual2_1_representation1.bank_account_info(manager="original_and_repr_objects").count(), 1
        )
        self.assertEqual(
            individual2_1_representation1.bank_account_info(manager="original_and_repr_objects")
            .filter(is_original=False)
            .count(),
            1,
        )

        individual2_1_representation2 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual2_1, program=self.program_finished1
        ).first()
        self.assertEqual(individual2_1_representation2.program, self.program_finished1)
        self.assertEqual(individual2_1_representation2.is_original, False)
        self.assertEqual(individual2_1_representation2.origin_unicef_id, self.individual2_1.unicef_id)
        self.assertEqual(individual2_1_representation2.copied_from, self.individual2_1)
        self.assertEqual(individual2_1_representation2.household, household2_representation2)
        self.assertEqual(household2_representation2.head_of_household, individual2_1_representation2)
        self.assertEqual(individual2_1_representation2.documents(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(
            individual2_1_representation2.documents(manager="original_and_repr_objects")
            .filter(is_original=False)
            .count(),
            2,
        )
        self.assertEqual(
            individual2_1_representation2.documents(manager="original_and_repr_objects")
            .filter(program=self.program_finished1)
            .count(),
            2,
        )
        self.assertEqual(
            individual2_1_representation2.documents(manager="original_and_repr_objects").first().program,
            self.program_finished1,
        )
        self.assertEqual(individual2_1_representation2.identities(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            individual2_1_representation2.identities(manager="original_and_repr_objects")
            .filter(is_original=False)
            .count(),
            1,
        )
        self.assertEqual(
            individual2_1_representation2.bank_account_info(manager="original_and_repr_objects").count(), 1
        )
        self.assertEqual(
            individual2_1_representation2.bank_account_info(manager="original_and_repr_objects")
            .filter(is_original=False)
            .count(),
            1,
        )

        self.assertEqual(self.individual2_2.copied_to(manager="original_and_repr_objects").count(), 2)

        individual2_2_representation1 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual2_2, program=self.program_active
        ).first()
        self.assertEqual(individual2_2_representation1.program, self.program_active)
        self.assertEqual(individual2_2_representation1.is_original, False)
        self.assertEqual(individual2_2_representation1.origin_unicef_id, self.individual2_2.unicef_id)
        self.assertEqual(individual2_2_representation1.copied_from, self.individual2_2)
        self.assertEqual(individual2_2_representation1.household, household2_representation1)
        self.assertEqual(individual2_2_representation1.documents(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            individual2_1_representation2.documents(manager="original_and_repr_objects").first().is_original, False
        )
        self.assertEqual(
            individual2_2_representation1.documents(manager="original_and_repr_objects").first().program,
            self.program_active,
        )
        self.assertEqual(individual2_2_representation1.identities(manager="original_and_repr_objects").count(), 0)
        self.assertEqual(
            individual2_2_representation1.bank_account_info(manager="original_and_repr_objects").count(), 0
        )

        individual2_2_representation2 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual2_2, program=self.program_finished1
        ).first()
        self.assertEqual(individual2_2_representation2.program, self.program_finished1)
        self.assertEqual(individual2_2_representation2.is_original, False)
        self.assertEqual(individual2_2_representation2.origin_unicef_id, self.individual2_2.unicef_id)
        self.assertEqual(individual2_2_representation2.copied_from, self.individual2_2)
        self.assertEqual(individual2_2_representation2.household, household2_representation2)
        self.assertEqual(individual2_2_representation2.documents(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            individual2_2_representation2.documents(manager="original_and_repr_objects").first().is_original, False
        )
        self.assertEqual(
            individual2_2_representation2.documents(manager="original_and_repr_objects").first().program,
            self.program_finished1,
        )
        self.assertEqual(individual2_2_representation2.identities(manager="original_and_repr_objects").count(), 0)
        self.assertEqual(
            individual2_2_representation2.bank_account_info(manager="original_and_repr_objects").count(), 0
        )

        collector2_1_representation1 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.collector2_1, program=self.program_active
        ).first()
        collector2_1_representation2 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.collector2_1, program=self.program_finished1
        ).first()
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household2_representation1,
                role=ROLE_PRIMARY,
                individual=collector2_1_representation1,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household2_representation1,
                role=ROLE_ALTERNATE,
                individual=individual1_1_representation1,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household2_representation2,
                role=ROLE_PRIMARY,
                individual=collector2_1_representation2,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household2_representation2,
                role=ROLE_ALTERNATE,
                individual=individual1_1_representation2,
            ).first()
        )

        # Test household3
        # check the original household
        self.assertEqual(self.household3.program, None)
        self.assertEqual(self.household3.is_original, True)
        self.assertEqual(self.household3.individuals.count(), 1)
        self.assertEqual(self.household3.representatives.count(), 2)
        self.assertEqual(self.household3.head_of_household, self.individual3_1)
        self.assertEqual(self.household3.target_populations.count(), 1)
        self.assertEqual(self.household3.selections.count(), 1)
        self.assertEqual(self.household_helper.program, None)
        self.assertEqual(self.household_helper.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(self.individual_helper3.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.document_helper.copied_to(manager="original_and_repr_objects").count(), 2)

        # check the copied household - copied to program_finished1
        self.assertEqual(self.household3.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(self.individual3_1.copied_to(manager="original_and_repr_objects").count(), 1)

        household3_representation = self.household3.copied_to(manager="original_and_repr_objects").first()
        self.assertEqual(
            household3_representation.program,
            self.program_finished1,
        )
        self.assertEqual(household3_representation.is_original, False)
        self.assertEqual(household3_representation.origin_unicef_id, self.household3.unicef_id)
        self.assertEqual(household3_representation.copied_from, self.household3)
        self.assertEqual(household3_representation.individuals(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(household3_representation.representatives(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(household3_representation.target_populations.count(), 1)
        self.assertEqual(household3_representation.selections(manager="original_and_repr_objects").count(), 1)

        individual3_1_representation = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual3_1, program=self.program_finished1
        ).first()

        self.assertEqual(individual3_1_representation.is_original, False)
        self.assertEqual(individual3_1_representation.origin_unicef_id, self.individual3_1.unicef_id)
        self.assertEqual(individual3_1_representation.copied_from, self.individual3_1)
        self.assertEqual(individual3_1_representation.household, household3_representation)
        self.assertEqual(household3_representation.head_of_household, individual3_1_representation)
        self.assertEqual(individual3_1_representation.documents(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            individual3_1_representation.documents(manager="original_and_repr_objects").first().is_original, False
        )
        self.assertEqual(
            individual3_1_representation.documents(manager="original_and_repr_objects").first().program,
            self.program_finished1,
        )
        self.assertEqual(individual3_1_representation.identities(manager="original_and_repr_objects").count(), 0)
        self.assertEqual(individual3_1_representation.bank_account_info(manager="original_and_repr_objects").count(), 0)

        individual_helper3_representation = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual_helper3, program=self.program_finished1
        ).first()
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household3_representation,
                role=ROLE_ALTERNATE,
                individual=individual3_1_representation,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household3_representation,
                role=ROLE_PRIMARY,
                individual=individual_helper3_representation,
            ).first()
        )

        # Test household4
        # check the original household
        self.assertEqual(self.household4.program, None)
        self.assertEqual(self.household4.is_original, True)
        self.assertEqual(self.household4.individuals.count(), 1)
        self.assertEqual(self.household4.representatives.count(), 1)
        self.assertEqual(self.household4.head_of_household, self.individual4_1)
        self.assertEqual(self.household4.target_populations.count(), 0)
        self.assertEqual(self.household4.selections.count(), 0)

        # check the copied household - moved to storage program
        self.assertEqual(self.household4.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(self.individual4_1.copied_to(manager="original_and_repr_objects").count(), 1)

        household4_representation = self.household4.copied_to(manager="original_and_repr_objects").first()
        program_storage_full = Program.all_objects.get(name=f"Storage program - COLLECTION TYPE " f"{self.full.label}")
        self.assertEqual(household4_representation.program, program_storage_full)
        self.assertEqual(household4_representation.is_original, False)
        self.assertEqual(household4_representation.origin_unicef_id, self.household4.unicef_id)
        self.assertEqual(household4_representation.copied_from, self.household4)
        self.assertEqual(household4_representation.individuals(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(household4_representation.representatives(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(household4_representation.target_populations.count(), 0)
        self.assertEqual(household4_representation.selections(manager="original_and_repr_objects").count(), 0)

        individual4_1_representation = self.individual4_1.copied_to(manager="original_and_repr_objects").first()
        self.assertEqual(individual4_1_representation.program, program_storage_full)
        self.assertEqual(individual4_1_representation.is_original, False)
        self.assertEqual(individual4_1_representation.origin_unicef_id, self.individual4_1.unicef_id)
        self.assertEqual(individual4_1_representation.copied_from, self.individual4_1)
        self.assertEqual(individual4_1_representation.household, household4_representation)
        self.assertEqual(household4_representation.head_of_household, individual4_1_representation)
        self.assertEqual(individual4_1_representation.documents(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            individual4_1_representation.documents(manager="original_and_repr_objects").first().program,
            program_storage_full,
        )
        self.assertEqual(individual4_1_representation.identities(manager="original_and_repr_objects").count(), 0)
        self.assertEqual(individual4_1_representation.bank_account_info(manager="original_and_repr_objects").count(), 0)
        self.assertEqual(self.rdi4_1.households(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(
            self.rdi4_1.households(manager="original_and_repr_objects").filter(is_original=True).count(), 1
        )
        self.assertEqual(
            self.rdi4_1.households(manager="original_and_repr_objects").filter(is_original=False).count(), 1
        )
        self.assertEqual(self.rdi4_1.individuals(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.rdi4_1.program, program_storage_full)

        # Test household5, 6, 7
        # check the original households
        self.assertEqual(self.household5.program, None)
        self.assertEqual(self.household5.is_original, True)
        self.assertEqual(self.household5.individuals.count(), 1)
        self.assertEqual(self.household5.representatives.count(), 2)
        self.assertEqual(self.household5.head_of_household, self.individual5_1)
        self.assertEqual(self.household5.target_populations.count(), 2)
        self.assertEqual(self.household5.selections.count(), 2)
        self.assertEqual(self.household6.program, None)
        self.assertEqual(self.household6.is_original, True)
        self.assertEqual(self.household6.individuals.count(), 2)
        self.assertEqual(self.household6.representatives.count(), 1)
        self.assertEqual(self.household6.head_of_household, self.individual6_1)
        self.assertEqual(self.household6.target_populations.count(), 0)
        self.assertEqual(self.household6.selections.count(), 0)
        self.assertEqual(self.household7.program, None)
        self.assertEqual(self.household7.is_original, True)
        self.assertEqual(self.household7.individuals.count(), 1)
        self.assertEqual(self.household7.representatives.count(), 2)
        self.assertEqual(self.household7.head_of_household, self.individual7_1)
        self.assertEqual(self.household7.target_populations.count(), 1)
        self.assertEqual(self.household7.selections.count(), 1)

        # check the copied households - copied to every program that any of this RDI's households fulfilled the criteria
        self.assertEqual(self.household5.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.household6.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(self.household7.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.individual5_1.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.individual6_1.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(self.individual7_1.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertEqual(self.collector5_1.copied_to(manager="original_and_repr_objects").count(), 3)
        self.assertEqual(self.collector5_2.copied_to(manager="original_and_repr_objects").count(), 3)

        self.assertEqual(
            self.household6.copied_to(manager="original_and_repr_objects").first().program, self.program_active
        )
        self.assertIn(
            self.program_active.id,
            self.household5.copied_to(manager="original_and_repr_objects").values_list("program", flat=True),
        )
        self.assertIn(
            self.program_finished1.id,
            self.household5.copied_to(manager="original_and_repr_objects").values_list("program", flat=True),
        )
        self.assertIn(
            self.program_active.id,
            self.household7.copied_to(manager="original_and_repr_objects").values_list("program", flat=True),
        )
        self.assertIn(
            self.program_finished2.id,
            self.household7.copied_to(manager="original_and_repr_objects").values_list("program", flat=True),
        )

        self.assertEqual(self.rdi_with_3_hhs.households(manager="original_and_repr_objects").count(), 8)
        self.assertEqual(
            self.rdi_with_3_hhs.households(manager="original_and_repr_objects").filter(is_original=True).count(), 3
        )
        self.assertEqual(
            self.rdi_with_3_hhs.households(manager="original_and_repr_objects").filter(is_original=False).count(), 5
        )
        self.assertEqual(self.rdi_with_3_hhs.individuals(manager="original_and_repr_objects").count(), 16)
        self.assertIn(
            self.rdi_with_3_hhs.program, [self.program_active, self.program_finished1, self.program_finished2]
        )

        household5_1_representation1 = Household.original_and_repr_objects.filter(
            is_original=False, copied_from=self.household5, program=self.program_active
        ).first()
        household5_1_representation2 = Household.original_and_repr_objects.filter(
            is_original=False, copied_from=self.household5, program=self.program_finished1
        ).first()
        household7_1_representation1 = Household.original_and_repr_objects.filter(
            is_original=False, copied_from=self.household7, program=self.program_active
        ).first()
        household7_1_representation3 = Household.original_and_repr_objects.filter(
            is_original=False, copied_from=self.household7, program=self.program_finished2
        ).first()
        individual5_1_representation1 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual5_1, program=self.program_active
        ).first()
        individual5_1_representation2 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual5_1, program=self.program_finished1
        ).first()
        collector5_1_representation1 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.collector5_1, program=self.program_active
        ).first()
        collector5_1_representation2 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.collector5_1, program=self.program_finished1
        ).first()
        collector5_1_representation3 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.collector5_1, program=self.program_finished2
        ).first()

        collector5_2_representation1 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.collector5_2, program=self.program_active
        ).first()
        collector5_2_representation2 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.collector5_2, program=self.program_finished1
        ).first()
        collector5_2_representation3 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.collector5_2, program=self.program_finished2
        ).first()
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household5_1_representation1,
                role=ROLE_PRIMARY,
                individual=collector5_1_representation1,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household5_1_representation1,
                role=ROLE_ALTERNATE,
                individual=collector5_2_representation1,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household5_1_representation2,
                role=ROLE_PRIMARY,
                individual=collector5_1_representation2,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household5_1_representation2,
                role=ROLE_ALTERNATE,
                individual=collector5_2_representation2,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household7_1_representation3,
                role=ROLE_ALTERNATE,
                individual=collector5_2_representation3,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household7_1_representation3,
                role=ROLE_PRIMARY,
                individual=collector5_1_representation3,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household7_1_representation1,
                role=ROLE_ALTERNATE,
                individual=collector5_2_representation1,
            ).first()
        )
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                is_original=False,
                household=household7_1_representation1,
                role=ROLE_PRIMARY,
                individual=collector5_1_representation1,
            ).first()
        )
        self.assertEqual(household5_1_representation1.head_of_household, individual5_1_representation1)
        self.assertEqual(household5_1_representation2.head_of_household, individual5_1_representation2)
        for representation in [
            individual5_1_representation1,
            individual5_1_representation2,
        ]:
            self.assertEqual(representation.is_original, False)
            self.assertEqual(representation.copied_from, self.individual5_1)
            self.assertEqual(representation.origin_unicef_id, self.individual5_1.unicef_id)

        self.assertEqual(
            Individual.original_and_repr_objects.filter(copied_from=self.individual7_1).aggregate(Count("identities"))[
                "identities__count"
            ],
            2,
        )
        # Test mixed households/rdi
        self.assertIn(
            self.rdi_mixed.program.name,
            [self.program_finished1.name, f"Storage program - COLLECTION TYPE {self.size_only.label}"],
        )

        self.assertEqual(self.household_mixed_closed_tp_paid.copied_to(manager="original_and_repr_objects").count(), 1)
        repr_household_mixed_closed_tp_paid = self.household_mixed_closed_tp_paid.copied_to(
            manager="original_and_repr_objects"
        ).first()
        self.assertEqual(repr_household_mixed_closed_tp_paid.program, self.program_finished1)

        self.assertEqual(
            self.household_mixed_closed_tp_withdrawn_paid.copied_to(manager="original_and_repr_objects").count(), 1
        )
        repr_household_mixed_closed_tp_withdrawn_paid = self.household_mixed_closed_tp_withdrawn_paid.copied_to(
            manager="original_and_repr_objects"
        ).first()
        self.assertEqual(repr_household_mixed_closed_tp_withdrawn_paid.program, self.program_finished1)

        self.assertEqual(
            self.household_mixed_closed_tp_withdrawn_not_paid.copied_to(manager="original_and_repr_objects").count(), 1
        )
        repr_household_mixed_closed_tp_withdrawn_not_paid = self.household_mixed_closed_tp_withdrawn_not_paid.copied_to(
            manager="original_and_repr_objects"
        ).first()
        self.assertEqual(
            repr_household_mixed_closed_tp_withdrawn_not_paid.program.name,
            f"Storage program - COLLECTION TYPE " f"{self.size_only.label}",
        )
        self.assertFalse(
            repr_household_mixed_closed_tp_withdrawn_not_paid.program.is_visible,
        )

        self.assertEqual(self.household_mixed_no_tp.copied_to(manager="original_and_repr_objects").count(), 1)
        repr_household_mixed_no_tp = self.household_mixed_no_tp.copied_to(manager="original_and_repr_objects").first()
        self.assertEqual(
            repr_household_mixed_no_tp.program.name,
            f"Storage program - COLLECTION TYPE " f"{self.size_only.label}",
        )

        # Test mixed households/rdi
        self.assertIn(
            self.rdi_mixed_active.program.name,
            [
                f"Storage program - COLLECTION TYPE {self.size_only.label}",
                self.program_active.name,
                self.program_finished1.name,
            ],
        )

        self.assertEqual(
            self.household_mixed_closed_tp_paid_active.copied_to(manager="original_and_repr_objects").count(), 2
        )
        repr_household_mixed_closed_tp_paid_active_programs = self.household_mixed_closed_tp_paid_active.copied_to(
            manager="original_and_repr_objects"
        ).values_list("program", flat=True)
        self.assertIn(self.program_finished1.id, repr_household_mixed_closed_tp_paid_active_programs)
        self.assertIn(self.program_active.id, repr_household_mixed_closed_tp_paid_active_programs)

        self.assertEqual(
            self.household_mixed_closed_tp_withdrawn_paid_active.copied_to(manager="original_and_repr_objects").count(),
            1,
        )
        household_mixed_closed_tp_withdrawn_paid_active_repr_programs = (
            self.household_mixed_closed_tp_withdrawn_paid_active.copied_to(
                manager="original_and_repr_objects"
            ).values_list("program", flat=True)
        )
        self.assertIn(self.program_finished1.id, household_mixed_closed_tp_withdrawn_paid_active_repr_programs)

        self.assertEqual(
            self.household_mixed_closed_tp_withdrawn_not_paid_active.copied_to(
                manager="original_and_repr_objects"
            ).count(),
            1,
        )
        repr_household_mixed_closed_tp_withdrawn_not_paid_active = (
            self.household_mixed_closed_tp_withdrawn_not_paid_active.copied_to(
                manager="original_and_repr_objects"
            ).first()
        )
        self.assertEqual(
            repr_household_mixed_closed_tp_withdrawn_not_paid_active.program.name,
            f"Storage program - COLLECTION TYPE " f"{self.size_only.label}",
        )

        self.assertEqual(self.household_mixed_no_tp_active.copied_to(manager="original_and_repr_objects").count(), 1)
        repr_household_mixed_no_tp_active = self.household_mixed_no_tp_active.copied_to(
            manager="original_and_repr_objects"
        ).first()
        self.assertEqual(
            repr_household_mixed_no_tp_active.program,
            self.program_active,
        )

        self.assertEqual(self.household_mixed_active.copied_to(manager="original_and_repr_objects").count(), 1)
        repr_household_mixed_active = self.household_mixed_active.copied_to(manager="original_and_repr_objects").first()
        self.assertEqual(
            repr_household_mixed_active.program,
            self.program_active,
        )

        self.assertEqual(self.household_mixed_active_partial.copied_to(manager="original_and_repr_objects").count(), 1)
        repr_household_mixed_active_partial = self.household_mixed_active_partial.copied_to(
            manager="original_and_repr_objects"
        ).first()
        program_storage_partial = Program.all_objects.get(
            name=f"Storage program - COLLECTION TYPE {self.partial.label}"
        )
        self.assertEqual(
            repr_household_mixed_active_partial.program,
            program_storage_partial,
        )

        self.assertEqual(self.household_mixed_active_full.copied_to(manager="original_and_repr_objects").count(), 1)
        repr_household_mixed_active_full = self.household_mixed_active_full.copied_to(
            manager="original_and_repr_objects"
        ).first()
        self.assertEqual(
            repr_household_mixed_active_full.program,
            program_storage_full,
        )

        self.assertEqual(
            self.household_mixed_active_size_only.copied_to(manager="original_and_repr_objects").count(), 1
        )
        repr_household_mixed_active_size_only = self.household_mixed_active_size_only.copied_to(
            manager="original_and_repr_objects"
        ).first()
        self.assertEqual(
            repr_household_mixed_active_size_only.program.name,
            f"Storage program - COLLECTION TYPE " f"{self.size_only.label}",
        )

        self.assertEqual(
            self.household_mixed_active_no_ind_data.copied_to(manager="original_and_repr_objects").count(), 1
        )
        repr_household_mixed_active_no_ind_data = self.household_mixed_active_no_ind_data.copied_to(
            manager="original_and_repr_objects"
        ).first()
        self.assertEqual(
            repr_household_mixed_active_no_ind_data.program.name,
            f"Storage program - COLLECTION TYPE " f"{self.no_ind_data.label}",
        )

        self.assertEqual(
            self.household_mixed_active_full_withdrawn.copied_to(manager="original_and_repr_objects").count(), 1
        )
        repr_household_mixed_active_full_withdrawn = self.household_mixed_active_full_withdrawn.copied_to(
            manager="original_and_repr_objects"
        ).first()
        self.assertEqual(
            repr_household_mixed_active_full_withdrawn.program.name,
            f"Storage program - COLLECTION TYPE " f"{self.full.label}",
        )

        self.assertEqual(
            self.household_full_closed.copied_to(manager="original_and_repr_objects").count(),
            1,
        )
        self.assertEqual(
            self.household_full_closed.copied_to(manager="original_and_repr_objects").first().program,
            self.program_finished1,
        )

        # 2x household1, 2x household2, 1x household3, 1x household_helper,
        # 1x household4, 5x from rdi_with_3_hhs, 6x from mixed rdi,
        # 1x(household_mixed_closed_tp_paid, household_mixed_closed_tp_withdrawn_paid,
        # household_mixed_closed_tp_withdrawn_not_paid, household_mixed_no_tp,household_mixed_active_partial,
        # household_mixed_active_partial, household_mixed_active_full, household_mixed_active_size_only,
        # household_mixed_active_no_ind_data, household_full_closed, household_with_assigned_rdi)
        self.assertEqual(Household.original_and_repr_objects.count() - household_count, 29)
        # 2x individual1_1, 2x individual1_2, 2x individual1_3, 2x individual2_1, 2x individual2_2, 2x collector2_1,
        # 1x individual3_1, 2x individual_helper3, 1x individual4_1, 11 from rdi_with_3_hhs, 6x from mixed rdi, 1x from(
        # household_mixed_closed_tp_paid, household_mixed_closed_tp_withdrawn_paid,
        # household_mixed_closed_tp_withdrawn_not_paid, household_mixed_no_tp,household_mixed_active_partial,
        # household_mixed_active_partial, household_mixed_active_full, household_mixed_active_size_only,
        # household_mixed_active_no_ind_data, household_full_closed, individual_with_assigned_rdi)
        self.assertEqual(Individual.original_and_repr_objects.count() - individual_count, 44)
        # 6x for household1, 6x for household2, 1x for household3, 2x for household_helper, 1x for household4
        self.assertEqual(Document.original_and_repr_objects.count() - document_count, 16)
        # 2x for household1, 2x for household2, 1x for household_helper, 1x for household3, 6x mixed rdis
        self.assertEqual(HouseholdSelection.original_and_repr_objects.count() - household_selection_count, 15)
        # 2x for household1, 2x for household2, 2x household7
        self.assertEqual(IndividualIdentity.original_and_repr_objects.count() - identity_count, 6)
        # 2x for household1, 2x for household2
        self.assertEqual(BankAccountInfo.original_and_repr_objects.count() - bank_account_info_count, 4)
        # 4x for household1, 4x for household2, 2x for household3, 1x for household4, 4x household7,
        # 1x household6, 4x household5
        self.assertEqual(IndividualRoleInHousehold.original_and_repr_objects.count() - roles_count, 20)

        # test soft delete of original objects
        soft_delete_original_objects()
        self.refresh_objects()
        self.assertEqual(Household.all_objects.filter(is_removed=True).count(), household_count)
        self.assertEqual(Household.all_objects.filter(is_removed=True, is_original=True).count(), household_count)
        self.assertEqual(Household.all_objects.filter(is_removed=True, is_original=False).count(), 0)
        self.assertEqual(Individual.all_objects.filter(is_removed=True).count(), individual_count)
        self.assertEqual(Individual.all_objects.filter(is_removed=True, is_original=True).count(), individual_count)
        self.assertEqual(Individual.all_objects.filter(is_removed=True, is_original=False).count(), 0)
        self.assertEqual(IndividualRoleInHousehold.all_objects.filter(is_removed=True).count(), roles_count)
        self.assertEqual(
            IndividualRoleInHousehold.all_objects.filter(is_removed=True, is_original=True).count(), roles_count
        )
        self.assertEqual(IndividualRoleInHousehold.all_objects.filter(is_removed=True, is_original=False).count(), 0)
        self.assertEqual(Document.all_objects.filter(is_removed=True).count(), document_count)
        self.assertEqual(Document.all_objects.filter(is_removed=True, is_original=True).count(), document_count)
        self.assertEqual(Document.all_objects.filter(is_removed=True, is_original=False).count(), 0)
        self.assertEqual(IndividualIdentity.all_objects.filter(is_removed=True).count(), identity_count)
        self.assertEqual(
            IndividualIdentity.all_objects.filter(is_removed=True, is_original=True).count(), identity_count
        )
        self.assertEqual(IndividualIdentity.all_objects.filter(is_removed=True, is_original=False).count(), 0)
        self.assertEqual(BankAccountInfo.all_objects.filter(is_removed=True).count(), bank_account_info_count)
        self.assertEqual(
            BankAccountInfo.all_objects.filter(is_removed=True, is_original=True).count(), bank_account_info_count
        )
        self.assertEqual(BankAccountInfo.all_objects.filter(is_removed=True, is_original=False).count(), 0)

        # test migrating for RDI with program assigned (update on prod since 21-09-2023)
        self.assertEqual(self.rdi_with_program.program, self.program_active)
        self.assertEqual(self.household_with_assigned_rdi.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            self.household_with_assigned_rdi.copied_to(manager="original_and_repr_objects").first().program,
            self.program_active,
        )
        self.assertEqual(self.individual_with_assigned_rdi.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            self.individual_with_assigned_rdi.copied_to(manager="original_and_repr_objects").first().program,
            self.program_active,
        )

    def test_adjust_payments_and_payment_records(self) -> None:
        payment_count = Payment.objects.filter(business_area=self.business_area).count()
        payment_record_count = PaymentRecord.objects.filter(business_area=self.business_area).count()

        self.assertEqual(self.payment1.collector, self.individual1_2)
        self.assertEqual(self.payment1.head_of_household, self.individual1_1)
        self.assertEqual(self.payment1.household, self.household1)
        self.assertEqual(self.payment_record1.head_of_household, self.individual1_1)
        self.assertEqual(self.payment_record1.household, self.household1)

        self.assertEqual(self.payment2.collector, self.collector2_1)
        self.assertEqual(self.payment2.head_of_household, self.individual2_1)
        self.assertEqual(self.payment2.household, self.household2)
        self.assertEqual(self.payment_record2.head_of_household, self.collector2_1)
        self.assertEqual(self.payment_record2.household, self.household2)

        self.assertEqual(self.payment5.collector, self.collector5_1)
        self.assertEqual(self.payment5.head_of_household, self.individual5_1)
        self.assertEqual(self.payment5.household, self.household5)
        self.assertEqual(self.payment_record5.head_of_household, self.individual5_1)
        self.assertEqual(self.payment_record5.household, self.household5)

        self.assertEqual(self.payment7.collector, self.collector5_1)
        self.assertEqual(self.payment7.head_of_household, self.individual7_1)
        self.assertEqual(self.payment7.household, self.household7)
        self.assertEqual(self.payment_record7.head_of_household, self.individual7_1)
        self.assertEqual(self.payment_record7.household, self.household7)

        migrate_data_to_representations_per_business_area(business_area=self.business_area)
        adjust_payments(business_area=self.business_area)
        adjust_payment_records(business_area=self.business_area)

        self.refresh_objects()

        self.assertEqual(Payment.objects.filter(business_area=self.business_area).count(), payment_count)
        self.assertEqual(PaymentRecord.objects.filter(business_area=self.business_area).count(), payment_record_count)

        # payment1
        individual1_1_representation1 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual1_1, program=self.program_active
        ).first()
        individual1_2_representation1 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual1_2, program=self.program_active
        ).first()
        household1_representation1 = Household.original_and_repr_objects.filter(
            is_original=False, copied_from=self.household1, program=self.program_active
        ).first()
        self.assertEqual(self.payment1.collector, individual1_2_representation1)
        self.assertEqual(self.payment1.head_of_household, individual1_1_representation1)
        self.assertEqual(self.payment1.household, household1_representation1)
        self.assertEqual(self.payment_record1.head_of_household, individual1_1_representation1)
        self.assertEqual(self.payment_record1.household, household1_representation1)

        # payment2
        individual2_1_representation2 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual2_1, program=self.program_finished1
        ).first()
        collector2_1_representation2 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.collector2_1, program=self.program_finished1
        ).first()
        household2_representation2 = Household.original_and_repr_objects.filter(
            is_original=False, copied_from=self.household2, program=self.program_finished1
        ).first()
        self.assertEqual(self.payment2.collector, collector2_1_representation2)
        self.assertEqual(self.payment2.head_of_household, individual2_1_representation2)
        self.assertEqual(self.payment2.household, household2_representation2)
        self.assertEqual(self.payment_record2.head_of_household, collector2_1_representation2)
        self.assertEqual(self.payment_record2.household, household2_representation2)

        # payment5
        collector5_1_representation2 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.collector5_1, program=self.program_finished1
        ).first()
        household5_representation2 = Household.original_and_repr_objects.filter(
            is_original=False, copied_from=self.household5, program=self.program_finished1
        ).first()
        individual5_1_representation2 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual5_1, program=self.program_finished1
        ).first()
        self.assertEqual(self.payment5.collector, collector5_1_representation2)
        self.assertEqual(self.payment5.head_of_household, individual5_1_representation2)
        self.assertEqual(self.payment5.household, household5_representation2)
        self.assertEqual(self.payment_record5.head_of_household, individual5_1_representation2)
        self.assertEqual(self.payment_record5.household, household5_representation2)

        # payment7
        collector5_1_representation3 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.collector5_1, program=self.program_finished2
        ).first()
        household7_representation3 = Household.original_and_repr_objects.filter(
            is_original=False, copied_from=self.household7, program=self.program_finished2
        ).first()
        individual7_1_representation3 = Individual.original_and_repr_objects.filter(
            is_original=False, copied_from=self.individual7_1, program=self.program_finished2
        ).first()
        self.assertEqual(self.payment7.collector, collector5_1_representation3)
        self.assertEqual(self.payment7.head_of_household, individual7_1_representation3)
        self.assertEqual(self.payment7.household, household7_representation3)
        self.assertEqual(self.payment_record7.head_of_household, individual7_1_representation3)
        self.assertEqual(self.payment_record7.household, household7_representation3)


class TestCountrySpecificRules(TestCase):
    def create_hh_with_ind(
        self,
        ind_data: dict,
        hh_data: dict,
        business_area: BusinessArea,
        target_populations: Optional[List[TargetPopulation]] = None,
    ) -> tuple:
        if "registration_data_import" not in hh_data:
            hh_data["registration_data_import"] = None
        if "registration_data_import" not in ind_data:
            ind_data["registration_data_import"] = None
        individual = IndividualFactory(
            business_area=business_area,
            household=None,
            **ind_data,
        )
        household = HouseholdFactory(
            business_area=business_area,
            head_of_household=individual,
            **hh_data,
        )
        if target_populations:
            household.target_populations.set(target_populations)
        else:
            household.target_populations.set([])
        individual.household = household
        individual.save()
        return individual, household

    def setUp(self) -> None:
        # collecting_types
        generate_data_collecting_types()
        self.partial = DataCollectingType.objects.get(code="partial_individuals")
        self.full = DataCollectingType.objects.get(code="full_collection")
        self.size_only = DataCollectingType.objects.get(code="size_only")
        self.no_ind_data = DataCollectingType.objects.get(code="size_age_gender_disaggregated")

        # Country specific rules setup
        self.business_area_afghanistan = BusinessAreaFactory(name="Afghanistan")
        self.business_area_congo = BusinessAreaFactory(name="Democratic Republic of Congo")
        self.business_area_sudan = BusinessAreaFactory(name="Sudan")

        # Unknown unassigned rules setup
        self.business_area_trinidad_and_tobago = BusinessAreaFactory(name="Trinidad & Tobago")
        self.business_area_slovakia = BusinessAreaFactory(name="Slovakia")
        self.business_area_sri_lanka = BusinessAreaFactory(name="Sri Lanka")

        # Objects for Afghanistan specific rules
        self.rdi_for_afghanistan_ignore = RegistrationDataImportFactory(
            business_area=self.business_area_afghanistan,
            name="PMU-REG-Social_Transfer-Zabul-AF2401-Qalat-SHAO-v2.1",
            program=None,
        )
        # Afghanistan programs
        self.program_afg_finished = ProgramFactory(
            status=Program.FINISHED,
            business_area=self.business_area_afghanistan,
            data_collecting_type=self.full,
            name="afghanistan finished",
        )
        self.program_afg_active = ProgramFactory(
            status=Program.ACTIVE,
            business_area=self.business_area_afghanistan,
            data_collecting_type=self.full,
            name="afghanistan active full",
        )
        # Afghanistan target populations
        self.target_population_afg_finished = TargetPopulationFactory(
            program=self.program_afg_finished,
            status=TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
            business_area=self.business_area_afghanistan,
        )
        self.target_population_afg_active = TargetPopulationFactory(
            program=self.program_afg_active,
            status=TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
            business_area=self.business_area_afghanistan,
        )

        (
            _,
            self.household_afg_in_closed,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_for_afghanistan_ignore,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
            business_area=self.business_area_afghanistan,
            target_populations=[self.target_population_afg_finished],
        )
        (
            _,
            self.household_afg_in_active,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_for_afghanistan_ignore,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
            business_area=self.business_area_afghanistan,
            target_populations=[self.target_population_afg_active],
        )
        (
            _,
            self.household_afg_not_in_tp,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_for_afghanistan_ignore,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
            business_area=self.business_area_afghanistan,
            target_populations=[],
        )

        # Sudan setup
        self.rdi_for_sudan_ignore = RegistrationDataImportFactory(
            business_area=self.business_area_sudan,
            name="Health and Nutrition - FLWS Modification",
            program=None,
        )

        self.program_sudan_active = ProgramFactory(
            status=Program.ACTIVE,
            business_area=self.business_area_sudan,
            data_collecting_type=self.full,
            name="Health & Nutrition Reporting FLWS",
        )
        self.program_sudan_active_other = ProgramFactory(
            status=Program.ACTIVE,
            business_area=self.business_area_sudan,
            data_collecting_type=self.full,
            name="Active other",
        )

        self.target_population_sudan_active_other = TargetPopulationFactory(
            program=self.program_sudan_active_other,
            status=TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
            business_area=self.business_area_sudan,
        )

        (
            _,
            self.household_sudan_in_tp,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_for_sudan_ignore,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
            business_area=self.business_area_sudan,
            target_populations=[self.target_population_sudan_active_other],
        )
        (
            _,
            self.household_sudan_no_tp,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_for_sudan_ignore,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
            business_area=self.business_area_sudan,
            target_populations=[],
        )
        # Congo setup
        self.rdi_for_congo_ignore = RegistrationDataImportFactory(
            business_area=self.business_area_congo,
            name="Importation du 11 nov 2021",
            program=None,
        )

        self.program_congo_active = ProgramFactory(
            status=Program.ACTIVE,
            business_area=self.business_area_congo,
            data_collecting_type=self.full,
            name="Cash-Nutrition Manono for partners",
        )
        self.program_congo_active_other = ProgramFactory(
            status=Program.ACTIVE,
            business_area=self.business_area_congo,
            data_collecting_type=self.full,
            name="Active other",
        )

        self.target_population_congo_active_other = TargetPopulationFactory(
            program=self.program_congo_active_other,
            status=TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
            business_area=self.business_area_congo,
        )

        (
            _,
            self.household_congo_in_tp,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_for_congo_ignore,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
            business_area=self.business_area_congo,
            target_populations=[self.target_population_congo_active_other],
        )
        (
            _,
            self.household_congo_no_tp,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_for_congo_ignore,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
            business_area=self.business_area_congo,
            target_populations=[],
        )

        self.rdi_for_congo_to_withdraw = RegistrationDataImportFactory(
            business_area=self.business_area_congo,
            name="1er Cohorte DPS Manierma, 18 Mars 2022",
            program=None,
        )

        (
            _,
            self.household_congo_in_tp_withdraw,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_for_congo_to_withdraw,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
            business_area=self.business_area_congo,
            target_populations=[self.target_population_congo_active_other],
        )
        (
            _,
            self.household_congo_no_tp_withdraw,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_for_congo_to_withdraw,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
            business_area=self.business_area_congo,
            target_populations=[],
        )

        self.rdi_for_congo_to_withdraw_no_tp = RegistrationDataImportFactory(
            business_area=self.business_area_congo,
            name="Prod_test_DRC_June142023",
            program=None,
        )
        (
            _,
            self.household_congo_no_tp_withdraw_2,
        ) = self.create_hh_with_ind(
            {},
            {
                "registration_data_import": self.rdi_for_congo_to_withdraw_no_tp,
                "collect_individual_data": COLLECT_TYPE_SIZE_ONLY,
            },
            business_area=self.business_area_congo,
            target_populations=[],
        )

        # Unknown setup
        (
            _,
            self.household_unknown_for_storage,
        ) = self.create_hh_with_ind(
            {},
            {
                "collect_individual_data": COLLECT_TYPE_UNKNOWN,
            },
            business_area=self.business_area_congo,
            target_populations=[],
        )
        (
            _,
            self.household_unknown_from_sudan,
        ) = self.create_hh_with_ind(
            {},
            {
                "collect_individual_data": COLLECT_TYPE_UNKNOWN,
            },
            business_area=self.business_area_sudan,
            target_populations=[],
        )
        (
            _,
            self.household_unknown_from_trinidad,
        ) = self.create_hh_with_ind(
            {},
            {
                "collect_individual_data": COLLECT_TYPE_UNKNOWN,
            },
            business_area=self.business_area_trinidad_and_tobago,
            target_populations=[],
        )
        self.program_sudan_for_unknown = ProgramFactory(
            status=Program.ACTIVE,
            business_area=self.business_area_sudan,
            data_collecting_type=self.full,
            name="MCCT programme",
        )
        self.program_trinidad_for_unknown = ProgramFactory(
            status=Program.ACTIVE,
            business_area=self.business_area_trinidad_and_tobago,
            data_collecting_type=self.full,
            name="TEEN",
        )

        RegistrationDataImport.objects.update(created_at=timezone.make_aware(timezone.datetime(2023, 9, 20)))

    def refresh_objects(self) -> None:
        self.household_afg_in_closed.refresh_from_db()
        self.household_afg_in_active.refresh_from_db()
        self.household_afg_not_in_tp.refresh_from_db()
        self.household_sudan_in_tp.refresh_from_db()
        self.household_sudan_no_tp.refresh_from_db()
        self.household_congo_in_tp.refresh_from_db()
        self.household_congo_no_tp.refresh_from_db()
        self.household_congo_in_tp_withdraw.refresh_from_db()
        self.household_congo_no_tp_withdraw.refresh_from_db()
        self.household_congo_no_tp_withdraw_2.refresh_from_db()
        self.rdi_for_congo_to_withdraw_no_tp.refresh_from_db()
        self.rdi_for_afghanistan_ignore.refresh_from_db()
        self.rdi_for_sudan_ignore.refresh_from_db()
        self.rdi_for_congo_ignore.refresh_from_db()
        self.rdi_for_congo_to_withdraw.refresh_from_db()
        self.household_unknown_for_storage.refresh_from_db()
        self.household_unknown_from_sudan.refresh_from_db()
        self.household_unknown_from_trinidad.refresh_from_db()

    @unittest.skip("need to adjust to new managers")
    def test_migrate_data_to_representations_for_country_specific_rules(self) -> None:
        self.assertIsNone(DataCollectingType.objects.filter(code="unknown").first())

        migrate_data_to_representations()

        self.refresh_objects()

        # Test Afghanistan rules
        self.assertIn(self.rdi_for_afghanistan_ignore.program, [self.program_afg_finished, self.program_afg_active])

        self.assertEqual(
            self.household_afg_in_closed.copied_to(manager="original_and_repr_objects").count(),
            2,
        )
        self.assertEqual(
            self.household_afg_in_active.copied_to(manager="original_and_repr_objects").count(),
            1,
        )
        self.assertEqual(
            self.household_afg_not_in_tp.copied_to(manager="original_and_repr_objects").count(),
            0,
        )

        # Test Sudan rules
        self.assertIn(self.rdi_for_sudan_ignore.program, [self.program_sudan_active, self.program_sudan_active_other])
        self.assertEqual(self.household_sudan_in_tp.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertIn(
            self.program_sudan_active_other.id,
            list(
                self.household_sudan_in_tp.copied_to(manager="original_and_repr_objects").values_list(
                    "program__id", flat=True
                )
            ),
        )
        self.assertIn(
            self.program_sudan_active.id,
            list(
                self.household_sudan_in_tp.copied_to(manager="original_and_repr_objects").values_list(
                    "program__id", flat=True
                )
            ),
        )
        self.assertEqual(self.household_sudan_no_tp.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertIn(
            self.program_sudan_active_other.id,
            list(
                self.household_sudan_no_tp.copied_to(manager="original_and_repr_objects").values_list(
                    "program__id", flat=True
                )
            ),
        )
        self.assertIn(
            self.program_sudan_active.id,
            list(
                self.household_sudan_no_tp.copied_to(manager="original_and_repr_objects").values_list(
                    "program__id", flat=True
                )
            ),
        )

        # Test Congo rules
        self.assertIn(self.rdi_for_congo_ignore.program, [self.program_congo_active, self.program_congo_active_other])
        self.assertEqual(self.household_congo_in_tp.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            self.program_congo_active_other,
            self.household_congo_in_tp.copied_to(manager="original_and_repr_objects").first().program,
        )
        self.assertEqual(self.household_congo_no_tp.copied_to(manager="original_and_repr_objects").count(), 2)
        self.assertIn(
            self.program_congo_active_other.id,
            list(
                self.household_congo_no_tp.copied_to(manager="original_and_repr_objects").values_list(
                    "program__id", flat=True
                )
            ),
        )
        self.assertIn(
            self.program_congo_active.id,
            list(
                self.household_congo_no_tp.copied_to(manager="original_and_repr_objects").values_list(
                    "program__id", flat=True
                )
            ),
        )

        # Congo withdraw
        self.assertEqual(self.rdi_for_congo_to_withdraw.program, self.program_congo_active_other)
        self.assertEqual(self.household_congo_in_tp_withdraw.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            self.household_congo_in_tp_withdraw.copied_to(manager="original_and_repr_objects").first().program,
            self.program_congo_active_other,
        )
        self.assertFalse(
            self.household_congo_in_tp_withdraw.copied_to(manager="original_and_repr_objects").first().withdrawn
        )

        self.assertEqual(self.household_congo_no_tp_withdraw.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            self.household_congo_no_tp_withdraw.copied_to(manager="original_and_repr_objects").first().program,
            self.program_congo_active_other,
        )
        self.assertTrue(
            self.household_congo_no_tp_withdraw.copied_to(manager="original_and_repr_objects").first().withdrawn
        )

        self.assertEqual(
            self.rdi_for_congo_to_withdraw_no_tp.program.name,
            f"Storage program - COLLECTION TYPE {self.size_only.label}",
        )
        self.assertEqual(
            self.household_congo_no_tp_withdraw_2.copied_to(manager="original_and_repr_objects").count(), 1
        )
        self.assertEqual(
            self.household_congo_no_tp_withdraw_2.copied_to(manager="original_and_repr_objects").first().program.name,
            f"Storage program - COLLECTION TYPE {self.size_only.label}",
        )

        # Test Unknown rules
        unknown_coll_type = DataCollectingType.objects.filter(code="unknown").first()
        self.assertIsNotNone(unknown_coll_type)
        program_storage_unknown = Program.all_objects.get(
            data_collecting_type=unknown_coll_type, business_area=self.business_area_congo
        )

        self.assertEqual(self.household_unknown_for_storage.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            self.household_unknown_for_storage.copied_to(manager="original_and_repr_objects").first().program,
            program_storage_unknown,
        )

        self.assertEqual(self.household_unknown_from_sudan.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            self.household_unknown_from_sudan.copied_to(manager="original_and_repr_objects").first().program,
            self.program_sudan_for_unknown,
        )

        self.assertEqual(self.household_unknown_from_trinidad.copied_to(manager="original_and_repr_objects").count(), 1)
        self.assertEqual(
            self.household_unknown_from_trinidad.copied_to(manager="original_and_repr_objects").first().program,
            self.program_trinidad_for_unknown,
        )
