from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import patch

from django.conf import settings

from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service import (
    XlsxPaymentPlanImportPerFspService,
)


def file_without_delivery_dates() -> BytesIO:
    content = Path(
        f"{settings.PROJECT_ROOT}/apps/payment/tests/test_file/import_file_no_delivery_date.xlsx"
    ).read_bytes()
    file = BytesIO(content)
    return file


def file_with_existing_delivery_dates() -> BytesIO:
    content = Path(
        f"{settings.PROJECT_ROOT}/apps/payment/tests/test_file/import_file_with_existing_delivery_date.xlsx"
    ).read_bytes()
    file = BytesIO(content)
    return file


def file_one_record() -> BytesIO:
    content = Path(f"{settings.PROJECT_ROOT}/apps/payment/tests/test_file/import_file_one_record.xlsx").read_bytes()
    file = BytesIO(content)
    return file


class TestDeliveryDate(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
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
            unicef_id="RCPT-0060-23-0.000.001",
            household=household_1,
            entitlement_quantity=212,
            delivered_quantity=150,
        )

        hoh2 = IndividualFactory(household=None)
        household_2 = HouseholdFactory(head_of_household=hoh2)
        cls.payment_2 = PaymentFactory(
            parent=cls.payment_plan,
            unicef_id="RCPT-0060-23-0.000.002",
            household=household_2,
            entitlement_quantity=212,
            delivered_quantity=150,
        )

        hoh3 = IndividualFactory(household=None)
        household_3 = HouseholdFactory(head_of_household=hoh3)
        cls.payment_3 = PaymentFactory(
            parent=cls.payment_plan,
            unicef_id="RCPT-0060-23-0.000.003",
            household=household_3,
            entitlement_quantity=212,
            delivered_quantity=150,
        )

    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    @patch(
        "hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service.timezone.now",
        return_value=datetime(2023, 10, 23),
    )
    def test_uploading_delivery_date_with_xlsx(self, mock_time_zone: Any, mock_exchange_rate: Any) -> None:
        file_no_delivery_date = file_without_delivery_dates()

        import_service = XlsxPaymentPlanImportPerFspService(self.payment_plan, file_no_delivery_date)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_payment_list()

        self.payment_1.refresh_from_db()
        self.payment_2.refresh_from_db()
        self.payment_3.refresh_from_db()

        self.assertEqual(self.payment_1.delivery_date, datetime(2023, 10, 23).replace(tzinfo=utc))
        self.assertEqual(self.payment_2.delivery_date, datetime(2023, 10, 23).replace(tzinfo=utc))
        self.assertEqual(self.payment_3.delivery_date, datetime(2023, 10, 23).replace(tzinfo=utc))

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
