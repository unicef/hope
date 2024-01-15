from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest.mock import patch

from django.contrib.admin.options import get_content_type_for_model
from django.core.files.base import ContentFile

import pytz

from hct_mis_api import settings
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, FileTemp
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service import (
    XlsxPaymentPlanImportPerFspService,
)
from hct_mis_api.one_time_scripts.delivery_date_fix import delivery_date_fix


def file_without_delivery_dates() -> BytesIO:
    content = Path(
        f"{settings.PROJECT_ROOT}/apps/payment/tests/test_file/import_file_no_delivery_date.xlsx"
    ).read_bytes()
    file = BytesIO(content)
    return file


class TestFixDeliveryDate(APITestCase):
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
            household=household_1,
            entitlement_quantity=212,
            delivered_quantity=150,
            currency="PLN",
        )
        cls.payment_1.unicef_id = "RCPT-0060-23-0.000.001"
        cls.payment_1.save()

        hoh2 = IndividualFactory(household=None)
        household_2 = HouseholdFactory(head_of_household=hoh2)
        cls.payment_2 = PaymentFactory(
            parent=cls.payment_plan,
            household=household_2,
            entitlement_quantity=212,
            delivered_quantity=150,
            currency="PLN",
        )
        cls.payment_2.unicef_id = "RCPT-0060-23-0.000.002"
        cls.payment_2.save()

        hoh3 = IndividualFactory(household=None)
        household_3 = HouseholdFactory(head_of_household=hoh3)
        cls.payment_3 = PaymentFactory(
            parent=cls.payment_plan,
            household=household_3,
            entitlement_quantity=212,
            delivered_quantity=150,
            currency="PLN",
        )
        cls.payment_3.unicef_id = "RCPT-0060-23-0.000.003"
        cls.payment_3.save()

    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_fix_delivery_date(self, mock_exchange_rate: Any) -> None:
        file_no_delivery_date = file_without_delivery_dates()
        file_temp = FileTemp()
        file_temp.file.save("temp_file.xlsx", ContentFile(file_no_delivery_date.read(), "temp_file.xlsx"))
        file_temp.object_id = self.payment_plan.pk
        file_temp.content_type = get_content_type_for_model(self.payment_plan)
        file_temp.created = pytz.utc.localize(datetime(2023, 10, 23))
        file_temp.save()

        import_service = XlsxPaymentPlanImportPerFspService(self.payment_plan, file_no_delivery_date)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_payment_list()
        self.payment_1.delivery_date = None
        self.payment_1.save()
        self.payment_2.delivery_quantity = 0
        self.payment_2.save()
        delivery_date2 = self.payment_2.delivery_date
        delivery_date3 = self.payment_3.delivery_date
        delivery_date_fix()
        self.payment_1.refresh_from_db()
        self.payment_2.refresh_from_db()
        self.payment_3.refresh_from_db()
        date_now = pytz.utc.localize(datetime(2023, 10, 23))
        self.assertEqual(self.payment_1.delivery_date, date_now)
        self.assertEqual(self.payment_2.delivery_date, delivery_date2)
        self.assertEqual(self.payment_3.delivery_date, delivery_date3)
