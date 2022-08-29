from django.core.management import call_command
from django.test import TestCase

import hct_mis_api.apps.mis_datahub.models as dh_models
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.mis_datahub.tasks.send_tp_to_datahub import SendTPToDatahubTask
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.models import TargetPopulation


class TestExternalCollectorSendTpToDatahub(TestCase):
    multi_db = True
    databases = "__all__"

    @staticmethod
    def _pre_test_commands():
        create_afghanistan()
        call_command("loadcountries")
        call_command("generatedocumenttypes")
        call_command("loadcountrycodes")
        business_area_with_data_sharing = BusinessArea.objects.first()
        business_area_with_data_sharing.has_data_sharing_agreement = True
        business_area_with_data_sharing.save()

    @staticmethod
    def _create_target_population(**kwargs):
        tp_nullable = {
            "ca_id": None,
            "ca_hash_id": None,
            "created_by": None,
            "change_date": None,
            "changed_by": None,
            "finalized_at": None,
            "finalized_by": None,
        }

        return TargetPopulation.objects.create(
            **tp_nullable,
            **kwargs,
        )

    @classmethod
    def setUpTestData(cls):
        cls._pre_test_commands()

        business_area_with_data_sharing = BusinessArea.objects.first()

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="State",
            country=country,
            area_level=1,
        )
        admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")

        cls.program_individual_data_needed_true = ProgramFactory(
            individual_data_needed=True,
            business_area=business_area_with_data_sharing,
        )
        cls.program_individual_data_needed_false = ProgramFactory(
            individual_data_needed=False,
            business_area=business_area_with_data_sharing,
        )

        rdi = RegistrationDataImportFactory()
        rdi_second = RegistrationDataImportFactory()

        cls.create_first_household(admin_area, rdi)

        cls.create_second_household(admin_area, rdi_second)
        cls.create_third_household(admin_area, rdi_second)

        cls.target_population_with_individuals = cls._create_target_population(
            sent_to_datahub=False,
            name="Test TP",
            program=cls.program_individual_data_needed_true,
            business_area=business_area_with_data_sharing,
            status=TargetPopulation.STATUS_PROCESSING,
        )
        cls.target_population_with_individuals.households.set([cls.household, cls.household_second])
        cls.target_population_with_individuals.refresh_stats()
        cls.target_population_with_individuals.save()


        cls.target_population_without_individuals = cls._create_target_population(
            sent_to_datahub=False,
            name="Test TP 2",
            program=cls.program_individual_data_needed_false,
            business_area=business_area_with_data_sharing,
            status=TargetPopulation.STATUS_PROCESSING,
        )
        cls.target_population_without_individuals.households.set([cls.household, cls.household_second])
        cls.target_population_without_individuals.refresh_stats()
        cls.target_population_without_individuals.save()

    @classmethod
    def create_first_household(cls, admin_area, rdi):
        cls.household = HouseholdFactory.build(
            size=4,
            registration_data_import=rdi,
            admin_area=admin_area,
        )
        cls.household1_individual_primary_and_head = IndividualFactory(
            household=cls.household,
            relationship="HEAD",
            registration_data_import=rdi,
        )
        IndividualRoleInHousehold.objects.create(
            individual=cls.household1_individual_primary_and_head,
            household=cls.household,
            role=ROLE_PRIMARY,
        )
        cls.household1_individual_alternate = IndividualFactory(
            household=cls.household,
            registration_data_import=rdi,
        )
        IndividualRoleInHousehold.objects.create(
            individual=cls.household1_individual_alternate,
            household=cls.household,
            role=ROLE_ALTERNATE,
        )
        cls.individual_no_role_first = IndividualFactory(
            household=cls.household,
            registration_data_import=rdi,
        )
        cls.individual_no_role_second = IndividualFactory(
            household=cls.household,
            registration_data_import=rdi,
        )
        cls.household.head_of_household = cls.household1_individual_primary_and_head
        cls.household.save()

    @classmethod
    def create_second_household(cls, admin_area, rdi_second):
        cls.household_second = HouseholdFactory.build(
            size=1,
            registration_data_import=rdi_second,
            admin_area=admin_area,
        )
        cls.external_primary_collector_household = HouseholdFactory.build(
            size=1,
            registration_data_import=rdi_second,
            admin_area=admin_area,
        )
        cls.second_household_head = IndividualFactory(
            household=cls.household_second,
            relationship="HEAD",
            registration_data_import=rdi_second,
        )
        cls.external_primary_collector = IndividualFactory(
            household=cls.external_primary_collector_household,
            registration_data_import=rdi_second,
        )
        cls.external_primary_collector_household.head_of_household = cls.external_primary_collector
        cls.external_primary_collector_household.save()
        cls.external_alternate_collector = IndividualFactory(
            registration_data_import=rdi_second,
            household=cls.external_primary_collector_household,
        )
        IndividualRoleInHousehold.objects.create(
            individual=cls.external_primary_collector,
            household=cls.household_second,
            role=ROLE_PRIMARY,
        )
        IndividualRoleInHousehold.objects.create(
            individual=cls.external_alternate_collector,
            household=cls.household_second,
            role=ROLE_ALTERNATE,
        )
        cls.household_second.head_of_household = cls.second_household_head
        cls.household_second.save()

    @classmethod
    def create_third_household(cls, admin_area, rdi_second):
        """this is generated only to have additional informaation in DB"""
        household_third = HouseholdFactory.build(
            size=1,
            registration_data_import=rdi_second,
            admin_area=admin_area,
        )
        external_primary_collector_household = HouseholdFactory.build(
            size=1,
            registration_data_import=rdi_second,
            admin_area=admin_area,
        )
        household_third_head = IndividualFactory(
            household=household_third,
            relationship="HEAD",
            registration_data_import=rdi_second,
        )
        external_primary_collector = IndividualFactory(
            household=external_primary_collector_household,
            registration_data_import=rdi_second,
        )
        external_primary_collector_household.head_of_household = external_primary_collector
        external_primary_collector_household.save()
        external_alternate_collector = IndividualFactory(
            registration_data_import=rdi_second,
            household=external_primary_collector_household,
        )
        IndividualRoleInHousehold.objects.create(
            individual=external_primary_collector,
            household=household_third,
            role=ROLE_PRIMARY,
        )
        IndividualRoleInHousehold.objects.create(
            individual=external_alternate_collector,
            household=household_third,
            role=ROLE_ALTERNATE,
        )
        household_third.head_of_household = household_third_head
        household_third.save()

    def test_send_targeting_with_external_collectors_with_individuals(self):
        task = SendTPToDatahubTask()
        task.send_target_population(self.target_population_with_individuals)

        # Check first household in DB
        self.assertEqual(
            dh_models.Household.objects.filter(mis_id=self.household.id).count(),
            1,
            "Household 1 should be in MIS datahub",
        )

        self.assertEqual(
            dh_models.Individual.objects.filter(mis_id=self.household1_individual_primary_and_head.id).count(),
            1,
            "Head of household for first household should be in datahub",
        )
        self.assertEqual(
            dh_models.Individual.objects.filter(mis_id=self.household1_individual_alternate.id).count(),
            1,
            "Alternate collector for first household should be in datahub",
        )
        self.assertEqual(
            dh_models.Individual.objects.filter(
                mis_id__in=[self.individual_no_role_first.id, self.individual_no_role_second.id]
            ).count(),
            2,
            "All individuals for first household should be in datahub",
        )
        self.assertEqual(
            dh_models.IndividualRoleInHousehold.objects.filter(
                individual_mis_id=self.household1_individual_primary_and_head.id,
                household_mis_id=self.household.id,
                role=ROLE_PRIMARY,
            ).count(),
            1,
            "Primary collector role for household 1 should exist",
        )
        self.assertEqual(
            dh_models.IndividualRoleInHousehold.objects.filter(
                individual_mis_id=self.household1_individual_alternate.id,
                household_mis_id=self.household.id,
                role=ROLE_ALTERNATE,
            ).count(),
            1,
            "Alternate collector role for household 1 should exist",
        )

        # Check 2nd household in DB
        self.assertEqual(
            dh_models.Household.objects.filter(mis_id=self.household_second.id).count(),
            1,
            "Household 2 should be in MIS datahub",
        )
        self.assertEqual(
            dh_models.Household.objects.filter(mis_id=self.external_primary_collector_household.id).count(),
            1,
            "Primary collector household should be in MIS datahub",
        )
        self.assertEqual(
            dh_models.Individual.objects.filter(mis_id=self.second_household_head.id).count(),
            1,
            "Head of household for 2nd household should be in datahub",
        )

        self.assertEqual(
            dh_models.Individual.objects.filter(mis_id=self.external_primary_collector.id).count(),
            1,
            "External Primary collector for 2nd household should be in datahub",
        )
        self.assertEqual(
            dh_models.Individual.objects.filter(mis_id=self.external_primary_collector.id).count(),
            1,
            "External Alternate collector for 2nd household should be in datahub",
        )

        self.assertEqual(
            dh_models.IndividualRoleInHousehold.objects.filter(
                individual_mis_id=self.external_primary_collector.id,
                household_mis_id=self.household_second.id,
                role=ROLE_PRIMARY,
            ).count(),
            1,
            "Primary collector role for 2nd household should exist",
        )

        self.assertEqual(
            dh_models.IndividualRoleInHousehold.objects.filter(
                individual_mis_id=self.external_alternate_collector.id,
                household_mis_id=self.household_second.id,
                role=ROLE_ALTERNATE,
            ).count(),
            1,
            "Alternate collector role for 2nd household should exist",
        )

        # check for duplcations

        self.assertEqual(
            dh_models.Household.objects.count(),
            3,
            "Only 3 households should be copied",
        )

        self.assertEqual(
            dh_models.Individual.objects.count(),
            7,
            "Only 7 individuals should be copied",
        )
        self.assertEqual(
            dh_models.IndividualRoleInHousehold.objects.count(),
            4,
            "Only 4 Roles should be copied",
        )

    def test_send_targeting_with_external_collectors_without_individuals(self):
        task = SendTPToDatahubTask()
        task.send_target_population(self.target_population_without_individuals)

        # Check first household in DB
        self.assertEqual(
            dh_models.Household.objects.filter(mis_id=self.household.id).count(),
            1,
            "Household 1 should be in MIS datahub",
        )

        self.assertEqual(
            dh_models.Individual.objects.filter(mis_id=self.household1_individual_primary_and_head.id).count(),
            1,
            "Head of household for first household should be in datahub",
        )
        self.assertEqual(
            dh_models.Individual.objects.filter(mis_id=self.household1_individual_alternate.id).count(),
            1,
            "Alternate collector for first household should be in datahub",
        )
        self.assertEqual(
            dh_models.Individual.objects.filter(
                mis_id__in=[self.individual_no_role_first.id, self.individual_no_role_second.id]
            ).count(),
            0,
            "Individuals without role should not be sent",
        )
        self.assertEqual(
            dh_models.IndividualRoleInHousehold.objects.filter(
                individual_mis_id=self.household1_individual_primary_and_head.id,
                household_mis_id=self.household.id,
                role=ROLE_PRIMARY,
            ).count(),
            1,
            "Primary collector role for household 1 should exist",
        )
        self.assertEqual(
            dh_models.IndividualRoleInHousehold.objects.filter(
                individual_mis_id=self.household1_individual_alternate.id,
                household_mis_id=self.household.id,
                role=ROLE_ALTERNATE,
            ).count(),
            1,
            "Alternate collector role for household 1 should exist",
        )

        # Check 2nd household in DB
        self.assertEqual(
            dh_models.Household.objects.filter(mis_id=self.household_second.id).count(),
            1,
            "Household 2 should be in MIS datahub",
        )
        self.assertEqual(
            dh_models.Household.objects.filter(mis_id=self.external_primary_collector_household.id).count(),
            1,
            "Primary collector household should be in MIS datahub",
        )
        self.assertEqual(
            dh_models.Individual.objects.filter(mis_id=self.second_household_head.id).count(),
            1,
            "Head of household for 2nd household should be in datahub",
        )

        self.assertEqual(
            dh_models.Individual.objects.filter(mis_id=self.external_primary_collector.id).count(),
            1,
            "External Primary collector for 2nd household should be in datahub",
        )
        self.assertEqual(
            dh_models.Individual.objects.filter(mis_id=self.external_primary_collector.id).count(),
            1,
            "External Alternate collector for 2nd household should be in datahub",
        )

        self.assertEqual(
            dh_models.IndividualRoleInHousehold.objects.filter(
                individual_mis_id=self.external_primary_collector.id,
                household_mis_id=self.household_second.id,
                role=ROLE_PRIMARY,
            ).count(),
            1,
            "Primary collector role for 2nd household should exist",
        )

        self.assertEqual(
            dh_models.IndividualRoleInHousehold.objects.filter(
                individual_mis_id=self.external_alternate_collector.id,
                household_mis_id=self.household_second.id,
                role=ROLE_ALTERNATE,
            ).count(),
            1,
            "Alternate collector role for 2nd household should exist",
        )

        # check for duplcations

        self.assertEqual(
            dh_models.Household.objects.count(),
            3,
            "Only 3 households should be copied",
        )

        self.assertEqual(
            dh_models.Individual.objects.count(),
            5,
            "Only 5 individuals should be copied",
        )
        self.assertEqual(
            dh_models.IndividualRoleInHousehold.objects.count(),
            4,
            "Only 4 Roles should be copied",
        )
