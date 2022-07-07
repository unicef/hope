from django.utils import timezone

from django.core.management import call_command
from django.test import TestCase

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.erp_datahub.fixtures import FundsCommitmentFactory
from hct_mis_api.apps.erp_datahub.models import DownPayment
from hct_mis_api.apps.erp_datahub.tasks.sync_to_mis_datahub import SyncToMisDatahubTask
from hct_mis_api.apps.mis_datahub import models as mis_models


class TestSyncToMisDatahubTask(TestCase):
    databases = "__all__"
    bosnia_and_herzegovina = None
    bosnia = None
    herzegovina = None

    funds_commitment_1 = None
    funds_commitment_2 = None

    @classmethod
    def _prepare_business_areas(cls):
        call_command("loadbusinessareas")
        cls.bosnia_and_herzegovina = BusinessArea.objects.get(code="0530")
        cls.bosnia = BusinessArea(
            code="0531",
            name="Bosnia",
            long_name="Bosnia",
            region_name="ECAR",
            slug="bosnia",
            parent=cls.bosnia_and_herzegovina,
        )
        cls.herzegovina = BusinessArea(
            code="0532",
            name="Herzegovina",
            long_name="Herzegovina",
            region_name="ECAR",
            slug="herzegovina",
            parent=cls.bosnia_and_herzegovina,
        )
        cls.bosnia.save()
        cls.herzegovina.save()

    @classmethod
    def setUpTestData(cls):
        cls._prepare_business_areas()

    def test_dont_sync_parent(self):
        funds_commitment = FundsCommitmentFactory.create(
            business_area=self.bosnia_and_herzegovina.code,
            funds_commitment_number="123456",
            total_open_amount_local=1000,
            total_open_amount_usd=2000,
        )
        down_payment = DownPayment.objects.create(
            rec_serial_number="1600000009",
            business_area=self.bosnia_and_herzegovina.code,
            down_payment_reference="2021/3210065763/001",
            total_down_payment_amount_local=1000.00,
            total_down_payment_amount_usd=1000.00,
            currency_code="USD",
            posting_date=timezone.now(),
            created_by="johniak",
        )
        task = SyncToMisDatahubTask()
        task.execute()
        funds_commitment.refresh_from_db()
        down_payment.refresh_from_db()
        self.assertEqual(funds_commitment.mis_sync_flag, False)
        self.assertEqual(down_payment.mis_sync_flag, False)
        self.assertEqual(0, mis_models.FundsCommitment.objects.count())
        self.assertEqual(0, mis_models.DownPayment.objects.count())

    def test_sync_with_set_new_business_area(self):
        funds_commitment = FundsCommitmentFactory.create(
            business_area=self.bosnia_and_herzegovina.code,
            funds_commitment_number="123456",
            total_open_amount_local=1000,
            total_open_amount_usd=2000,
            business_office_code=self.bosnia.code,
        )
        down_payment = DownPayment.objects.create(
            rec_serial_number="1600000009",
            business_area=self.bosnia_and_herzegovina.code,
            down_payment_reference="2021/3210065763/001",
            total_down_payment_amount_local=1000.00,
            total_down_payment_amount_usd=1000.00,
            currency_code="USD",
            posting_date=timezone.now(),
            created_by="johniak",
            business_office_code=self.herzegovina.code,
        )
        task = SyncToMisDatahubTask()
        task.execute()
        funds_commitment.refresh_from_db()
        down_payment.refresh_from_db()
        self.assertEqual(funds_commitment.mis_sync_flag, True)
        self.assertEqual(down_payment.mis_sync_flag, True)
        self.assertEqual(1, mis_models.FundsCommitment.objects.count())
        self.assertEqual(1, mis_models.DownPayment.objects.count())

    def test_sync_normal(self):
        funds_commitment = FundsCommitmentFactory.create(
            business_area=BusinessArea.objects.first().code,
            funds_commitment_number="123456",
            total_open_amount_local=1000,
            total_open_amount_usd=2000,
        )
        down_payment = DownPayment.objects.create(
            rec_serial_number="1600000009",
            business_area=BusinessArea.objects.first().code,
            down_payment_reference="2021/3210065763/001",
            total_down_payment_amount_local=1000.00,
            total_down_payment_amount_usd=1000.00,
            currency_code="USD",
            posting_date=timezone.now(),
            created_by="johniak",
        )
        task = SyncToMisDatahubTask()
        task.execute()
        funds_commitment.refresh_from_db()
        down_payment.refresh_from_db()
        self.assertEqual(funds_commitment.mis_sync_flag, True)
        self.assertEqual(down_payment.mis_sync_flag, True)
        self.assertEqual(1, mis_models.FundsCommitment.objects.count())
        self.assertEqual(1, mis_models.DownPayment.objects.count())

    def test_dont_sync_with_set_new_business_area_already_synced(self):
        funds_commitment = FundsCommitmentFactory.create(
            business_area=self.bosnia_and_herzegovina.code,
            funds_commitment_number="123456",
            total_open_amount_local=1000,
            total_open_amount_usd=2000,
            business_office_code=self.bosnia.code,
            mis_sync_flag=True,
        )
        down_payment = DownPayment.objects.create(
            rec_serial_number="1600000009",
            business_area=self.bosnia_and_herzegovina.code,
            down_payment_reference="2021/3210065763/001",
            total_down_payment_amount_local=1000.00,
            total_down_payment_amount_usd=1000.00,
            currency_code="USD",
            posting_date=timezone.now(),
            created_by="johniak",
            business_office_code=self.herzegovina.code,
            mis_sync_flag=True,
        )
        task = SyncToMisDatahubTask()
        task.execute()
        funds_commitment.refresh_from_db()
        down_payment.refresh_from_db()
        self.assertEqual(funds_commitment.mis_sync_flag, True)
        self.assertEqual(down_payment.mis_sync_flag, True)
        self.assertEqual(0, mis_models.FundsCommitment.objects.count())
        self.assertEqual(0, mis_models.DownPayment.objects.count())

    def test_dont_sync_normal_already_synced(self):
        funds_commitment = FundsCommitmentFactory.create(
            business_area=BusinessArea.objects.first().code,
            funds_commitment_number="123456",
            total_open_amount_local=1000,
            total_open_amount_usd=2000,
            mis_sync_flag=True,
        )
        down_payment = DownPayment.objects.create(
            rec_serial_number="1600000009",
            business_area=BusinessArea.objects.first().code,
            down_payment_reference="2021/3210065763/001",
            total_down_payment_amount_local=1000.00,
            total_down_payment_amount_usd=1000.00,
            currency_code="USD",
            posting_date=timezone.now(),
            created_by="johniak",
            mis_sync_flag=True,
        )
        task = SyncToMisDatahubTask()
        task.execute()
        funds_commitment.refresh_from_db()
        down_payment.refresh_from_db()
        self.assertEqual(funds_commitment.mis_sync_flag, True)
        self.assertEqual(down_payment.mis_sync_flag, True)
        self.assertEqual(0, mis_models.FundsCommitment.objects.count())
        self.assertEqual(0, mis_models.DownPayment.objects.count())
