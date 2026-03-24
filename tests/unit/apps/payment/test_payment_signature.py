import hashlib
from typing import Any
from unittest import mock

from django.conf import settings
from django.utils import timezone
from freezegun import freeze_time
import pytest
from pytz import utc

from extras.test_utils.factories import (
    AccountFactory,
    BusinessAreaFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.payment.celery_tasks import prepare_payment_plan_task
from hope.apps.payment.services.payment_household_snapshot_service import create_payment_plan_snapshot_data
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.models import Payment, PaymentPlan, Program

pytestmark = pytest.mark.django_db


def calculate_hash_manually(payment: Payment) -> str:
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


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user() -> Any:
    return UserFactory()


@pytest.fixture
def program(business_area: Any) -> Program:
    return ProgramFactory(
        status=Program.ACTIVE,
        start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
        end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
        business_area=business_area,
    )


@pytest.fixture
def program_cycle(program: Program) -> Any:
    return ProgramCycleFactory(
        program=program,
        start_date=timezone.datetime(2021, 10, 10, tzinfo=utc).date(),
        end_date=timezone.datetime(2021, 12, 10, tzinfo=utc).date(),
        title="Cycle Signature",
    )


@pytest.fixture
def payment_plan(user: Any, business_area: Any, program_cycle: Any) -> PaymentPlan:
    return PaymentPlanFactory(
        status=PaymentPlan.Status.OPEN,
        created_by=user,
        business_area=business_area,
        program_cycle=program_cycle,
    )


def test_payment_single_signature(payment_plan: PaymentPlan) -> None:
    (payment,) = PaymentFactory.create_batch(1, parent=payment_plan)
    create_payment_plan_snapshot_data(payment_plan)
    payment.refresh_from_db()
    payment.save()
    assert payment.signature_hash == calculate_hash_manually(payment)


def test_bulk_update(payment_plan: PaymentPlan) -> None:
    (payment,) = PaymentFactory.create_batch(1, parent=payment_plan)
    create_payment_plan_snapshot_data(payment_plan)
    payment.refresh_from_db()
    payment.save()
    old_signature = calculate_hash_manually(payment)
    assert payment.signature_hash == old_signature
    payment.entitlement_quantity = 21
    Payment.signature_manager.bulk_update_with_signature([payment], ["entitlement_quantity"])
    payment.refresh_from_db()
    assert payment.signature_hash != old_signature
    assert payment.signature_hash == calculate_hash_manually(payment)


def test_bulk_create(payment_plan: PaymentPlan) -> None:
    (payment,) = PaymentFactory.create_batch(1, parent=payment_plan)
    creation_dict = payment.__dict__.copy()
    creation_dict.pop("id")
    creation_dict.pop("_state")
    Payment.all_objects.filter(id=payment.id).delete()
    (payment,) = Payment.signature_manager.bulk_create_with_signature([Payment(**creation_dict)])
    create_payment_plan_snapshot_data(payment_plan)
    payment.refresh_from_db()
    assert payment.signature_hash == calculate_hash_manually(payment)


@freeze_time("2020-10-10")
def test_signature_after_prepare_payment_plan(
    business_area: Any,
    user: Any,
    program: Program,
    program_cycle: Any,
) -> None:
    DeliveryMechanismFactory(code="cash", name="Cash")
    fsp = FinancialServiceProviderFactory()

    hoh1 = IndividualFactory(household=None, program=program, business_area=business_area)
    hoh2 = IndividualFactory(household=None, program=program, business_area=business_area)
    hh1 = HouseholdFactory(
        head_of_household=hoh1,
        program=program,
        business_area=business_area,
        registration_data_import=hoh1.registration_data_import,
    )
    hh2 = HouseholdFactory(
        head_of_household=hoh2,
        program=program,
        business_area=business_area,
        registration_data_import=hoh2.registration_data_import,
    )
    hh1.refresh_from_db()
    hh2.refresh_from_db()

    IndividualFactory.create_batch(
        4,
        household=hh1,
        business_area=business_area,
        program=program,
        registration_data_import=hoh1.registration_data_import,
    )

    AccountFactory(individual=hoh1)
    AccountFactory(individual=hoh2)

    rules = [
        {
            "household_filters_blocks": [],
            "household_ids": f"{hh1.unicef_id}, {hh2.unicef_id}",
            "individual_ids": "",
            "individuals_filters_blocks": [],
        }
    ]

    input_data = {
        "business_area_slug": business_area.slug,
        "name": "paymentPlanName",
        "program_cycle_id": str(program_cycle.id),
        "rules": rules,
        "flag_exclude_if_active_adjudication_ticket": False,
        "flag_exclude_if_on_sanction_list": False,
        "excluded_ids": "TEST_INVALID_ID_01, TEST_INVALID_ID_02",
        "fsp_id": fsp.id,
        "delivery_mechanism_code": "cash",
    }

    with (
        mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0),
        mock.patch("hope.apps.payment.services.payment_plan_services.prepare_payment_plan_task"),
    ):
        pp = PaymentPlanService.create(
            input_data=input_data,
            user=user,
            business_area_slug=business_area.slug,
        )

    pp.refresh_from_db()
    assert pp.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_PENDING

    prepare_payment_plan_task(str(pp.id))
    pp.refresh_from_db()

    assert pp.build_status == PaymentPlan.BuildStatus.BUILD_STATUS_OK

    payment1 = pp.payment_items.all()[0]
    payment2 = pp.payment_items.all()[1]
    assert payment1.signature_hash == calculate_hash_manually(payment1)
    assert payment2.signature_hash == calculate_hash_manually(payment2)
