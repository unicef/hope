import json
from unittest.mock import patch

from django.test import TestCase
from django.db.utils import IntegrityError

from hct_mis_api.apps.household.fixtures import IndividualFactory, HouseholdFactory
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory, PaymentFactory
from hct_mis_api.apps.payment.models import PaymentPlan, Payment, PaymentChannel, GenericPayment
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

    def test_manager_annotations__pp_conflicts(self):
        pp1 = PaymentPlanFactory()

        # create hard conflicted payment
        pp2 = PaymentPlanFactory(start_date=pp1.start_date, end_date=pp1.end_date, status=PaymentPlan.Status.LOCKED)
        # create soft conflicted payments
        pp3 = PaymentPlanFactory(start_date=pp1.start_date, end_date=pp1.end_date, status=PaymentPlan.Status.OPEN)
        pp4 = PaymentPlanFactory(start_date=pp1.start_date, end_date=pp1.end_date, status=PaymentPlan.Status.OPEN)
        p1 = PaymentFactory(payment_plan=pp1, excluded=False)
        p2 = PaymentFactory(payment_plan=pp2, household=p1.household, excluded=False)
        p3 = PaymentFactory(payment_plan=pp3, household=p1.household, excluded=False)
        p4 = PaymentFactory(payment_plan=pp4, household=p1.household, excluded=False)

        for _ in [pp1, pp2, pp3, pp4, p1, p2, p3, p4]:
            _.refresh_from_db()  # update unicef_id from trigger

        p1_data = Payment.objects.filter(id=p1.id).values()[0]
        self.assertEqual(p1_data["payment_plan_hard_conflicted"], True)
        self.assertEqual(p1_data["payment_plan_soft_conflicted"], True)

        self.assertEqual(len(p1_data["payment_plan_hard_conflicted_data"]), 1)
        self.assertEqual(
            json.loads(p1_data["payment_plan_hard_conflicted_data"][0]),
            {
                "payment_id": str(p2.id),
                "payment_plan_id": str(pp2.id),
                "payment_plan_status": str(pp2.status),
                "payment_plan_start_date": pp2.start_date.strftime("%Y-%m-%d"),
                "payment_plan_end_date": pp2.end_date.strftime("%Y-%m-%d"),
                "payment_plan_unicef_id": str(pp2.unicef_id),
                "payment_unicef_id": str(p2.unicef_id),
            },
        )
        self.assertEqual(len(p1_data["payment_plan_soft_conflicted_data"]), 2)
        self.assertCountEqual(
            [json.loads(conflict_data) for conflict_data in p1_data["payment_plan_soft_conflicted_data"]],
            [
                {
                    "payment_id": str(p3.id),
                    "payment_plan_id": str(pp3.id),
                    "payment_plan_status": str(pp3.status),
                    "payment_plan_start_date": pp3.start_date.strftime("%Y-%m-%d"),
                    "payment_plan_end_date": pp3.end_date.strftime("%Y-%m-%d"),
                    "payment_plan_unicef_id": str(pp3.unicef_id),
                    "payment_unicef_id": str(p3.unicef_id),
                },
                {
                    "payment_id": str(p4.id),
                    "payment_plan_id": str(pp4.id),
                    "payment_plan_status": str(pp4.status),
                    "payment_plan_start_date": pp4.start_date.strftime("%Y-%m-%d"),
                    "payment_plan_end_date": pp4.end_date.strftime("%Y-%m-%d"),
                    "payment_plan_unicef_id": str(pp4.unicef_id),
                    "payment_unicef_id": str(p4.unicef_id),
                },
            ],
        )

    def test_manager_annotations__payment_channels(self):
        pp1 = PaymentPlanFactory()
        p1 = PaymentFactory(payment_plan=pp1, excluded=False, assigned_payment_channel=None)

        p1_data = Payment.objects.filter(id=p1.id).values()[0]
        self.assertEqual(p1_data["has_defined_payment_channel"], False)
        self.assertEqual(p1_data["has_assigned_payment_channel"], False)

        pc1 = PaymentChannel.objects.create(
            individual=p1.collector, delivery_mechanism=GenericPayment.DELIVERY_TYPE_CASH
        )
        p1.assigned_payment_channel = pc1
        p1.save()

        p1_data = Payment.objects.filter(id=p1.id).values()[0]
        self.assertEqual(p1_data["has_defined_payment_channel"], True)
        self.assertEqual(p1_data["has_assigned_payment_channel"], True)
