from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytz
from django.conf import settings
from django.core.files import File
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import IndividualFactory, HouseholdFactory
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory, PaymentFactory

from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service import XlsxPaymentPlanImportPerFspService


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
            delivered_quantity=150
        )

        hoh2 = IndividualFactory(household=None)
        household_2 = HouseholdFactory(head_of_household=hoh2)
        cls.payment_2 = PaymentFactory(
            parent=cls.payment_plan,
            unicef_id="RCPT-0060-23-0.000.002",
            household=household_2,
            entitlement_quantity=212,
            delivered_quantity=150
        )

        hoh3 = IndividualFactory(household=None)
        household_3 = HouseholdFactory(head_of_household=hoh3)
        cls.payment_3 = PaymentFactory(
            parent=cls.payment_plan,
            unicef_id="RCPT-0060-23-0.000.003",
            household=household_3,
            entitlement_quantity=212,
            delivered_quantity=150
        )

    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    @patch("hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service.timezone.now", return_value=datetime(2023, 10, 23))
    def test_sth(self, mock_time_zone, mock_exchange_rate) -> None:
        content = Path(f"{settings.PROJECT_ROOT}/apps/payment/tests/test_file/fake_import_file.xlsx").read_bytes()
        file = BytesIO(content)

        import_service = XlsxPaymentPlanImportPerFspService(self.payment_plan, file)
        import_service.open_workbook()
        import_service.validate()
        import_service.import_payment_list()

        self.payment_1.refresh_from_db()
        self.payment_2.refresh_from_db()
        self.payment_3.refresh_from_db()

        self.assertEqual(self.payment_1.delivery_date, datetime(2023, 10, 23).replace(tzinfo=utc))
        self.assertEqual(self.payment_2.delivery_date, datetime(2023, 10, 23).replace(tzinfo=utc))
        self.assertEqual(self.payment_3.delivery_date, datetime(2023, 10, 23).replace(tzinfo=utc))

        import_service = XlsxPaymentPlanImportPerFspService(self.payment_plan, file)
        import_service.open_workbook()
        import_service.validate()

        print(import_service.errors)

        self.assertEqual(1, 2)

