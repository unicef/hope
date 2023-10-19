import hashlib
from datetime import timedelta
from typing import Any
from unittest import mock

from django.conf import settings
from django.utils import timezone

from aniso8601 import parse_date
from freezegun import freeze_time
from graphql import GraphQLError
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import (
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.payment.celery_tasks import (
    prepare_follow_up_payment_plan_task,
    prepare_payment_plan_task,
)
from hct_mis_api.apps.payment.fixtures import PaymentFactory, PaymentPlanFactory
from hct_mis_api.apps.payment.models import Payment, PaymentPlan
from hct_mis_api.apps.payment.services.payment_household_snapshot_service import create_payment_plan_snapshot_data
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.targeting.models import TargetPopulation


class TestPaymentPlanServices(APITestCase):
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

    def test_payment_single_signature(self):
        pp: PaymentPlan = PaymentPlanFactory(status=PaymentPlan.Status.OPEN)
        (payment,) = PaymentFactory.create_batch(1, parent=pp)
        create_payment_plan_snapshot_data(pp)
        payment.refresh_from_db()
        payment.save()
        self.assertEqual(payment.signature_hash, self.calculate_hash_manually(payment))

    def test_bulk_update(self):
        pp: PaymentPlan = PaymentPlanFactory(status=PaymentPlan.Status.OPEN)
        (payment,) = PaymentFactory.create_batch(1, parent=pp)
        create_payment_plan_snapshot_data(pp)
        payment.refresh_from_db()
        payment.save()
        old_signature = self.calculate_hash_manually(payment)
        self.assertEqual(payment.signature_hash, old_signature)
        payment.entitlement_quantity = 21
        Payment.signature_manager.bulk_update_with_signature([payment], ['entitlement_quantity'])
        payment.refresh_from_db()
        self.assertNotEqual(payment.signature_hash, old_signature)
        self.assertEqual(payment.signature_hash, self.calculate_hash_manually(payment))

    def test_bulk_create(self):
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

