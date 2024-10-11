import hashlib
from typing import Any
from unittest import mock

from django.conf import settings
from django.utils import timezone

from aniso8601 import parse_date
from freezegun import freeze_time
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import (
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.payment.celery_tasks import prepare_payment_plan_task
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import Payment, PaymentPlan
from hct_mis_api.apps.payment.services.payment_household_snapshot_service import (
    create_payment_plan_snapshot_data,
)
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import TargetPopulation


class TestPaymentSignature(APITestCase):
    databases = ("default",)

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()

    def calculate_hash_manually(self, payment: Payment) -> str:
        sha1 = hashlib.sha1()
        sha1.update(settings.SECRET_KEY.encode("utf-8"))
        sha1.update(str(payment.parent_id).encode("utf-8"))
        sha1.update(str(payment.conflicted).encode("utf-8"))
        sha1.update(str(payment.excluded).encode("utf-8"))
        sha1.update(str(payment.entitlement_date).encode("utf-8"))
        sha1.update(str(payment.financial_service_provider_id).encode("utf-8"))
        sha1.update(str(payment.collector_id).encode("utf-8"))
        sha1.update(str(payment.source_payment_id).encode("utf-8"))
        sha1.update(str(payment.is_follow_up).encode("utf-8"))
        sha1.update(str(payment.reason_for_unsuccessful_payment).encode("utf-8"))
        sha1.update(str(payment.program_id).encode("utf-8"))
        sha1.update(str(payment.order_number).encode("utf-8"))
        sha1.update(str(payment.token_number).encode("utf-8"))
        sha1.update(str(payment.household_snapshot.snapshot_data).encode("utf-8"))
        sha1.update(str(payment.business_area_id).encode("utf-8"))
        sha1.update(str(payment.status).encode("utf-8"))
        sha1.update(str(payment.status_date).encode("utf-8"))
        sha1.update(str(payment.household_id).encode("utf-8"))
        sha1.update(str(payment.head_of_household_id).encode("utf-8"))
        sha1.update(str(payment.delivery_type).encode("utf-8"))
        sha1.update(str(payment.currency).encode("utf-8"))
        sha1.update(str(payment.entitlement_quantity).encode("utf-8"))
        sha1.update(str(payment.entitlement_quantity_usd).encode("utf-8"))
        sha1.update(str(payment.delivered_quantity).encode("utf-8"))
        sha1.update(str(payment.delivered_quantity_usd).encode("utf-8"))
        sha1.update(str(payment.delivery_date).encode("utf-8"))
        sha1.update(str(payment.transaction_reference_id).encode("utf-8"))
        return sha1.hexdigest()

    def test_payment_single_signature(self) -> None:
        pp: PaymentPlan = PaymentPlanFactory(status=PaymentPlan.Status.OPEN)
        (payment,) = PaymentFactory.create_batch(1, parent=pp)
        create_payment_plan_snapshot_data(pp)
        payment.refresh_from_db()
        payment.save()
        self.assertEqual(payment.signature_hash, self.calculate_hash_manually(payment))

    def test_bulk_update(self) -> None:
        pp: PaymentPlan = PaymentPlanFactory(status=PaymentPlan.Status.OPEN)
        (payment,) = PaymentFactory.create_batch(1, parent=pp)
        create_payment_plan_snapshot_data(pp)
        payment.refresh_from_db()
        payment.save()
        old_signature = self.calculate_hash_manually(payment)
        self.assertEqual(payment.signature_hash, old_signature)
        payment.entitlement_quantity = 21
        Payment.signature_manager.bulk_update_with_signature([payment], ["entitlement_quantity"])
        payment.refresh_from_db()
        self.assertNotEqual(payment.signature_hash, old_signature)
        self.assertEqual(payment.signature_hash, self.calculate_hash_manually(payment))

    def test_bulk_create(self) -> None:
        pp: PaymentPlan = PaymentPlanFactory(status=PaymentPlan.Status.OPEN)

        (payment,) = PaymentFactory.create_batch(1, parent=pp)
        creation_dict = payment.__dict__.copy()
        creation_dict.pop("id")
        creation_dict.pop("_state")
        Payment.all_objects.filter(id=payment.id).delete()
        (payment,) = Payment.signature_manager.bulk_create_with_signature([Payment(**creation_dict)])
        create_payment_plan_snapshot_data(pp)
        payment.refresh_from_db()
        self.assertEqual(payment.signature_hash, self.calculate_hash_manually(payment))

    @freeze_time("2020-10-10")
    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    def test_signature_after_prepare_payment_plan(self, get_exchange_rate_mock: Any) -> None:
        targeting = TargetPopulationFactory()

        self.business_area.is_payment_plan_applicable = True
        self.business_area.save()

        targeting.status = TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE
        targeting.program = ProgramFactory(
            status=Program.ACTIVE,
            start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
            cycle__start_date=timezone.datetime(2021, 10, 10, tzinfo=utc).date(),
            cycle__end_date=timezone.datetime(2021, 12, 10, tzinfo=utc).date(),
        )

        hoh1 = IndividualFactory(household=None)
        hoh2 = IndividualFactory(household=None)
        hh1 = HouseholdFactory(head_of_household=hoh1)
        hh2 = HouseholdFactory(head_of_household=hoh2)
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)

        targeting.program_cycle = targeting.program.cycles.first()
        targeting.households.set([hh1, hh2])
        targeting.save()

        input_data = dict(
            business_area_slug="afghanistan",
            targeting_id=self.id_to_base64(targeting.id, "Targeting"),
            dispersion_start_date=parse_date("2020-09-10"),
            dispersion_end_date=parse_date("2020-11-10"),
            currency="USD",
            name="paymentPlanName",
        )

        with mock.patch("hct_mis_api.apps.payment.services.payment_plan_services.prepare_payment_plan_task"):
            pp = PaymentPlanService.create(input_data=input_data, user=self.user)

        prepare_payment_plan_task(pp.id)
        pp.refresh_from_db()
        payment1 = pp.payment_items.all()[0]
        payment2 = pp.payment_items.all()[1]
        self.assertEqual(payment1.signature_hash, self.calculate_hash_manually(payment1))
        self.assertEqual(payment2.signature_hash, self.calculate_hash_manually(payment2))
