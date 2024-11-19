from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import patch

from django.conf import settings

import pytz
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service import (
    XlsxPaymentPlanImportPerFspService,
)


def file_without_delivery_dates() -> BytesIO:
    content = Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/import_file_no_delivery_date.xlsx").read_bytes()
    file = BytesIO(content)
    return file


def file_with_existing_delivery_dates() -> BytesIO:
    content = Path(
        f"{settings.TESTS_ROOT}/apps/payment/test_file/import_file_with_existing_delivery_date.xlsx"
    ).read_bytes()
    file = BytesIO(content)
    return file


def file_one_record() -> BytesIO:
    content = Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/import_file_one_record.xlsx").read_bytes()
    file = BytesIO(content)
    return file


def file_reference_id() -> BytesIO:
    content = Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/import_file_reference_id.xlsx").read_bytes()
    file = BytesIO(content)
    return file


class TestDeliveryDate(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        cls.payment_plan = PaymentPlanFactory(
            dispersion_start_date=datetime(2020, 8, 10).date(),
            dispersion_end_date=datetime(2020, 12, 10).date(),
        )

        hoh1 = IndividualFactory(household=None)
        household_1 = HouseholdFactory(head_of_household=hoh1)
        cls.payment_1 = PaymentFactory(
            parent=cls.payment_plan,
            unicef_id="RCPT-0060-24-0.000.001",
            household=household_1,
            entitlement_quantity=212,
            delivered_quantity=150,
            currency="PLN",
        )

        hoh2 = IndividualFactory(household=None)
        household_2 = HouseholdFactory(head_of_household=hoh2)
        cls.payment_2 = PaymentFactory(
            parent=cls.payment_plan,
            unicef_id="RCPT-0060-24-0.000.002",
            household=household_2,
            entitlement_quantity=212,
            delivered_quantity=150,
            currency="PLN",
        )

        hoh3 = IndividualFactory(household=None)
        household_3 = HouseholdFactory(head_of_household=hoh3)
        cls.payment_3 = PaymentFactory(
            parent=cls.payment_plan,
            unicef_id="RCPT-0060-24-0.000.003",
            household=household_3,
            entitlement_quantity=212,
            delivered_quantity=150,
            currency="PLN",
        )

    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    @patch(
        "hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service.timezone.now",
        return_value=datetime(2023, 10, 23).replace(tzinfo=utc),
    )
    def test_uploading_delivery_date_with_xlsx(self, mock_time_zone: Any, mock_exchange_rate: Any) -> None:
        self.payment_1.delivery_date = None
        self.payment_1.save()
        old_delivery_date2 = self.payment_2.delivery_date
        old_delivery_date3 = self.payment_3.delivery_date
        file_no_delivery_date = file_without_delivery_dates()
        self.payment_1.unicef_id = "RCPT-0060-24-0.000.001"
        self.payment_2.unicef_id = "RCPT-0060-24-0.000.002"
        self.payment_3.unicef_id = "RCPT-0060-24-0.000.003"
        self.payment_1.save()
        self.payment_2.save()
        self.payment_3.save()

        import_service = XlsxPaymentPlanImportPerFspService(self.payment_plan, file_no_delivery_date)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_payment_list()
        self.payment_1.refresh_from_db()
        self.payment_2.refresh_from_db()
        self.payment_3.refresh_from_db()
        date_now = pytz.utc.localize(datetime(2023, 10, 23))
        self.assertEqual(self.payment_1.delivery_date, date_now)
        self.assertEqual(self.payment_2.delivery_date, old_delivery_date2)
        self.assertEqual(self.payment_3.delivery_date, old_delivery_date3)

    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_uploading_xlsx_file_with_existing_dates_throws_error(self, mock_exchange_rate: Any) -> None:
        self.payment_1.delivery_date = datetime(2023, 10, 23).replace(tzinfo=utc)
        self.payment_2.delivery_date = datetime(2023, 10, 23).replace(tzinfo=utc)
        self.payment_3.delivery_date = datetime(2023, 10, 23).replace(tzinfo=utc)
        self.payment_1.save()
        self.payment_2.save()
        self.payment_3.save()

        file_existing_delivery_date = file_with_existing_delivery_dates()

        import_service = XlsxPaymentPlanImportPerFspService(self.payment_plan, file_existing_delivery_date)
        import_service.open_workbook()
        import_service.validate()

        self.assertEqual(len(import_service.errors), 1)

        error = import_service.errors[0]
        self.assertListEqual(
            [error.sheet, error.coordinates, error.message],
            [
                "Test FSP 1",
                None,
                "There aren't any updates in imported file, please add changes and try again",
            ],
        )

    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_uploading_xlsx_file_with_one_record_not_overrides_other_payments_dates(
        self, mock_exchange_rate: Any
    ) -> None:
        self.payment_1.delivery_date = datetime(2023, 12, 24).replace(tzinfo=utc)
        self.payment_2.delivery_date = datetime(2023, 12, 24).replace(tzinfo=utc)
        self.payment_3.delivery_date = datetime(2023, 12, 24).replace(tzinfo=utc)
        self.payment_1.save()
        self.payment_2.save()
        self.payment_3.save()

        file_with_one_record = file_one_record()

        import_service = XlsxPaymentPlanImportPerFspService(self.payment_plan, file_with_one_record)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_payment_list()

        self.payment_1.refresh_from_db()
        self.payment_2.refresh_from_db()
        self.payment_3.refresh_from_db()

        self.assertEqual(self.payment_1.delivery_date, datetime(2023, 5, 5).replace(tzinfo=utc))  # only this changed
        self.assertEqual(self.payment_2.delivery_date, datetime(2023, 12, 24).replace(tzinfo=utc))
        self.assertEqual(self.payment_3.delivery_date, datetime(2023, 12, 24).replace(tzinfo=utc))

    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_upload_reference_id(self, mock_exchange_rate: Any) -> None:
        pp = PaymentPlanFactory(
            dispersion_start_date=datetime(2024, 2, 10).date(),
            dispersion_end_date=datetime(2024, 12, 10).date(),
            status=PaymentPlan.Status.ACCEPTED,
        )

        payment_1 = PaymentFactory(parent=pp)
        payment_1.unicef_id = "RCPT-0060-24-0.000.665"
        payment_1.entitlement_quantity = 212  # the same value like in file
        payment_1.save()

        payment_2 = PaymentFactory(parent=pp)
        payment_2.unicef_id = "RCPT-0060-24-0.000.666"
        payment_2.entitlement_quantity = 212  # the same value like in file
        payment_2.save()

        file_with_reference_id = file_reference_id()

        import_service = XlsxPaymentPlanImportPerFspService(pp, file_with_reference_id)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_payment_list()

        payment_1.refresh_from_db()
        payment_2.refresh_from_db()

        self.assertEqual(payment_1.transaction_reference_id, "ref1")
        self.assertEqual(payment_2.transaction_reference_id, "ref2")

    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=1.0)
    def test_upload_transaction_status_blockchain_link(self, mock_exchange_rate: Any) -> None:
        pp = PaymentPlanFactory(
            dispersion_start_date=datetime(2024, 2, 10).date(),
            dispersion_end_date=datetime(2024, 12, 10).date(),
            status=PaymentPlan.Status.ACCEPTED,
        )

        payment_1 = PaymentFactory(parent=pp)
        payment_1.unicef_id = "RCPT-0060-24-0.000.665"
        payment_1.entitlement_quantity = 212  # the same value like in file
        payment_1.save()

        payment_2 = PaymentFactory(parent=pp)
        payment_2.unicef_id = "RCPT-0060-24-0.000.666"
        payment_2.entitlement_quantity = 212  # the same value like in file
        payment_2.save()

        file_with_reference_id = file_reference_id()

        import_service = XlsxPaymentPlanImportPerFspService(pp, file_with_reference_id)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_payment_list()

        payment_1.refresh_from_db(fields=["transaction_status_blockchain_link"])
        payment_2.refresh_from_db(fields=["transaction_status_blockchain_link"])

        self.assertEqual(payment_1.transaction_status_blockchain_link, "transaction_status_blockchain_link_111")
        self.assertEqual(payment_2.transaction_status_blockchain_link, "www_link")
