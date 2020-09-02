import uuid
from datetime import timedelta

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from cash_assist_datahub.models import CashPlan as DHCashPlan, PaymentRecord as DHPaymentRecord, \
    TargetPopulation as DHTargetPopulation, ServiceProvider as DHServiceProvider, Programme as DHProgram
from cash_assist_datahub.models import Session
from cash_assist_datahub.tasks.pull_from_datahub import PullFromDatahubTask
from core.models import BusinessArea
from household.fixtures import (
    create_household,
)
from payment.models import PaymentRecord
from program.models import Program, CashPlan
from targeting.models import TargetPopulation


class TestPullDataFromDatahub(TestCase):
    multi_db = True
    program = None
    target_population = None
    dh_cash_plan1 = None
    dh_cash_plan2 = None
    household = None

    @staticmethod
    def _pre_test_commands():
        call_command("loadbusinessareas")
        # call_command("generatedocumenttypes")
        # business_area_with_data_sharing = BusinessArea.objects.first()
        # business_area_with_data_sharing.has_data_sharing_agreement = True
        # business_area_with_data_sharing.save()

    @classmethod
    def _setup_in_app_data(cls):
        target_population = TargetPopulation()
        target_population.name = "Test TP"
        target_population.status = TargetPopulation.STATUS_FINALIZED
        target_population.save()

        program = Program()
        program.name = "Test Program"
        program.status = Program.ACTIVE
        program.start_date = timezone.now()
        program.end_date = timezone.now() + timedelta(days=10)
        program.description = "Test Program description"
        program.business_area = BusinessArea.objects.first()
        program.budget = 1000
        program.frequency_of_payments = Program.REGULAR
        program.sector = Program.CHILD_PROTECTION
        program.scope = Program.SCOPE_UNICEF
        program.cash_plus = True
        program.population_goal = 1000
        program.administrative_areas_of_implementation = "Test something"
        program.individual_data_needed = True
        program.save()
        (household, individuals) = create_household(household_args={"size": 1})
        cls.household = household
        cls.target_population = target_population
        cls.program = program

    @classmethod
    def _setup_datahub_data(cls):
        session = Session()
        session.status = Session.STATUS_READY
        session.save()
        cls.session = session
        print(cls.session)
        print(DHProgram.objects.filter(session=session))
        dh_target_population = DHTargetPopulation()
        dh_target_population.session = session
        dh_target_population.ca_id = "123-TP-12345"
        dh_target_population.ca_hash_id = uuid.uuid4()
        dh_target_population.mis_id = cls.target_population.id
        dh_target_population.save()
        cls.dh_target_population = dh_target_population
        # dh_program = DHProgram()
        # dh_program.session = session
        # dh_program.mis_id = cls.program.id
        # dh_program.ca_id = "123-PRG-12345"
        # dh_program.ca_hash_id = uuid.uuid4()
        # dh_program.save()

        dh_cash_plan1 = DHCashPlan()
        dh_cash_plan1.session = session
        dh_cash_plan1.business_area = BusinessArea.objects.first().code
        dh_cash_plan1.cash_plan_id = "123-CSH-12345"
        dh_cash_plan1.cash_plan_hash_id = uuid.uuid4()
        dh_cash_plan1.status = CashPlan.DISTRIBUTION_COMPLETED
        dh_cash_plan1.status_date = timezone.now()
        dh_cash_plan1.name = "Test CashAssist CashPlan"
        dh_cash_plan1.distribution_level = "Test Distribution Level"
        dh_cash_plan1.start_date = timezone.now()
        dh_cash_plan1.end_date = timezone.now() + timedelta(days=10)
        dh_cash_plan1.dispersion_date = timezone.now() + timedelta(days=2)
        dh_cash_plan1.coverage_duration = 4
        dh_cash_plan1.coverage_unit = "days"
        dh_cash_plan1.comments = "Test Comment"
        dh_cash_plan1.program_mis_id = cls.program.id
        dh_cash_plan1.delivery_type = "CARD"
        dh_cash_plan1.assistance_measurement = "TEST measurement"
        dh_cash_plan1.assistance_through = "Test Bank"
        dh_cash_plan1.vision_id = "random-csh-vision-id"
        dh_cash_plan1.funds_commitment = "123"
        dh_cash_plan1.down_payment = "100"
        dh_cash_plan1.validation_alerts_count = 0
        dh_cash_plan1.total_persons_covered = 1
        dh_cash_plan1.total_persons_covered_revised = 1
        dh_cash_plan1.payment_records_count = 1
        dh_cash_plan1.total_entitled_quantity = 10
        dh_cash_plan1.total_entitled_quantity_revised = 10
        dh_cash_plan1.total_delivered_quantity = 10
        dh_cash_plan1.total_undelivered_quantity = 0
        dh_cash_plan1.save()
        cls.dh_cash_plan1 = dh_cash_plan1

        dh_service_provider = DHServiceProvider()
        dh_service_provider.session = session
        dh_service_provider.business_area = BusinessArea.objects.first().code
        dh_service_provider.ca_id = "123-SP-12345"
        dh_service_provider.full_name = "SOME TEST BANK"
        dh_service_provider.short_name = "STB"
        dh_service_provider.country = "POL"
        dh_service_provider.vision_id = "random-sp-vision-id"
        cls.dh_service_provider = dh_service_provider

        dh_payment_record = DHPaymentRecord()
        dh_payment_record.session = session
        dh_payment_record.business_area = BusinessArea.objects.first().code
        dh_payment_record.status = PaymentRecord.STATUS_SUCCESS
        dh_payment_record.status_date = timezone.now()
        dh_payment_record.ca_id = "123-PR-12345"
        dh_payment_record.ca_hash_id = uuid.uuid4()
        dh_payment_record.registration_ca_id = "123-RDI-12345"
        dh_payment_record.household_mis_id = cls.household.id
        dh_payment_record.head_of_household_mis_id = cls.household.head_of_household.id
        dh_payment_record.full_name = cls.household.head_of_household.full_name
        dh_payment_record.total_persons_covered = 1
        dh_payment_record.distribution_modality = "Test distribution_modality"
        dh_payment_record.target_population_mis_id = cls.target_population.id
        dh_payment_record.target_population_cash_assist_id = "123-TP-12345"
        dh_payment_record.entitlement_card_number = "ASH12345678"
        dh_payment_record.entitlement_card_status = PaymentRecord.ENTITLEMENT_CARD_STATUS_ACTIVE
        dh_payment_record.entitlement_card_issue_date = timezone.now() - timedelta(days=10)
        dh_payment_record.delivery_type = PaymentRecord.DELIVERY_TYPE_CASH
        dh_payment_record.currency = "USD"
        dh_payment_record.entitlement_quantity = 10
        dh_payment_record.delivered_quantity = 10
        dh_payment_record.delivery_date = timezone.now() - timedelta(days=1)
        dh_payment_record.service_provider_ca_id = dh_service_provider.ca_id
        dh_payment_record.transaction_reference_id = "12345"
        dh_payment_record.vision_id = "random-pr-vision-id"
        cls.dh_payment_record = dh_payment_record

    @classmethod
    def setUpTestData(cls):
        import ipdb;ipdb.set_trace()
        cls._pre_test_commands()
        cls._setup_in_app_data()
        cls._setup_datahub_data()

    def test_pull_data(self):
        task = PullFromDatahubTask()
        task.execute()
        session = self.session
        session.refresh_from_db()
        self.assertEqual(session.status, Session.STATUS_COMPLETED)
