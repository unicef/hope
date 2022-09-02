import uuid
from datetime import datetime
from django.utils import timezone
from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase

import hct_mis_api.apps.mis_datahub.models as dh_models
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import (
    ROLE_PRIMARY,
    UNHCR,
    Agency,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.mis_datahub.tasks.send_tp_to_datahub import SendTPToDatahubTask
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation


class TestDataSendTpToDatahub(TestCase):
    multi_db = True
    databases = "__all__"

    @staticmethod
    def _pre_test_commands():
        create_afghanistan()
        call_command("generatedocumenttypes")
        call_command("loadcountries")
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
            "targeting_criteria": None,
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
        state_area_type = AreaTypeFactory(
            name="State",
            country=country,
            area_level=1,
        )
        province_area_type = AreaTypeFactory(
            name="Province",
            country=country,
            area_level=2,
        )
        admin_area1 = AreaFactory(name="City Test", area_type=state_area_type, p_code="asdfgfhghkjltr1")
        admin_area2 = AreaFactory(
            name="City Test", area_type=province_area_type, p_code="asdfgfhghkjltr2", parent=admin_area1
        )

        cls.program = ProgramFactory(
            individual_data_needed=True,
            business_area=business_area_with_data_sharing,
            ca_hash_id=uuid.uuid4(),
            ca_id="TEST",
        )
        rdi = RegistrationDataImportFactory()

        cls.create_first_household(admin_area2, rdi)

        cls.target_population = cls._create_target_population(
            sent_to_datahub=False,
            name="Test TP",
            program=cls.program,
            business_area=business_area_with_data_sharing,
            status=TargetPopulation.STATUS_PROCESSING,
        )
        cls.target_population.households.set([cls.household])
        cls.target_population.refresh_stats()
        cls.target_population.save()
        HouseholdSelection.objects.update(vulnerability_score=1.23)

    @classmethod
    def create_first_household(cls, admin_area, rdi):
        country = Country.objects.filter(iso_code2="PL").first()
        cls.household = HouseholdFactory.build(
            size=1, registration_data_import=rdi, admin_area=admin_area, unhcr_id="UNHCR-1337", country=country
        )
        unhcr_agency = Agency.objects.create(type=UNHCR)
        cls.individual = IndividualFactory(household=cls.household, relationship="HEAD", registration_data_import=rdi)
        IndividualIdentity.objects.create(agency=unhcr_agency, number="UN-TEST", individual=cls.individual)
        IndividualRoleInHousehold.objects.create(
            individual=cls.individual,
            household=cls.household,
            role=ROLE_PRIMARY,
        )

        cls.household.head_of_household = cls.individual
        cls.household.save()

    def test_program_data_is_send_correctly(self):
        self.maxDiff = None
        self.target_population.refresh_from_db()
        task = SendTPToDatahubTask()
        task.send_target_population(self.target_population)
        expected_program_dict = {
            "business_area": "0060",
            "ca_hash_id": str(self.program.ca_hash_id),
            "ca_id": self.program.ca_id,
            "description": self.program.description,
            "end_date": timezone.make_aware(datetime.combine(self.program.end_date, datetime.min.time())),
            "individual_data_needed": True,
            "mis_id": self.program.id,
            "name": self.program.name,
            "scope": self.program.scope,
            "start_date": timezone.make_aware(datetime.combine(self.program.start_date, datetime.min.time())),
        }
        dh_program_dict = dh_models.Program.objects.first().__dict__
        dh_program_dict.pop("_state")
        dh_program_dict.pop("id")
        dh_program_dict.pop("session_id")
        self.assertDictEqual(expected_program_dict, dh_program_dict)

    def test_target_population_data_is_send_correctly(self):
        self.maxDiff = None
        self.target_population.refresh_from_db()
        task = SendTPToDatahubTask()
        task.send_target_population(self.target_population)
        expected_target_population_dict = {
            "active_households": 1,
            "mis_id": self.target_population.id,
            "name": "Test TP",
            "population_type": "HOUSEHOLD",
            "program_mis_id": self.program.id,
            "targeting_criteria": "",
        }
        dh_target_population_dict = dh_models.TargetPopulation.objects.first().__dict__
        dh_target_population_dict.pop("_state")
        dh_target_population_dict.pop("id")
        dh_target_population_dict.pop("session_id")
        self.assertDictEqual(expected_target_population_dict, dh_target_population_dict)

    def test_target_population_entry_data_is_send_correctly(self):
        self.maxDiff = None
        self.target_population.refresh_from_db()
        task = SendTPToDatahubTask()
        task.send_target_population(self.target_population)
        expected_target_population_entry_dict = {
            "household_mis_id": self.household.id,
            "household_unhcr_id": "UNHCR-1337",
            "individual_mis_id": None,
            "individual_unhcr_id": None,
            "target_population_mis_id": self.target_population.id,
            "vulnerability_score": Decimal("1.230"),
        }
        dh_target_population_entry_dict = dh_models.TargetPopulationEntry.objects.first().__dict__
        dh_target_population_entry_dict.pop("_state")
        dh_target_population_entry_dict.pop("id")
        dh_target_population_entry_dict.pop("session_id")
        self.assertDictEqual(expected_target_population_entry_dict, dh_target_population_entry_dict)

    def test_individual_send_correctly(self):
        self.maxDiff = None
        self.target_population.refresh_from_db()
        task = SendTPToDatahubTask()
        task.send_target_population(self.target_population)
        self.individual.refresh_from_db()
        expected_individual_dict = {
            "date_of_birth": self.individual.birth_date,
            "estimated_date_of_birth": self.individual.estimated_birth_date,
            "family_name": self.individual.family_name,
            "full_name": self.individual.full_name,
            "given_name": self.individual.given_name,
            "household_mis_id": self.individual.household.id,
            "marital_status": self.individual.marital_status,
            "middle_name": self.individual.middle_name,
            "mis_id": self.individual.id,
            "phone_number": str(self.individual.phone_no),
            "pregnant": None,
            "relationship": self.individual.relationship,
            "sanction_list_confirmed_match": self.individual.sanction_list_confirmed_match,
            "sex": self.individual.sex,
            "status": self.individual.status,
            "unhcr_id": "UN-TEST",
            "unicef_id": self.individual.unicef_id,
        }
        dh_expected_individual_dict = dh_models.Individual.objects.first().__dict__
        dh_expected_individual_dict.pop("_state")
        dh_expected_individual_dict.pop("id")
        dh_expected_individual_dict.pop("session_id")
        self.assertDictEqual(expected_individual_dict, dh_expected_individual_dict)

    def test_household_send_correctly(self):
        task = SendTPToDatahubTask()
        self.target_population.refresh_from_db()
        self.target_population.refresh_stats()
        self.target_population.save()
        task.send_target_population(self.target_population)
        self.household.refresh_from_db()
        expected_household_dict = {
            "address": self.household.address,
            "admin1": str(self.household.admin1),
            "admin2": str(self.household.admin2),
            "country": "POL",
            "form_number": None,
            "household_size": 1,
            "mis_id": self.household.id,
            "registration_date": self.household.last_registration_date.date(),
            "residence_status": self.household.residence_status,
            "status": self.household.status,
            "unhcr_id": self.household.unhcr_id,
            "unicef_id": self.household.unicef_id,
            "village": self.household.village,
        }
        dh_expected_household_dict = dh_models.Household.objects.first().__dict__
        dh_expected_household_dict.pop("_state")
        dh_expected_household_dict.pop("id")
        dh_expected_household_dict.pop("session_id")
        self.assertDictEqual(expected_household_dict, dh_expected_household_dict)
