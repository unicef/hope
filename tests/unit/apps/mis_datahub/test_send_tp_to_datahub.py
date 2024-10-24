from typing import Any

from django.core.management import call_command
from django.db.utils import IntegrityError
from django.test import TestCase

from parameterized import parameterized

import hct_mis_api.apps.mis_datahub.models as dh_models
from hct_mis_api.apps.account.fixtures import PartnerFactory
from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import (
    HouseholdFactory,
    IndividualFactory,
    create_household,
)
from hct_mis_api.apps.household.models import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Document,
    DocumentType,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.mis_datahub.tasks.send_tp_to_datahub import SendTPToDatahubTask
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import (
    HouseholdSelectionFactory,
    TargetingCriteriaFactory,
    TargetingCriteriaRuleFactory,
    TargetPopulationFactory,
)
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.targeting.services.targeting_stats_refresher import refresh_stats
from hct_mis_api.apps.utils.models import MergeStatusModel


class TestSendTpToDatahub(TestCase):
    databases = {"default", "cash_assist_datahub_mis"}

    @staticmethod
    def _pre_test_commands() -> None:
        create_afghanistan()
        PartnerFactory(name="UNICEF")
        call_command("loadcountries")
        call_command("generatedocumenttypes")
        call_command("loadcountrycodes")
        business_area_with_data_sharing = BusinessArea.objects.first()
        business_area_with_data_sharing.has_data_sharing_agreement = True
        business_area_with_data_sharing.save()

    @staticmethod
    def _create_target_population(**kwargs: Any) -> TargetPopulation:
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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls._pre_test_commands()

        business_area_with_data_sharing = BusinessArea.objects.first()

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="State",
            country=country,
            area_level=1,
        )
        admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")

        cls.unhcr, _ = Partner.objects.get_or_create(name="UNHCR", defaults={"is_un": True})

        cls.program_individual_data_needed_true = ProgramFactory(
            business_area=business_area_with_data_sharing,
        )
        cls.program_individual_data_needed_false = ProgramFactory(
            business_area=business_area_with_data_sharing,
        )
        cls.program_third = ProgramFactory(
            business_area=business_area_with_data_sharing,
        )
        rdi = RegistrationDataImportFactory()
        rdi.program.save()
        rdi_second = RegistrationDataImportFactory()
        rdi_second.program.save()

        cls.household = HouseholdFactory.build(
            size=4,
            registration_data_import=rdi,
            admin_area=admin_area,
            program=rdi.program,
        )
        cls.household.household_collection.save()
        cls.household_second = HouseholdFactory.build(
            size=1, registration_data_import=rdi_second, admin_area=admin_area, program=rdi_second.program
        )
        cls.household_second.household_collection.save()
        cls.second_household_head = IndividualFactory(
            household=cls.household_second,
            relationship="HEAD",
            registration_data_import=rdi_second,
            program=rdi_second.program,
        )
        unhcr, _ = Partner.objects.get_or_create(name="UNHCR", defaults={"is_un": True})
        IndividualRoleInHousehold.objects.create(
            individual=cls.second_household_head,
            household=cls.household_second,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        cls.household_second.head_of_household = cls.second_household_head
        cls.household_second.save()

        cls.individual_primary = IndividualFactory(
            household=cls.household, relationship="HEAD", registration_data_import=rdi, program=rdi.program
        )
        IndividualRoleInHousehold.objects.create(
            individual=cls.individual_primary,
            household=cls.household,
            role=ROLE_PRIMARY,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        Document.objects.create(
            document_number="1231231",
            photo="",
            individual=cls.individual_primary,
            type=DocumentType.objects.filter(key="national_id").first(),
            program=cls.individual_primary.program,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        IndividualIdentity.objects.create(
            partner=cls.unhcr,
            individual=cls.individual_primary,
            number="1111",
            country=country,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        cls.individual_alternate = IndividualFactory(
            household=cls.household, registration_data_import=rdi, program=rdi.program
        )
        IndividualRoleInHousehold.objects.create(
            individual=cls.individual_alternate,
            household=cls.household,
            role=ROLE_ALTERNATE,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        IndividualIdentity.objects.create(
            individual=cls.individual_alternate,
            number="2222",
            partner=cls.unhcr,
            country=country,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        cls.individual_no_role_first = IndividualFactory(
            household=cls.household,
            registration_data_import=rdi,
            program=rdi.program,
        )
        IndividualIdentity.objects.create(
            individual=cls.individual_no_role_first,
            number="3333",
            partner=cls.unhcr,
            country=country,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        cls.individual_no_role_second = IndividualFactory(
            household=cls.household, registration_data_import=rdi, program=rdi.program
        )
        IndividualIdentity.objects.create(
            individual=cls.individual_no_role_second,
            number="4444",
            partner=cls.unhcr,
            country=country,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        cls.household.head_of_household = cls.individual_primary
        cls.household.save()

        cls.target_population_first = cls._create_target_population(
            sent_to_datahub=False,
            name="Test TP",
            program=cls.program_individual_data_needed_true,
            business_area=business_area_with_data_sharing,
            status=TargetPopulation.STATUS_PROCESSING,
            program_cycle=cls.program_individual_data_needed_true.cycles.first(),
        )
        cls.target_population_first.households.set([cls.household])
        cls.target_population_first = refresh_stats(cls.target_population_first)
        cls.target_population_first.save()

        cls.target_population_second = cls._create_target_population(
            sent_to_datahub=False,
            name="Test TP 2",
            program=cls.program_individual_data_needed_false,
            business_area=business_area_with_data_sharing,
            status=TargetPopulation.STATUS_PROCESSING,
            program_cycle=cls.program_individual_data_needed_false.cycles.first(),
        )
        cls.target_population_second.households.set([cls.household])
        cls.target_population_second = refresh_stats(cls.target_population_second)
        cls.target_population_second.save()

        cls.target_population_third = cls._create_target_population(
            sent_to_datahub=False,
            name="Test TP 3",
            program=cls.program_third,
            business_area=business_area_with_data_sharing,
            status=TargetPopulation.STATUS_PROCESSING,
            program_cycle=cls.program_third.cycles.first(),
        )
        cls.target_population_third.households.set([cls.household_second])
        cls.target_population_third = refresh_stats(cls.target_population_third)
        cls.target_population_third.save()

    def test_individual_data_needed_true(self) -> None:
        task = SendTPToDatahubTask()
        task.send_target_population(self.target_population_first)

        dh_household = dh_models.Household.objects.all()
        dh_individuals = dh_models.Individual.objects.all()
        dh_documents = dh_models.Document.objects.all()
        dh_roles = dh_models.IndividualRoleInHousehold.objects.all()

        self.assertEqual(dh_household.count(), 1)
        self.assertEqual(dh_individuals.count(), 2)
        self.assertEqual(dh_documents.count(), 1)
        self.assertEqual(dh_roles.count(), 2)

    def test_individual_data_needed_false(self) -> None:
        task = SendTPToDatahubTask()
        task.send_target_population(self.target_population_second)

        dh_household = dh_models.Household.objects.all()
        dh_individuals = dh_models.Individual.objects.all()
        dh_documents = dh_models.Document.objects.all()
        dh_roles = dh_models.IndividualRoleInHousehold.objects.all()

        self.assertEqual(dh_household.count(), 1)
        self.assertEqual(dh_individuals.count(), 2)
        self.assertEqual(dh_documents.count(), 1)
        self.assertEqual(dh_roles.count(), 2)

    def test_individual_sharing_is_true_and_unhcr_id(self) -> None:
        task = SendTPToDatahubTask()
        task.send_target_population(self.target_population_third)

        dh_household = dh_models.Household.objects.all()
        dh_individuals = dh_models.Individual.objects.all()
        dh_documents = dh_models.Document.objects.all()
        dh_roles = dh_models.IndividualRoleInHousehold.objects.all()
        self.assertEqual(dh_household.count(), 1)
        self.assertEqual(dh_household.first().unhcr_id, None)
        self.assertEqual(dh_individuals.count(), 1)
        self.assertEqual(dh_documents.count(), 0)
        self.assertEqual(dh_roles.count(), 1)

    def test_send_two_times_household_with_different(self) -> None:
        business_area_with_data_sharing = BusinessArea.objects.first()

        program_individual_data_needed_true = ProgramFactory(
            business_area=business_area_with_data_sharing,
        )
        program_individual_data_needed_false = ProgramFactory(
            business_area=business_area_with_data_sharing,
        )
        (household, individuals) = create_household(
            {"size": 3, "residence_status": "HOST", "business_area": business_area_with_data_sharing},
        )

        target_population_first = self._create_target_population(
            sent_to_datahub=False,
            name="Test TP xD",
            program=program_individual_data_needed_false,
            business_area=business_area_with_data_sharing,
            status=TargetPopulation.STATUS_PROCESSING,
            program_cycle=program_individual_data_needed_false.cycles.first(),
        )
        target_population_first.households.set([household])
        target_population_first = refresh_stats(target_population_first)
        target_population_second = self._create_target_population(
            sent_to_datahub=False,
            name="Test TP xD 2",
            program=program_individual_data_needed_true,
            business_area=business_area_with_data_sharing,
            status=TargetPopulation.STATUS_PROCESSING,
            program_cycle=program_individual_data_needed_true.cycles.first(),
        )
        target_population_second.households.set([household])
        target_population_second = refresh_stats(target_population_second)
        task = SendTPToDatahubTask()
        task.send_target_population(target_population_first)
        dh_households_count = dh_models.Household.objects.filter(mis_id=household.id).count()
        dh_individuals_count = dh_models.Individual.objects.filter(household_mis_id=household.id).count()
        self.assertEqual(dh_households_count, 1)
        self.assertEqual(dh_individuals_count, 1)
        task.send_target_population(target_population_second)
        dh_individuals_count = dh_models.Individual.objects.filter(household_mis_id=household.id).count()
        dh_households_count = dh_models.Household.objects.filter(mis_id=household.id).count()
        self.assertEqual(dh_households_count, 1)
        self.assertEqual(dh_individuals_count, 1)

    @parameterized.expand(
        [
            ("equal", "AF", "AFG"),
            ("custom_code", "AU", "AUL"),
        ]
    )
    def test_send_household_country(self, _: Any, iso_code2: str, expected_ca_code: str) -> None:
        (household, individuals) = create_household(household_args={"size": 1})
        household.country = geo_models.Country.objects.filter(iso_code2=iso_code2).first()
        household.save()
        task = SendTPToDatahubTask()
        task.dh_session = dh_models.Session()
        dh_household = task._prepare_datahub_object_household(household)
        self.assertEqual(dh_household.country, expected_ca_code)

    def test_trim_targeting_criteria(self) -> None:
        business_area = BusinessArea.objects.first()

        program = ProgramFactory(
            business_area=business_area,
        )

        targeting_criteria = TargetingCriteriaFactory()
        TargetingCriteriaRuleFactory.create_batch(150, targeting_criteria=targeting_criteria)
        target_population = TargetPopulationFactory(
            program=program,
            status=TargetPopulation.STATUS_PROCESSING,
            targeting_criteria=targeting_criteria,
        )
        target_population = refresh_stats(target_population)

        task = SendTPToDatahubTask()
        task.send_target_population(target_population)

        dh_target_population = dh_models.TargetPopulation.objects.filter(mis_id=target_population.id).first()

        self.assertEqual(len(dh_target_population.targeting_criteria), 390)
        self.assertTrue("..." in dh_target_population.targeting_criteria)

    def test_should_not_trim_targeting_criteria(self) -> None:
        business_area = BusinessArea.objects.first()

        program = ProgramFactory(
            business_area=business_area,
        )

        targeting_criteria = TargetingCriteriaFactory()
        TargetingCriteriaRuleFactory.create_batch(50, targeting_criteria=targeting_criteria)
        target_population = TargetPopulationFactory(
            program=program,
            status=TargetPopulation.STATUS_PROCESSING,
            targeting_criteria=targeting_criteria,
        )
        target_population = refresh_stats(target_population)

        task = SendTPToDatahubTask()
        task.send_target_population(target_population)

        dh_target_population = dh_models.TargetPopulation.objects.filter(mis_id=target_population.id).first()

        self.assertEqual(len(dh_target_population.targeting_criteria), 194)
        self.assertFalse("..." in dh_target_population.targeting_criteria)

    def test_not_creating_duplicate_households(self) -> None:
        business_area = BusinessArea.objects.first()

        program = ProgramFactory(
            business_area=business_area,
        )

        targeting_criteria = TargetingCriteriaFactory()
        TargetingCriteriaRuleFactory.create_batch(50, targeting_criteria=targeting_criteria)
        target_population = TargetPopulationFactory(
            program=program,
            status=TargetPopulation.STATUS_PROCESSING,
            targeting_criteria=targeting_criteria,
        )

        try:
            for _ in range(2):
                HouseholdSelectionFactory(
                    household=self.household,
                    target_population=target_population,
                )
        except IntegrityError:
            pass
        else:
            self.fail("Should raise IntegrityError")
