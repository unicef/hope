import hashlib
from typing import Any
from unittest import mock

from django.conf import settings
from django.utils import timezone

from freezegun import freeze_time
from pytz import utc

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.payment.celery_tasks import prepare_payment_plan_task
from hct_mis_api.apps.payment.models import DeliveryMechanism, Payment, PaymentPlan
from hct_mis_api.apps.payment.services.payment_household_snapshot_service import (
    create_payment_plan_snapshot_data,
)
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.program.models import Program
from tests.extras.test_utils.factories.account import UserFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.household import (
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
)
from tests.extras.test_utils.factories.payment import (
    AccountFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from tests.extras.test_utils.factories.program import ProgramFactory


class TestPaymentSignature(APITestCase):
    databases = ("default",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        generate_delivery_mechanisms()
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
        pp: PaymentPlan = PaymentPlanFactory(status=PaymentPlan.Status.OPEN, created_by=self.user)
        (payment,) = PaymentFactory.create_batch(1, parent=pp)
        create_payment_plan_snapshot_data(pp)
        payment.refresh_from_db()
        payment.save()
        self.assertEqual(payment.signature_hash, self.calculate_hash_manually(payment))

    def test_bulk_update(self) -> None:
        pp: PaymentPlan = PaymentPlanFactory(status=PaymentPlan.Status.OPEN, created_by=self.user)
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
        pp: PaymentPlan = PaymentPlanFactory(status=PaymentPlan.Status.OPEN, created_by=self.user)

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
        program = ProgramFactory(
            status=Program.ACTIVE,
            start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
            cycle__start_date=timezone.datetime(2021, 10, 10, tzinfo=utc).date(),
            cycle__end_date=timezone.datetime(2021, 12, 10, tzinfo=utc).date(),
        )

        hoh1 = IndividualFactory(household=None, program=program)
        hoh2 = IndividualFactory(household=None, program=program)
        hh1 = HouseholdFactory(head_of_household=hoh1, program=program)
        hh2 = HouseholdFactory(head_of_household=hoh2, program=program)
        hoh1.household = hh1
        hoh1.save()
        hoh2.household = hh2
        hoh2.save()
        IndividualRoleInHouseholdFactory(household=hh1, individual=hoh1, role=ROLE_PRIMARY)
        IndividualRoleInHouseholdFactory(household=hh2, individual=hoh2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(4, household=hh1)

        dm_cash = DeliveryMechanism.objects.get(code="cash")

        for ind in [hoh1, hoh2]:
            AccountFactory(individual=ind)

        program_cycle = program.cycles.first()
        program_cycle_id = self.id_to_base64(program_cycle.id, "ProgramCycleNode")

        fsp = FinancialServiceProviderFactory()

        targeting_criteria = {
            "flag_exclude_if_active_adjudication_ticket": False,
            "flag_exclude_if_on_sanction_list": False,
            "rules": [
                {
                    "collectors_filters_blocks": [],
                    "household_filters_blocks": [],
                    "household_ids": f"{hh1.unicef_id}, {hh2.unicef_id}",
                    "individual_ids": "",
                    "individuals_filters_blocks": [],
                }
            ],
        }

        input_data = dict(
            business_area_slug="afghanistan",
            name="paymentPlanName",
            program_cycle_id=program_cycle_id,
            targeting_criteria=targeting_criteria,
            excluded_ids="TEST_INVALID_ID_01, TEST_INVALID_ID_02",
            fsp_id=encode_id_base64(fsp.id, "FinancialServiceProvider"),
            delivery_mechanism_code=dm_cash.code,
        )

        with mock.patch("hct_mis_api.apps.payment.services.payment_plan_services.prepare_payment_plan_task"):
            pp = PaymentPlanService.create(
                input_data=input_data, user=self.user, business_area_slug=self.business_area.slug
            )

        pp.refresh_from_db()
        self.assertEqual(pp.build_status, PaymentPlan.BuildStatus.BUILD_STATUS_PENDING)

        prepare_payment_plan_task(str(pp.id))
        pp.refresh_from_db()

        self.assertEqual(pp.build_status, PaymentPlan.BuildStatus.BUILD_STATUS_OK)

        payment1 = pp.payment_items.all()[0]
        payment2 = pp.payment_items.all()[1]
        self.assertEqual(payment1.signature_hash, self.calculate_hash_manually(payment1))
        self.assertEqual(payment2.signature_hash, self.calculate_hash_manually(payment2))
