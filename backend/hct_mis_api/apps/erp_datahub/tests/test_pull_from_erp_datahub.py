from decimal import Decimal

from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.erp_datahub.fixtures import FundsCommitmentFactory
from hct_mis_api.apps.erp_datahub.tasks.pull_from_erp_datahub import (
    PullFromErpDatahubTask,
)
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import PaymentRecordFactory, CashPlanFactory

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
            entitlement_quantity=1000,
            entitlement_quantity_usd=None,
            delivered_quantity=1000,
            delivered_quantity_usd=None,
            household=household,
        )
        cls.payment_record_2 = PaymentRecordFactory(
            cash_plan=cls.cash_plan_2,
            business_area=cls.cash_plan_2.business_area,
            entitlement_quantity=2000,
            entitlement_quantity_usd=None,
            delivered_quantity=2000,
            delivered_quantity_usd=None,
            household=household,
        )
        cls.payment_record_3 = PaymentRecordFactory(
            cash_plan=cls.cash_plan_3,
            business_area=cls.cash_plan_3.business_area,
            entitlement_quantity=3000,
            entitlement_quantity_usd=None,
            delivered_quantity=3000,
            delivered_quantity_usd=None,
            household=household,
        )
        cls.payment_record_4 = PaymentRecordFactory(
            cash_plan=cls.cash_plan_4,
            business_area=cls.cash_plan_4.business_area,
            entitlement_quantity=1000,
            entitlement_quantity_usd=None,
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

    @patch("hct_mis_api.apps.payment.models.CashPlan.get_exchange_rate", new=lambda *args, **kwargs: 2.00)
    def test_pull_data(self):
        usd_fields = [
            "total_entitled_quantity_usd",
            "total_entitled_quantity_revised_usd",
            "total_delivered_quantity_usd",
            "total_undelivered_quantity_usd",
        ]

        task = PullFromErpDatahubTask()
        task.execute()
        self.cash_plan_1.refresh_from_db()
        self.assertEqual(self.cash_plan_1.exchange_rate, Decimal(2))
        self.assertEqual(
            self.cash_plan_1.total_entitled_quantity_usd,
            Decimal(self.cash_plan_1.total_entitled_quantity / Decimal(2)).quantize(Decimal(".01")),
        )
        self.assertEqual(
            self.cash_plan_1.total_entitled_quantity_revised_usd,
            Decimal(self.cash_plan_1.total_entitled_quantity_revised / Decimal(2)).quantize(Decimal(".01")),
        )
        self.assertEqual(
            self.cash_plan_1.total_delivered_quantity_usd,
            Decimal(self.cash_plan_1.total_delivered_quantity / Decimal(2)).quantize(Decimal(".01")),
        )
        self.assertEqual(
            self.cash_plan_1.total_undelivered_quantity_usd,
            Decimal(self.cash_plan_1.total_undelivered_quantity / Decimal(2)).quantize(Decimal(".01")),
        )
        self.cash_plan_2.refresh_from_db()
        self.assertEqual(self.cash_plan_2.exchange_rate, Decimal(2))
        self.cash_plan_3.refresh_from_db()
        self.assertEqual(self.cash_plan_3.exchange_rate, Decimal(2))
        self.payment_record_1.refresh_from_db()
        self.assertEqual(
            self.payment_record_1.delivered_quantity_usd, Decimal(self.payment_record_1.delivered_quantity / Decimal(2))
        )
        self.assertEqual(
            self.payment_record_1.entitlement_quantity_usd,
            Decimal(self.payment_record_1.entitlement_quantity / Decimal(2)),
        )
        self.payment_record_2.refresh_from_db()
        self.assertEqual(
            self.payment_record_2.delivered_quantity_usd, Decimal(self.payment_record_2.delivered_quantity / Decimal(2))
        )
        self.assertEqual(
            self.payment_record_2.entitlement_quantity_usd,
            Decimal(self.payment_record_2.entitlement_quantity / Decimal(2)),
        )
        self.payment_record_3.refresh_from_db()
        self.assertEqual(
            self.payment_record_3.delivered_quantity_usd, Decimal(self.payment_record_3.delivered_quantity / Decimal(2))
        )
        self.assertEqual(
            self.payment_record_3.entitlement_quantity_usd,
            Decimal(self.payment_record_3.entitlement_quantity / Decimal(2)),
        )
        self.cash_plan_4.refresh_from_db()
        self.assertEqual(self.cash_plan_4.exchange_rate, Decimal(2))
        self.payment_record_4.refresh_from_db()
        self.assertEqual(
            self.payment_record_4.delivered_quantity_usd, Decimal(self.payment_record_4.delivered_quantity / Decimal(2))
        )
        self.assertEqual(
            self.payment_record_4.entitlement_quantity_usd,
            Decimal(self.payment_record_4.entitlement_quantity / Decimal(2)),
        )
