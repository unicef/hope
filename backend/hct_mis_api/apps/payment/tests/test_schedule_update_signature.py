from datetime import datetime
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.payment.celery_tasks import (
    import_payment_plan_payment_list_per_fsp_from_xlsx,
)
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory


class TestScheduleUpdateSignature(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()
        cls.user = UserFactory.create()

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
            currency="PLN",
        )

        hoh2 = IndividualFactory(household=None)
        household_2 = HouseholdFactory(head_of_household=hoh2)
        cls.payment_2 = PaymentFactory(
            parent=cls.payment_plan,
            unicef_id="RCPT-0060-23-0.000.002",
            household=household_2,
            entitlement_quantity=212,
            delivered_quantity=150,
            currency="PLN",
        )

        hoh3 = IndividualFactory(household=None)
        household_3 = HouseholdFactory(head_of_household=hoh3)
        cls.payment_3 = PaymentFactory(
            parent=cls.payment_plan,
            unicef_id="RCPT-0060-23-0.000.003",
            household=household_3,
            entitlement_quantity=212,
            delivered_quantity=150,
            currency="PLN",
        )

        content = Path(f"{settings.PROJECT_ROOT}/apps/payment/tests/test_file/import_file_one_record.xlsx").read_bytes()
        cls.file = FileTemp.objects.create(
            object_id=cls.payment_plan.pk,
            content_type=get_content_type_for_model(cls.payment_plan),
            created_by=cls.user,
            file=File(BytesIO(content), name="test_file.xlsx"),
        )

    @patch("hct_mis_api.apps.payment.celery_tasks.update_payments_signature.delay")
    def test_schedule_update_signature(self, celery_mock: MagicMock) -> None:
        with self.captureOnCommitCallbacks(execute=True):
            result = import_payment_plan_payment_list_per_fsp_from_xlsx.run(self.payment_plan.id, self.file.id)
        self.assertTrue(result)
        celery_mock.assert_called_once_with(self.payment_plan.id)
