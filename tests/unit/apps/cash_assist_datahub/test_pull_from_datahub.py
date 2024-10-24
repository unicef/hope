import os
import uuid
from datetime import timedelta
from typing import Any
from unittest import mock
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

import requests_mock
from parameterized import parameterized

from hct_mis_api.apps.cash_assist_datahub.models import CashPlan as DHCashPlan
from hct_mis_api.apps.cash_assist_datahub.models import PaymentRecord as DHPaymentRecord
from hct_mis_api.apps.cash_assist_datahub.models import Programme as DHProgram
from hct_mis_api.apps.cash_assist_datahub.models import (
    ServiceProvider as DHServiceProvider,
)
from hct_mis_api.apps.cash_assist_datahub.models import Session
from hct_mis_api.apps.cash_assist_datahub.models import (
    TargetPopulation as DHTargetPopulation,
)
from hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub import (
    PullFromDatahubTask,
)
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from hct_mis_api.apps.payment.fixtures import generate_delivery_mechanisms
from hct_mis_api.apps.payment.models import (
    CashPlan,
    DeliveryMechanism,
    PaymentRecord,
    ServiceProvider,
)
from hct_mis_api.apps.program.fixtures import (
    ProgramFactory,
    get_program_with_dct_type_and_name,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import TargetPopulation
from tests.unit.apps.core.test_exchange_rates import EXCHANGE_RATES_WITH_HISTORICAL_DATA


class DummyExchangeRates:
    pass


@mock.patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "TEST_API_KEY"})
class TestPullDataFromDatahub(TestCase):
    databases = "__all__"
    program = None
    target_population = None
    dh_cash_plan1 = None
    dh_cash_plan2 = None
    household = None

    @classmethod
    def _pre_test_commands(cls) -> None:
        cls.business_area = create_afghanistan()
        cls.program = get_program_with_dct_type_and_name()
        call_command("loadcountries")
        call_command("loadcountrycodes")

    @classmethod
    def _setup_in_app_data(cls) -> None:
        target_population = TargetPopulation.objects.create(
            name="Test TP",
            status=TargetPopulation.STATUS_PROCESSING,
            program=cls.program,
            business_area=cls.business_area,
            program_cycle=cls.program.cycles.first(),
        )

        program = ProgramFactory(
            name="Test Program",
            status=Program.ACTIVE,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=10),
            description="Test Program description",
            business_area=BusinessArea.objects.first(),
            budget=1000,
            frequency_of_payments=Program.REGULAR,
            sector=Program.CHILD_PROTECTION,
            scope=Program.SCOPE_UNICEF,
            cash_plus=True,
            population_goal=1000,
            administrative_areas_of_implementation="Test something",
        )
        (household, individuals) = create_household(household_args={"size": 1})
        cls.household = household
        cls.target_population = target_population
        cls.program = program
        generate_delivery_mechanisms()

    @classmethod
    def _setup_datahub_data(cls) -> None:
        session = Session()
        session.business_area = BusinessArea.objects.first().cash_assist_code
        session.status = Session.STATUS_READY
        session.save()
        cls.session = session
        dh_target_population = DHTargetPopulation()
        dh_target_population.session = session
        dh_target_population.ca_id = "123-TP-12345"
        dh_target_population.ca_hash_id = uuid.uuid4()
        dh_target_population.mis_id = cls.target_population.id
        dh_target_population.save()
        cls.dh_target_population = dh_target_population

        dh_program = DHProgram()
        dh_program.session = session
        dh_program.mis_id = cls.program.id
        dh_program.ca_id = "123-PRG-12345"
        dh_program.ca_hash_id = uuid.uuid4()
        dh_program.save()
        cls.dh_program = dh_program

        dh_service_provider = DHServiceProvider()
        dh_service_provider.session = session
        dh_service_provider.business_area = BusinessArea.objects.first().cash_assist_code
        dh_service_provider.ca_id = "123-SP-12345"
        dh_service_provider.full_name = "SOME TEST BANK"
        dh_service_provider.short_name = "STB"
        dh_service_provider.country = "POL"
        dh_service_provider.vision_id = "random-sp-vision-id"
        dh_service_provider.save()
        cls.dh_service_provider = dh_service_provider

        dh_cash_plan1 = DHCashPlan()
        dh_cash_plan1.session = session
        dh_cash_plan1.business_area = BusinessArea.objects.first().cash_assist_code
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
        dh_cash_plan1.assistance_through = dh_service_provider.ca_id
        dh_cash_plan1.vision_id = "random-csh-vision-id"
        dh_cash_plan1.funds_commitment = "123"
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

        dh_payment_record = DHPaymentRecord()
        dh_payment_record.session = session
        dh_payment_record.business_area = BusinessArea.objects.first().cash_assist_code
        dh_payment_record.status = PaymentRecord.STATUS_SUCCESS
        dh_payment_record.status_date = timezone.now()
        dh_payment_record.ca_id = "123-PR-12345"
        dh_payment_record.ca_hash_id = uuid.uuid4()
        dh_payment_record.cash_plan_ca_id = dh_cash_plan1.cash_plan_id
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
        dh_payment_record.delivery_type = DeliveryMechanismChoices.DELIVERY_TYPE_CASH
        dh_payment_record.currency = "USD"
        dh_payment_record.entitlement_quantity = 10
        dh_payment_record.delivered_quantity = 10
        dh_payment_record.delivery_date = timezone.now() - timedelta(days=1)
        dh_payment_record.service_provider_ca_id = dh_service_provider.ca_id
        dh_payment_record.transaction_reference_id = "12345"
        dh_payment_record.vision_id = "random-pr-vision-id"
        dh_payment_record.save()
        cls.dh_payment_record = dh_payment_record

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls._pre_test_commands()
        cls._setup_in_app_data()
        cls._setup_datahub_data()

    @requests_mock.Mocker()
    def test_pull_data(self, mocker: Any) -> None:
        mocker.register_uri(
            "GET",
            "https://uniapis.unicef.org/biapi/v1/exchangerates?history=yes",
            json=EXCHANGE_RATES_WITH_HISTORICAL_DATA,
        )
        task = PullFromDatahubTask()
        task.execute()
        session = self.session
        session.refresh_from_db()
        self.assertEqual(session.status, Session.STATUS_COMPLETED)
        # tp
        self.target_population.refresh_from_db()
        self.assertEqual(self.target_population.ca_id, self.dh_target_population.ca_id)
        self.assertEqual(str(self.target_population.ca_hash_id), str(self.dh_target_population.ca_hash_id))
        # program
        self.program.refresh_from_db()
        self.assertEqual(self.program.ca_id, self.dh_program.ca_id)
        self.assertEqual(str(self.program.ca_hash_id), str(self.dh_program.ca_hash_id))
        # service provider
        service_provider = ServiceProvider.objects.get(ca_id=self.dh_payment_record.service_provider_ca_id)
        self.assertEqual(service_provider.business_area.cash_assist_code, self.dh_service_provider.business_area)
        self.assertEqual(service_provider.ca_id, self.dh_service_provider.ca_id)
        self.assertEqual(service_provider.full_name, self.dh_service_provider.full_name)
        self.assertEqual(service_provider.short_name, self.dh_service_provider.short_name)
        self.assertEqual(service_provider.country, self.dh_service_provider.country)
        self.assertEqual(service_provider.vision_id, self.dh_service_provider.vision_id)
        # cash plan
        cash_plan = CashPlan.objects.get(ca_id=self.dh_cash_plan1.cash_plan_id)
        self.assertEqual(cash_plan.business_area.cash_assist_code, self.dh_cash_plan1.business_area)
        self.assertEqual(cash_plan.ca_id, self.dh_cash_plan1.cash_plan_id)
        self.assertEqual(str(cash_plan.ca_hash_id), str(self.dh_cash_plan1.cash_plan_hash_id))
        self.assertEqual(cash_plan.status, self.dh_cash_plan1.status)
        self.assertEqual(cash_plan.status_date, self.dh_cash_plan1.status_date)
        self.assertEqual(cash_plan.name, self.dh_cash_plan1.name)
        self.assertEqual(cash_plan.distribution_level, self.dh_cash_plan1.distribution_level)
        self.assertEqual(cash_plan.start_date.date(), self.dh_cash_plan1.start_date.date())
        self.assertEqual(cash_plan.end_date.date(), self.dh_cash_plan1.end_date.date())
        self.assertEqual(cash_plan.dispersion_date, self.dh_cash_plan1.dispersion_date)
        self.assertEqual(cash_plan.coverage_duration, self.dh_cash_plan1.coverage_duration)
        self.assertEqual(cash_plan.coverage_unit, self.dh_cash_plan1.coverage_unit)
        self.assertEqual(cash_plan.comments, self.dh_cash_plan1.comments)
        self.assertEqual(str(cash_plan.program_id), str(self.dh_cash_plan1.program_mis_id))
        self.assertEqual(cash_plan.delivery_type, self.dh_cash_plan1.delivery_type)
        self.assertEqual(cash_plan.assistance_measurement, self.dh_cash_plan1.assistance_measurement)
        self.assertEqual(cash_plan.assistance_through, self.dh_cash_plan1.assistance_through)
        self.assertEqual(cash_plan.vision_id, self.dh_cash_plan1.vision_id)
        self.assertEqual(cash_plan.funds_commitment, self.dh_cash_plan1.funds_commitment)
        self.assertEqual(cash_plan.down_payment, self.dh_cash_plan1.down_payment)
        self.assertEqual(cash_plan.validation_alerts_count, self.dh_cash_plan1.validation_alerts_count)
        self.assertEqual(cash_plan.total_persons_covered, self.dh_cash_plan1.total_persons_covered)
        self.assertEqual(cash_plan.total_persons_covered_revised, self.dh_cash_plan1.total_persons_covered_revised)
        self.assertEqual(cash_plan.payment_records_count, self.dh_cash_plan1.payment_records_count)
        self.assertEqual(cash_plan.total_entitled_quantity, self.dh_cash_plan1.total_entitled_quantity)
        self.assertEqual(cash_plan.total_entitled_quantity_revised, self.dh_cash_plan1.total_entitled_quantity_revised)
        self.assertEqual(cash_plan.total_delivered_quantity, self.dh_cash_plan1.total_delivered_quantity)
        self.assertEqual(cash_plan.total_undelivered_quantity, self.dh_cash_plan1.total_undelivered_quantity)
        self.assertEqual(cash_plan.service_provider.ca_id, self.dh_cash_plan1.assistance_through)

        # payment record
        payment_record = PaymentRecord.objects.get(ca_id=self.dh_payment_record.ca_id)

        self.assertEqual(payment_record.business_area.cash_assist_code, self.dh_payment_record.business_area)
        self.assertEqual(payment_record.status, self.dh_payment_record.status)
        self.assertEqual(payment_record.status_date, self.dh_payment_record.status_date)
        self.assertEqual(payment_record.ca_id, self.dh_payment_record.ca_id)
        self.assertEqual(str(payment_record.ca_hash_id), str(self.dh_payment_record.ca_hash_id))
        self.assertEqual(str(payment_record.household_id), str(self.dh_payment_record.household_mis_id))
        self.assertEqual(str(payment_record.head_of_household_id), str(self.dh_payment_record.head_of_household_mis_id))
        self.assertEqual(payment_record.full_name, self.dh_payment_record.full_name)
        self.assertEqual(payment_record.total_persons_covered, self.dh_payment_record.total_persons_covered)
        self.assertEqual(payment_record.distribution_modality, self.dh_payment_record.distribution_modality)
        self.assertEqual(str(payment_record.target_population_id), str(self.dh_payment_record.target_population_mis_id))
        self.assertEqual(payment_record.entitlement_card_number, self.dh_payment_record.entitlement_card_number)
        self.assertEqual(payment_record.entitlement_card_status, self.dh_payment_record.entitlement_card_status)
        self.assertEqual(
            payment_record.entitlement_card_issue_date, self.dh_payment_record.entitlement_card_issue_date.date()
        )
        self.assertEqual(
            payment_record.delivery_type, DeliveryMechanism.objects.get(name=self.dh_payment_record.delivery_type)
        )
        self.assertEqual(payment_record.currency, self.dh_payment_record.currency)
        self.assertEqual(payment_record.entitlement_quantity, self.dh_payment_record.entitlement_quantity)
        self.assertEqual(payment_record.delivered_quantity, self.dh_payment_record.delivered_quantity)
        self.assertEqual(payment_record.delivery_date, self.dh_payment_record.delivery_date)
        self.assertEqual(payment_record.transaction_reference_id, self.dh_payment_record.transaction_reference_id)
        self.assertEqual(payment_record.vision_id, self.dh_payment_record.vision_id)
        self.assertEqual(payment_record.service_provider_id, service_provider.id)
        self.assertEqual(payment_record.registration_ca_id, self.dh_payment_record.registration_ca_id)

        self.assertIn(self.household, self.program.households.all())
        self.household.refresh_from_db()
        self.assertEqual(self.household.total_cash_received, 10)


class TestSessionsPullDataFromDatahub(TestCase):
    databases = "__all__"
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadbusinessareas")
        call_command("loadcountrycodes")

    def test_multiple_sessions_same_ba_working(self) -> None:
        session1 = Session(status=Session.STATUS_READY, business_area=BusinessArea.objects.first().cash_assist_code)
        session1.save()
        session2 = Session(status=Session.STATUS_READY, business_area=BusinessArea.objects.first().cash_assist_code)
        session2.save()
        copy_session_mock = MagicMock()
        with patch(
            "hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub.PullFromDatahubTask.copy_session",
            copy_session_mock,
        ):
            task = PullFromDatahubTask(DummyExchangeRates())
            task.execute()
            self.assertEqual(copy_session_mock.call_count, 2)
        session1.delete()
        session2.delete()

    def test_multiple_sessions_same_ba_fail(self) -> None:
        session1 = Session(status=Session.STATUS_FAILED, business_area=BusinessArea.objects.first().cash_assist_code)
        session1.save()
        session2 = Session(status=Session.STATUS_READY, business_area=BusinessArea.objects.first().cash_assist_code)
        session2.save()
        copy_session_mock = MagicMock()
        with patch(
            "hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub.PullFromDatahubTask.copy_session",
            copy_session_mock,
        ):
            task = PullFromDatahubTask(DummyExchangeRates())
            task.execute()
            self.assertEqual(copy_session_mock.call_count, 0)
            self.assertEqual(copy_session_mock.call_args_list, [])
        session1.delete()
        session2.delete()

    def test_multiple_sessions_different_ba_run1(self) -> None:
        session1 = Session(status=Session.STATUS_FAILED, business_area=BusinessArea.objects.first().cash_assist_code)
        session1.save()
        session2 = Session(status=Session.STATUS_READY, business_area=BusinessArea.objects.first().cash_assist_code)
        session2.save()
        session3 = Session(status=Session.STATUS_READY, business_area=BusinessArea.objects.all()[3].cash_assist_code)
        session3.save()
        copy_session_mock = MagicMock()
        with patch(
            "hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub.PullFromDatahubTask.copy_session",
            copy_session_mock,
        ):
            task = PullFromDatahubTask(DummyExchangeRates())
            task.execute()
            self.assertEqual(copy_session_mock.call_count, 1)
            self.assertEqual(copy_session_mock.call_args_list[0][0][0].id, session3.id)
        session1.delete()
        session2.delete()
        session3.delete()

    @parameterized.expand(
        [
            (
                "equal",
                "AFG",
                "AFG",
            ),
            (
                "custom_code",
                "AUL",
                "AUS",
            ),
        ]
    )
    def test_country_mapping(self, _: Any, ca_code: str, expected: str) -> None:
        session = Session(status=Session.STATUS_READY, business_area=BusinessArea.objects.first().cash_assist_code)
        session.save()
        dh_service_provider = DHServiceProvider()
        dh_service_provider.session = session
        dh_service_provider.business_area = BusinessArea.objects.first().cash_assist_code
        dh_service_provider.ca_id = str(uuid.uuid4())
        dh_service_provider.full_name = "SOME TEST BANK"
        dh_service_provider.short_name = "STB"
        dh_service_provider.country = ca_code
        dh_service_provider.vision_id = "random-sp-vision-id"
        dh_service_provider.save()

        task = PullFromDatahubTask(DummyExchangeRates())
        task.copy_service_providers(session)
        service_provider = ServiceProvider.objects.filter(ca_id=dh_service_provider.ca_id).first()
        self.assertEqual(service_provider.country, expected)
