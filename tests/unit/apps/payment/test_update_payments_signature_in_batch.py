from datetime import datetime

from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import Payment
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService


class TestUpdatePaymentsSignatureInBatch(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
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

    def test_number_of_queries(self) -> None:
        Payment.objects.all().update(signature_hash="")
        self.assertEqual(Payment.objects.filter(signature_hash="").count(), 3)
        self.assertEqual(Payment.objects.exclude(signature_hash="").count(), 0)
        with self.assertNumQueries(8):
            PaymentPlanService(self.payment_plan).recalculate_signatures_in_batch(2)
        self.assertEqual(Payment.objects.filter(signature_hash="").count(), 0)
        self.assertEqual(Payment.objects.exclude(signature_hash="").count(), 3)
