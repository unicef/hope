from decimal import Decimal

from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.erp_datahub.fixtures import FundsCommitmentFactory
from hct_mis_api.apps.erp_datahub.tasks.pull_from_erp_datahub import (
    PullFromErpDatahubTask,
)
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import PaymentRecordFactory
from hct_mis_api.apps.program.fixtures import CashPlanFactory

from unittest.mock import patch


class TestPullDataFromErpDatahub(TestCase):
    databases = "__all__"
    cash_plan_1 = None
    cash_plan_2 = None
    payment_record_1 = None
    payment_record_2 = None
    funds_commitment_1 = None
    funds_commitment_2 = None

    @staticmethod
    def _pre_test_commands():
        create_afghanistan()

    @classmethod
    def _setup_in_app_data(cls):
        (household, _) = create_household(household_args={"size": 1})

        cls.cash_plan_1 = CashPlanFactory(funds_commitment="123456", exchange_rate=None)
        cls.cash_plan_2 = CashPlanFactory(funds_commitment="654321", exchange_rate=None)
        cls.cash_plan_3 = CashPlanFactory(funds_commitment="000000", exchange_rate=None)
        cls.cash_plan_4 = CashPlanFactory(funds_commitment="111111", exchange_rate=None)

        cls.payment_record_1 = PaymentRecordFactory(
            cash_plan=cls.cash_plan_1,
            business_area=cls.cash_plan_1.business_area,
            delivered_quantity=1000,
            delivered_quantity_usd=None,
            household=household,
        )
        cls.payment_record_2 = PaymentRecordFactory(
            cash_plan=cls.cash_plan_2,
            business_area=cls.cash_plan_2.business_area,
            delivered_quantity=2000,
            delivered_quantity_usd=None,
            household=household,
        )
        cls.payment_record_3 = PaymentRecordFactory(
            cash_plan=cls.cash_plan_3,
            business_area=cls.cash_plan_3.business_area,
            delivered_quantity=3000,
            delivered_quantity_usd=None,
            household=household,
        )
        cls.payment_record_4 = PaymentRecordFactory(
            cash_plan=cls.cash_plan_4,
            business_area=cls.cash_plan_4.business_area,
            delivered_quantity=1000,
            delivered_quantity_usd=None,
            household=household,
        )

    @classmethod
    def _setup_datahub_data(cls):
        cls.funds_commitment_1 = FundsCommitmentFactory(
            funds_commitment_number="123456", total_open_amount_local=1000, total_open_amount_usd=2000
        )
        cls.funds_commitment_2 = FundsCommitmentFactory(
            funds_commitment_number="654321", total_open_amount_local=1500, total_open_amount_usd=2000
        )
        cls.funds_commitment_4 = FundsCommitmentFactory(
            funds_commitment_number="111111", total_open_amount_local=1000, total_open_amount_usd=None
        )

    @classmethod
    def setUpTestData(cls):
        cls._pre_test_commands()
        cls._setup_in_app_data()
        cls._setup_datahub_data()

    @patch("hct_mis_api.apps.erp_datahub.utils.get_exchange_rate_for_cash_plan", new=lambda *arg: 2)
    @patch("hct_mis_api.apps.erp_datahub.utils.get_payment_record_delivered_quantity_in_usd", new=lambda *arg: 2)
    def test_pull_data(self):
        task = PullFromErpDatahubTask()
        task.execute()
        self.cash_plan_1.refresh_from_db()
        self.assertEqual(self.cash_plan_1.exchange_rate, Decimal(2))
        self.cash_plan_2.refresh_from_db()
        self.assertEqual(self.cash_plan_2.exchange_rate, Decimal("2"))
        self.cash_plan_3.refresh_from_db()
        self.assertEqual(self.cash_plan_3.exchange_rate, 2)
        self.payment_record_1.refresh_from_db()
        self.assertEqual(self.payment_record_1.delivered_quantity_usd, Decimal(2.0))
        self.payment_record_2.refresh_from_db()
        self.assertEqual(self.payment_record_2.delivered_quantity_usd, Decimal("2"))
        self.payment_record_3.refresh_from_db()
        self.assertEqual(self.payment_record_3.delivered_quantity_usd, 2)
        self.cash_plan_4.refresh_from_db()
        self.assertEqual(self.cash_plan_4.exchange_rate, 2)
        self.payment_record_4.refresh_from_db()
        self.assertEqual(self.payment_record_4.delivered_quantity_usd, 2)
