from unittest.mock import patch

from django.test import TestCase
from django.db.utils import IntegrityError

from hct_mis_api.apps.household.fixtures import IndividualFactory, HouseholdFactory
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory, PaymentFactory
from hct_mis_api.apps.payment.models import PaymentPlan, Payment
from hct_mis_api.apps.core.models import BusinessArea

from hct_mis_api.apps.core.fixtures import create_afghanistan

from datetime import datetime
from dateutil.relativedelta import relativedelta


class TestPaymentPlanModel(TestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

    def test_create(self):
        pp = PaymentPlanFactory()
        self.assertIsInstance(pp, PaymentPlan)

    def test_update_population_count_fields(self):
        pp = PaymentPlanFactory()
        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        p1 = PaymentFactory(payment_plan=pp, excluded=False, household=hh1, head_of_household=hoh1)
        p2 = PaymentFactory(payment_plan=pp, excluded=False, household=hh2, head_of_household=hoh2)

        female_child = IndividualFactory(
            household=hh1, sex="FEMALE", birth_date=datetime.now().date() - relativedelta(years=5)
        )
        male_child = IndividualFactory(
            household=hh1, sex="MALE", birth_date=datetime.now().date() - relativedelta(years=5)
        )
        female_adult = IndividualFactory(
            household=hh2, sex="FEMALE", birth_date=datetime.now().date() - relativedelta(years=20)
        )
        male_adult = IndividualFactory(
            household=hh2, sex="MALE", birth_date=datetime.now().date() - relativedelta(years=20)
        )

        pp.update_population_count_fields()

        pp.refresh_from_db()
        self.assertEqual(pp.female_children_count, 1)
        self.assertEqual(pp.male_children_count, 1)
        self.assertEqual(pp.female_adults_count, 1)
        self.assertEqual(pp.male_adults_count, 1)
        self.assertEqual(pp.total_households_count, 2)
        self.assertEqual(pp.total_individuals_count, 4)

    @patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_update_money_fields(self, get_exchange_rate_mock):
        pp = PaymentPlanFactory()
        p1 = PaymentFactory(
            payment_plan=pp,
            excluded=False,
            entitlement_quantity=100.00,
            entitlement_quantity_usd=200.00,
            delivered_quantity=50.00,
            delivered_quantity_usd=100.00,
        )
        p2 = PaymentFactory(
            payment_plan=pp,
            excluded=False,
            entitlement_quantity=100.00,
            entitlement_quantity_usd=200.00,
            delivered_quantity=50.00,
            delivered_quantity_usd=100.00,
        )

        pp.update_money_fields()

        pp.refresh_from_db()
        self.assertEqual(pp.exchange_rate, 2.0)
        self.assertEqual(pp.total_entitled_quantity, 200.00)
        self.assertEqual(pp.total_entitled_quantity_usd, 400.00)
        self.assertEqual(pp.total_delivered_quantity, 100.00)
        self.assertEqual(pp.total_delivered_quantity_usd, 200.00)
        self.assertEqual(pp.total_undelivered_quantity, 100.00)
        self.assertEqual(pp.total_undelivered_quantity_usd, 200.00)

    def test_all_active_payments(self):
        pp = PaymentPlanFactory()
        p1 = PaymentFactory(payment_plan=pp, excluded=False)
        p2 = PaymentFactory(payment_plan=pp, excluded=True)

        pp.refresh_from_db()
        self.assertEqual(pp.all_active_payments.count(), 1)

    def test_can_be_locked(self):
        pp1 = PaymentPlanFactory()
        self.assertEqual(pp1.can_be_locked, False)

        # create hard conflicted payment
        pp1_conflicted = PaymentPlanFactory(
            start_date=pp1.start_date, end_date=pp1.end_date, status=PaymentPlan.Status.LOCKED
        )
        p1 = PaymentFactory(payment_plan=pp1, excluded=False)
        p1_conflicted = PaymentFactory(payment_plan=pp1_conflicted, household=p1.household, excluded=False)
        self.assertEqual(pp1.payments.filter(payment_plan_hard_conflicted=True).count(), 1)
        self.assertEqual(pp1.can_be_locked, False)

        # create not conflicted payment
        p2 = PaymentFactory(payment_plan=pp1, excluded=False)
        self.assertEqual(pp1.can_be_locked, True)


class TestPaymentModel(TestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

    def test_create(self):
        p1 = PaymentFactory()
        self.assertIsInstance(p1, Payment)

    def test_unique_together(self):
        pp = PaymentPlanFactory()
        hoh1 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        p1 = PaymentFactory(payment_plan=pp, excluded=False, household=hh1)
        with self.assertRaises(IntegrityError):
            p2 = PaymentFactory(payment_plan=pp, excluded=False, household=hh1)
