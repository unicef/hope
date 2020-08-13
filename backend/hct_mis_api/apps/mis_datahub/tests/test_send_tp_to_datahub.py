from django.core.management import call_command
from django.test import TestCase

from core.fixtures import AdminAreaTypeFactory, AdminAreaFactory
from core.models import BusinessArea
from household.fixtures import (
    HouseholdFactory,
    IndividualFactory,
)
from household.models import (
    ROLE_PRIMARY,
    ROLE_ALTERNATE,
    Document,
    DocumentType,
    Agency,
    HouseholdIdentity,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from mis_datahub.tasks.send_tp_to_datahub import SendTPToDatahubTask
from program.fixtures import ProgramFactory
from registration_data.fixtures import RegistrationDataImportFactory
from targeting.models import TargetPopulation
import mis_datahub.models as dh_models


class TestSendTpToDatahub(TestCase):
    multi_db = True

    @staticmethod
    def _pre_test_commands():
        call_command("loadbusinessareas")
        call_command("generatedocumenttypes")
        business_area_with_data_sharing = BusinessArea.objects.first()
        business_area_with_data_sharing.has_data_sharing_agreement = True
        business_area_with_data_sharing.save()

    @staticmethod
    def _create_target_population(**kwargs):
        tp_nullable = {
            "ca_id": None,
            "ca_hash_id": None,
            "created_by": None,
            "approved_at": None,
            "approved_by": None,
            "finalized_at": None,
            "finalized_by": None,
            "candidate_list_total_households": None,
            "candidate_list_total_individuals": None,
            "final_list_total_households": None,
            "final_list_total_individuals": None,
            "selection_computation_metadata": None,
            "candidate_list_targeting_criteria": None,
            "final_list_targeting_criteria": None,
        }

        return TargetPopulation.objects.create(**tp_nullable, **kwargs,)

    @classmethod
    def setUpTestData(cls):
        cls._pre_test_commands()

        business_area_with_data_sharing = BusinessArea.objects.get(
            has_data_sharing_agreement=True
        )
        state_area_type = AdminAreaTypeFactory(
            name="State",
            business_area=business_area_with_data_sharing,
            admin_level=1,
        )
        admin_area = AdminAreaFactory(admin_area_type=state_area_type)
        unhcr_agency = Agency.objects.create(type="unhcr", label="UNHCR")
        test_agency = Agency.objects.create(type="test", label="test")

        cls.program_individual_data_needed_true = ProgramFactory(
            individual_data_needed=True,
            business_area=business_area_with_data_sharing,
        )
        cls.program_individual_data_needed_false = ProgramFactory(
            individual_data_needed=False,
            business_area=business_area_with_data_sharing,
        )
        cls.program_third = ProgramFactory(
            individual_data_needed=False,
            business_area=business_area_with_data_sharing,
        )
        rdi = RegistrationDataImportFactory()
        rdi_second = RegistrationDataImportFactory()

        cls.household = HouseholdFactory.build(
            size=4, registration_data_import=rdi, admin_area=admin_area,
        )
        cls.household_second = HouseholdFactory.build(
            size=1, registration_data_import=rdi_second, admin_area=admin_area,
        )
        cls.second_household_head = IndividualFactory(
            household=cls.household_second,
            relationship="HEAD",
            registration_data_import=rdi_second,
        )
        IndividualRoleInHousehold.objects.create(
            individual=cls.second_household_head,
            household=cls.household_second,
            role=ROLE_PRIMARY,
        )
        cls.household_second.head_of_household = cls.second_household_head
        cls.household_second.save()

        HouseholdIdentity.objects.create(
            agency=unhcr_agency,
            household=cls.household_second,
            document_number="45745745745",
        )

        cls.individual_primary = IndividualFactory(
            household=cls.household,
            relationship="HEAD",
            registration_data_import=rdi,
        )
        IndividualRoleInHousehold.objects.create(
            individual=cls.individual_primary,
            household=cls.household,
            role=ROLE_PRIMARY,
        )
        Document.objects.create(
            document_number="1231231",
            photo="",
            individual=cls.individual_primary,
            type=DocumentType.objects.filter(type="NATIONAL_ID").first(),
        )
        IndividualIdentity.objects.create(
            agency=unhcr_agency,
            individual=cls.individual_primary,
            number="1111",
        )

        cls.individual_alternate = IndividualFactory(
            household=cls.household, registration_data_import=rdi,
        )
        IndividualRoleInHousehold.objects.create(
            individual=cls.individual_alternate,
            household=cls.household,
            role=ROLE_ALTERNATE,
        )
        IndividualIdentity.objects.create(
            agency=unhcr_agency,
            individual=cls.individual_alternate,
            number="2222",
        )

        cls.individual_no_role_first = IndividualFactory(
            household=cls.household, registration_data_import=rdi,
        )
        IndividualIdentity.objects.create(
            agency=unhcr_agency,
            individual=cls.individual_no_role_first,
            number="3333",
        )

        cls.individual_no_role_second = IndividualFactory(
            household=cls.household, registration_data_import=rdi,
        )
        IndividualIdentity.objects.create(
            agency=unhcr_agency,
            individual=cls.individual_no_role_second,
            number="4444",
        )

        cls.household.head_of_household = cls.individual_primary
        cls.household.save()

        HouseholdIdentity.objects.create(
            agency=test_agency,
            household=cls.household,
            document_number="123123123",
        )

        cls.target_population_first = cls._create_target_population(
            sent_to_datahub=False,
            name="Test TP",
            program=cls.program_individual_data_needed_true,
            business_area=business_area_with_data_sharing,
            status=TargetPopulation.STATUS_FINALIZED,
        )
        cls.target_population_first.households.set([cls.household])

        cls.target_population_second = cls._create_target_population(
            sent_to_datahub=False,
            name="Test TP 2",
            program=cls.program_individual_data_needed_false,
            business_area=business_area_with_data_sharing,
            status=TargetPopulation.STATUS_FINALIZED,
        )
        cls.target_population_second.households.set([cls.household])

        cls.target_population_third = cls._create_target_population(
            sent_to_datahub=False,
            name="Test TP 3",
            program=cls.program_third,
            business_area=business_area_with_data_sharing,
            status=TargetPopulation.STATUS_FINALIZED,
        )
        cls.target_population_third.households.set([cls.household_second])

    def test_individual_data_needed_true(self):
        task = SendTPToDatahubTask()
        task.send_tp(self.target_population_first)

        dh_household = dh_models.Household.objects.all()
        dh_individuals = dh_models.Individual.objects.all()
        dh_documents = dh_models.Document.objects.all()
        dh_roles = dh_models.IndividualRoleInHousehold.objects.all()

        self.assertEqual(dh_household.count(), 1)
        self.assertEqual(dh_individuals.count(), 4)
        self.assertEqual(dh_documents.count(), 1)
        self.assertEqual(dh_roles.count(), 2)

    def test_individual_data_needed_false(self):
        task = SendTPToDatahubTask()
        task.send_tp(self.target_population_second)

        dh_household = dh_models.Household.objects.all()
        dh_individuals = dh_models.Individual.objects.all()
        dh_documents = dh_models.Document.objects.all()
        dh_roles = dh_models.IndividualRoleInHousehold.objects.all()

        self.assertEqual(dh_household.count(), 1)
        self.assertEqual(dh_individuals.count(), 2)
        self.assertEqual(dh_documents.count(), 1)
        self.assertEqual(dh_roles.count(), 2)

    def test_individual_sharing_is_true_and_unhcr_id(self):
        task = SendTPToDatahubTask()
        task.send_tp(self.target_population_third)

        dh_household = dh_models.Household.objects.all()
        dh_individuals = dh_models.Individual.objects.all()
        dh_documents = dh_models.Document.objects.all()
        dh_roles = dh_models.IndividualRoleInHousehold.objects.all()

        self.assertEqual(dh_household.count(), 1)
        self.assertEqual(dh_individuals.count(), 1)
        self.assertEqual(dh_documents.count(), 0)
        self.assertEqual(dh_roles.count(), 1)
