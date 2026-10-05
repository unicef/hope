from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.db.backends.postgresql.psycopg_any import NumericRange
from flags.models import FlagState
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanGroupFactory,
    ProgramCycleFactory,
    UserFactory,
)
from extras.test_utils.factories.core import CurrencyFactory
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentVerificationPlanFactory,
)
from hope.apps.payment.services.payment_plan_group_services import PaymentPlanGroupService
from hope.models import (
    AcceptanceProcessThreshold,
    Approval,
    DeliveryMechanism,
    LogEntry,
    Payment,
    PaymentPlan,
    PaymentPlanGroup,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def cycle():
    return ProgramCycleFactory()


@pytest.fixture
def delivery_mechanism():
    return DeliveryMechanismFactory()


@pytest.fixture
def financial_service_provider(delivery_mechanism):
    fsp = FinancialServiceProviderFactory()
    FspXlsxTemplatePerDeliveryMechanismFactory(
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
    )
    return fsp


@pytest.fixture
def currency():
    return CurrencyFactory()


@pytest.fixture
def open_group(cycle, financial_service_provider, currency):
    return PaymentPlanGroupFactory(
        cycle=cycle,
        status=PaymentPlanGroup.Status.OPEN,
        financial_service_provider=financial_service_provider,
        currency=currency,
    )


@pytest.fixture
def locked_payment_plan(cycle, open_group, financial_service_provider, delivery_mechanism, currency):
    return PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=open_group,
        status=PaymentPlan.Status.LOCKED,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism,
        currency=currency,
    )


def test_lock_sets_group_locked(open_group, locked_payment_plan):
    PaymentPlanGroupService(open_group).lock()

    open_group.refresh_from_db()
    assert open_group.status == PaymentPlanGroup.Status.LOCKED


def test_lock_sets_status_date(open_group, locked_payment_plan):
    PaymentPlanGroupService(open_group).lock()

    open_group.refresh_from_db()
    assert open_group.status_date is not None


def test_lock_locks_fsp_on_every_payment_plan(
    cycle, open_group, locked_payment_plan, financial_service_provider, delivery_mechanism, currency
):
    second_payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=open_group,
        status=PaymentPlan.Status.LOCKED,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism,
        currency=currency,
    )

    PaymentPlanGroupService(open_group).lock()

    locked_payment_plan.refresh_from_db()
    second_payment_plan.refresh_from_db()
    assert locked_payment_plan.status == PaymentPlan.Status.LOCKED_FSP
    assert second_payment_plan.status == PaymentPlan.Status.LOCKED_FSP


def test_lock_rejects_group_that_is_already_locked(cycle, locked_payment_plan):
    already_locked = locked_payment_plan.payment_plan_group
    already_locked.status = PaymentPlanGroup.Status.LOCKED
    already_locked.save(update_fields=["status"])

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(already_locked).lock()
    assert error.value.detail[0] == "Lock Payment Plan Group is possible only within Status OPEN"


def test_lock_rejects_group_without_payment_plans(open_group):
    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).lock()
    assert error.value.detail[0] == "Lock is not possible for a Payment Plan Group without Payment Plans."


def test_lock_rejects_payment_plan_that_is_not_locked(
    cycle, open_group, locked_payment_plan, financial_service_provider, delivery_mechanism, currency
):
    open_payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=open_group,
        status=PaymentPlan.Status.OPEN,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=delivery_mechanism,
        currency=currency,
    )

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).lock()
    assert error.value.detail[0] == (
        f"Every Payment Plan must be locked before the Payment Plan Group can be locked. "
        f"Not locked: {open_payment_plan.unicef_id}."
    )


def test_lock_rejects_group_without_fsp(open_group, locked_payment_plan):
    open_group.financial_service_provider = None
    open_group.save(update_fields=["financial_service_provider"])

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).lock()
    assert error.value.detail[0] == "Payment Plan Group needs a Financial Service Provider before it can be locked."


def test_lock_rejects_group_without_currency(open_group, locked_payment_plan):
    open_group.currency = None
    open_group.save(update_fields=["currency"])

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).lock()
    assert error.value.detail[0] == "Payment Plan Group needs a Currency before it can be locked."


def test_lock_rejects_payment_plan_without_delivery_template(
    cycle, open_group, locked_payment_plan, financial_service_provider, currency
):
    payment_plan_without_template = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=open_group,
        status=PaymentPlan.Status.LOCKED,
        financial_service_provider=financial_service_provider,
        delivery_mechanism=DeliveryMechanismFactory(),
        currency=currency,
    )

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).lock()
    assert error.value.detail[0] == (
        f"Every Payment Plan needs an FSP XLSX Template for its Financial Service Provider and "
        f"Delivery Mechanism. Missing for: {payment_plan_without_template.unicef_id}."
    )


def test_unlock_sets_group_open(open_group, locked_payment_plan):
    PaymentPlanGroupService(open_group).lock()

    PaymentPlanGroupService(open_group).unlock()

    open_group.refresh_from_db()
    assert open_group.status == PaymentPlanGroup.Status.OPEN


def test_unlock_releases_fsp_lock_on_every_payment_plan(open_group, locked_payment_plan):
    PaymentPlanGroupService(open_group).lock()

    PaymentPlanGroupService(open_group).unlock()

    locked_payment_plan.refresh_from_db()
    assert locked_payment_plan.status == PaymentPlan.Status.LOCKED


def test_unlock_rejects_group_that_is_open(open_group, locked_payment_plan):
    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).unlock()
    assert error.value.detail[0] == "Unlock Payment Plan Group is possible only within Status LOCKED"


def test_assign_fsp_copies_it_to_open_target_populations(cycle):
    group = PaymentPlanGroupFactory(cycle=cycle)
    target_population = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.TP_OPEN,
        financial_service_provider=None,
    )
    fsp = FinancialServiceProviderFactory()

    PaymentPlanGroupService(group).assign_financial_service_provider(fsp)
    group.save()

    target_population.refresh_from_db()
    assert group.financial_service_provider == fsp
    assert target_population.financial_service_provider == fsp


@patch("hope.apps.payment.services.payment_plan_services.payment_plan_full_rebuild_async_task")
def test_assign_fsp_rebuilds_every_target_population(mock_full_rebuild, cycle, django_capture_on_commit_callbacks):
    group = PaymentPlanGroupFactory(cycle=cycle)
    first = PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.TP_OPEN)
    second = PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.TP_OPEN)

    with django_capture_on_commit_callbacks(execute=True):
        PaymentPlanGroupService(group).assign_financial_service_provider(FinancialServiceProviderFactory())

    rebuilt = {call.args[0].pk for call in mock_full_rebuild.call_args_list}
    assert rebuilt == {first.pk, second.pk}


def test_assign_fsp_rejected_when_a_target_population_is_locked(cycle):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.TP_LOCKED)

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(group).assign_financial_service_provider(FinancialServiceProviderFactory())
    assert error.value.detail[0] == (
        "Financial Service Provider can be changed only while every Target Population in the group is Open."
    )


def test_assign_currency_rejected_when_a_payment_plan_is_opened(cycle, currency):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(program_cycle=cycle, payment_plan_group=group, status=PaymentPlan.Status.OPEN)

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(group).assign_currency(currency)
    assert error.value.detail[0] == "Currency can be changed only before any Payment Plan in the group is opened."


def test_assign_currency_usdc_rejected_with_non_digital_delivery_mechanism(cycle, delivery_mechanism):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.TP_OPEN,
        delivery_mechanism=delivery_mechanism,
    )

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(group).assign_currency(CurrencyFactory(code="USDC", name="USD Coin", is_crypto=True))
    assert (
        error.value.detail[0] == "For delivery mechanism Transfer to Digital Wallet only currency USDC can be assigned."
    )


def test_assign_currency_non_usdc_rejected_with_digital_wallet_delivery_mechanism(cycle, currency):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.TP_OPEN,
        delivery_mechanism=DeliveryMechanismFactory(transfer_type=DeliveryMechanism.TransferType.DIGITAL),
    )

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(group).assign_currency(currency)
    assert (
        error.value.detail[0] == "For delivery mechanism Transfer to Digital Wallet only currency USDC can be assigned."
    )


def test_assign_currency_sets_it_on_the_group(cycle, currency, delivery_mechanism):
    group = PaymentPlanGroupFactory(cycle=cycle)
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.DRAFT,
        delivery_mechanism=delivery_mechanism,
    )

    PaymentPlanGroupService(group).assign_currency(currency)

    assert group.currency == currency


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def locked_group(open_group, locked_payment_plan):
    PaymentPlanGroupService(open_group).lock()
    open_group.refresh_from_db()
    return open_group


@pytest.fixture
def group_in_approval(locked_group, user):
    with patch(
        "hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task"
    ):
        PaymentPlanGroupService(locked_group).send_for_approval(user)
    locked_group.refresh_from_db()
    return locked_group


@pytest.fixture
def group_in_authorization(group_in_approval, user):
    with patch(
        "hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task"
    ):
        PaymentPlanGroupService(group_in_approval).acceptance_process(PaymentPlan.Action.APPROVE.value, user)
    group_in_approval.refresh_from_db()
    return group_in_approval


@pytest.fixture
def group_in_review(group_in_authorization, user):
    with patch(
        "hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task"
    ):
        PaymentPlanGroupService(group_in_authorization).acceptance_process(PaymentPlan.Action.AUTHORIZE.value, user)
    group_in_authorization.refresh_from_db()
    return group_in_authorization


@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_send_for_approval_moves_group_and_plans(mock_notify, locked_group, locked_payment_plan, user):
    PaymentPlanGroupService(locked_group).send_for_approval(user)

    locked_group.refresh_from_db()
    locked_payment_plan.refresh_from_db()
    assert locked_group.status == PaymentPlanGroup.Status.IN_APPROVAL
    assert locked_payment_plan.status == PaymentPlan.Status.IN_APPROVAL


@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_send_for_approval_creates_approval_process_on_group(mock_notify, locked_group, locked_payment_plan, user):
    PaymentPlanGroupService(locked_group).send_for_approval(user)

    approval_process = locked_group.approval_process.get()
    assert approval_process.payment_plan is None
    assert approval_process.sent_for_approval_by == user
    assert approval_process.approval_number_required == 1
    assert locked_payment_plan.approval_process.count() == 0


@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_send_for_approval_takes_threshold_from_summed_total(
    mock_notify, cycle, open_group, locked_payment_plan, financial_service_provider, delivery_mechanism, currency, user
):
    locked_payment_plan.total_entitled_quantity_usd = 60
    locked_payment_plan.save(update_fields=["total_entitled_quantity_usd"])
    PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=open_group,
        status=PaymentPlan.Status.LOCKED,
        delivery_mechanism=delivery_mechanism,
        total_entitled_quantity_usd=60,
    )
    AcceptanceProcessThreshold.objects.create(
        business_area=open_group.business_area,
        payments_range_usd=NumericRange(100, 200),
        approval_number_required=2,
        authorization_number_required=3,
        finance_release_number_required=4,
    )
    PaymentPlanGroupService(open_group).lock()

    PaymentPlanGroupService(open_group).send_for_approval(user)

    approval_process = open_group.approval_process.get()
    assert approval_process.approval_number_required == 2
    assert approval_process.authorization_number_required == 3
    assert approval_process.finance_release_number_required == 4


@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_send_for_approval_queues_one_notification_for_the_group(mock_notify, locked_group, locked_payment_plan, user):
    PaymentPlanGroupService(locked_group).send_for_approval(user)

    mock_notify.assert_called_once()
    assert mock_notify.call_args.args[0] == locked_group
    assert mock_notify.call_args.args[1] == PaymentPlan.Action.SEND_FOR_APPROVAL.value


def test_send_for_approval_rejects_group_not_locked(open_group, locked_payment_plan, user):
    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).send_for_approval(user)
    assert error.value.detail[0] == "Send for Approval is possible only within Status LOCKED"


@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_approve_below_required_number_keeps_statuses(mock_notify, group_in_approval, locked_payment_plan, user):
    approval_process = group_in_approval.approval_process.get()
    approval_process.approval_number_required = 2
    approval_process.save(update_fields=["approval_number_required"])

    PaymentPlanGroupService(group_in_approval).acceptance_process(PaymentPlan.Action.APPROVE.value, user, "ok")

    group_in_approval.refresh_from_db()
    locked_payment_plan.refresh_from_db()
    assert group_in_approval.status == PaymentPlanGroup.Status.IN_APPROVAL
    assert locked_payment_plan.status == PaymentPlan.Status.IN_APPROVAL
    assert approval_process.approvals.get(type=Approval.APPROVAL).comment == "ok"
    mock_notify.assert_not_called()


@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_approve_reaching_required_number_moves_group_and_plans(
    mock_notify, group_in_approval, locked_payment_plan, user
):
    PaymentPlanGroupService(group_in_approval).acceptance_process(PaymentPlan.Action.APPROVE.value, user)

    group_in_approval.refresh_from_db()
    locked_payment_plan.refresh_from_db()
    approval_process = group_in_approval.approval_process.get()
    assert group_in_approval.status == PaymentPlanGroup.Status.IN_AUTHORIZATION
    assert locked_payment_plan.status == PaymentPlan.Status.IN_AUTHORIZATION
    assert approval_process.sent_for_authorization_by == user
    assert mock_notify.call_args.args[1] == PaymentPlan.Action.APPROVE.value


def test_approve_rejects_group_in_wrong_status(locked_group, user):
    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(locked_group).acceptance_process(PaymentPlan.Action.APPROVE.value, user)
    assert error.value.detail[0] == "Not possible to create APPROVE for Payment Plan Group within status LOCKED"


@patch("hope.apps.payment.services.payment_plan_services.config")
@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_second_approval_by_same_user_rejected(mock_notify, mock_config, group_in_approval, user):
    mock_config.PM_ACCEPTANCE_PROCESS_USER_HAVE_MULTIPLE_APPROVALS = False
    approval_process = group_in_approval.approval_process.get()
    approval_process.approval_number_required = 2
    approval_process.save(update_fields=["approval_number_required"])
    PaymentPlanGroupService(group_in_approval).acceptance_process(PaymentPlan.Action.APPROVE.value, user)

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(group_in_approval).acceptance_process(PaymentPlan.Action.APPROVE.value, user)
    assert error.value.detail[0] == "Can't create new APPROVAL. User have already created APPROVAL"


@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_reject_returns_group_and_plans_to_locked(mock_notify, group_in_approval, locked_payment_plan, user):
    PaymentPlanGroupService(group_in_approval).acceptance_process(PaymentPlan.Action.REJECT.value, user, "no")

    group_in_approval.refresh_from_db()
    locked_payment_plan.refresh_from_db()
    assert group_in_approval.status == PaymentPlanGroup.Status.LOCKED
    assert locked_payment_plan.status == PaymentPlan.Status.LOCKED_FSP
    assert group_in_approval.approval_process.get().approvals.filter(type=Approval.REJECT).exists()
    mock_notify.assert_not_called()


@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_authorize_moves_group_and_plans_to_in_review(mock_notify, group_in_authorization, locked_payment_plan, user):
    PaymentPlanGroupService(group_in_authorization).acceptance_process(PaymentPlan.Action.AUTHORIZE.value, user)

    group_in_authorization.refresh_from_db()
    locked_payment_plan.refresh_from_db()
    assert group_in_authorization.status == PaymentPlanGroup.Status.IN_REVIEW
    assert locked_payment_plan.status == PaymentPlan.Status.IN_REVIEW
    assert group_in_authorization.approval_process.get().sent_for_finance_release_by == user


@patch("hope.contrib.vision.tasks.send_payment_plan_to_vision_async_task")
@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_authorize_queues_vision_send_for_every_plan(
    mock_notify,
    mock_send_to_vision,
    group_in_authorization,
    locked_payment_plan,
    user,
    django_capture_on_commit_callbacks,
):
    FlagState.objects.get_or_create(name="VISION_INTEGRATION_ACTIVE", condition="boolean", value="True")
    business_area = locked_payment_plan.business_area
    business_area.vision_integration_active = True
    business_area.save(update_fields=["vision_integration_active"])

    with django_capture_on_commit_callbacks(execute=True):
        PaymentPlanGroupService(group_in_authorization).acceptance_process(PaymentPlan.Action.AUTHORIZE.value, user)

    mock_send_to_vision.assert_called_once_with(locked_payment_plan, str(locked_payment_plan.created_by_id))


@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_mark_as_released_moves_group_and_plans_to_accepted(mock_notify, group_in_review, locked_payment_plan, user):
    PaymentPlanGroupService(group_in_review).acceptance_process(PaymentPlan.Action.REVIEW.value, user)

    group_in_review.refresh_from_db()
    locked_payment_plan.refresh_from_db()
    assert group_in_review.status == PaymentPlanGroup.Status.ACCEPTED
    assert locked_payment_plan.status == PaymentPlan.Status.ACCEPTED
    assert mock_notify.call_args.args[1] == PaymentPlan.Action.REVIEW.value


def test_mark_as_released_rejected_when_a_plan_is_vision_managed(group_in_review, locked_payment_plan, user):
    FlagState.objects.get_or_create(name="VISION_INTEGRATION_ACTIVE", condition="boolean", value="True")
    business_area = locked_payment_plan.business_area
    business_area.vision_integration_active = True
    business_area.save(update_fields=["vision_integration_active"])

    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(group_in_review).acceptance_process(PaymentPlan.Action.REVIEW.value, user)
    assert error.value.detail[0] == "Vision-managed Payment Plans are released automatically after FC assignment"


@pytest.mark.enable_activity_log
@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_approve_logs_event_on_group(mock_notify, group_in_approval, user):
    PaymentPlanGroupService(group_in_approval).acceptance_process(PaymentPlan.Action.APPROVE.value, user, "fine")

    log = LogEntry.objects.get(
        content_type=ContentType.objects.get_for_model(PaymentPlanGroup),
        object_id=group_in_approval.pk,
        changes__has_key="acceptance_process",
    )
    assert log.user == user
    assert log.changes["acceptance_process"] == {"from": None, "to": Approval.APPROVAL}
    assert log.changes["comment"] == {"from": None, "to": "fine"}


@pytest.fixture
def accepted_group(group_in_review, user):
    with patch(
        "hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task"
    ):
        PaymentPlanGroupService(group_in_review).acceptance_process(PaymentPlan.Action.REVIEW.value, user)
    group_in_review.refresh_from_db()
    return group_in_review


@pytest.fixture
def delivered_payment(locked_payment_plan):
    return PaymentFactory(parent=locked_payment_plan, status=Payment.STATUS_DISTRIBUTION_SUCCESS)


@pytest.fixture
def finished_group(accepted_group, delivered_payment):
    PaymentPlanGroupService(accepted_group).sync_finished()
    accepted_group.refresh_from_db()
    return accepted_group


@pytest.fixture
def ready_group(finished_group, user):
    with patch(
        "hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task"
    ):
        PaymentPlanGroupService(finished_group).ready_for_closure(user)
    finished_group.refresh_from_db()
    return finished_group


def test_sync_finished_moves_group_and_plans_when_every_payment_is_reconciled(
    accepted_group, locked_payment_plan, delivered_payment
):
    PaymentPlanGroupService(accepted_group).sync_finished()

    accepted_group.refresh_from_db()
    locked_payment_plan.refresh_from_db()
    assert accepted_group.status == PaymentPlanGroup.Status.FINISHED
    assert locked_payment_plan.status == PaymentPlan.Status.FINISHED


def test_sync_finished_waits_for_every_payment_in_the_group(
    cycle, accepted_group, locked_payment_plan, delivered_payment, delivery_mechanism
):
    second_payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=accepted_group,
        status=PaymentPlan.Status.ACCEPTED,
        delivery_mechanism=delivery_mechanism,
    )
    PaymentFactory(parent=second_payment_plan, status=Payment.STATUS_PENDING)

    PaymentPlanGroupService(accepted_group).sync_finished()

    accepted_group.refresh_from_db()
    locked_payment_plan.refresh_from_db()
    assert accepted_group.status == PaymentPlanGroup.Status.ACCEPTED
    assert locked_payment_plan.status == PaymentPlan.Status.ACCEPTED


def test_sync_finished_reopens_group_and_plans_when_a_payment_is_pending_again(
    finished_group, locked_payment_plan, delivered_payment
):
    delivered_payment.status = Payment.STATUS_PENDING
    delivered_payment.save(update_fields=["status"])

    PaymentPlanGroupService(finished_group).sync_finished()

    finished_group.refresh_from_db()
    locked_payment_plan.refresh_from_db()
    assert finished_group.status == PaymentPlanGroup.Status.ACCEPTED
    assert locked_payment_plan.status == PaymentPlan.Status.ACCEPTED


@pytest.fixture
def follow_up_payment_plan(cycle, finished_group, locked_payment_plan, delivery_mechanism):
    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        payment_plan_group=finished_group,
        source_payment_plan=locked_payment_plan,
        plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        status=PaymentPlan.Status.OPEN,
        delivery_mechanism=delivery_mechanism,
    )
    PaymentFactory(parent=payment_plan, status=Payment.STATUS_PENDING)
    return payment_plan


def test_sync_finished_ignores_pending_payment_of_follow_up_plan(finished_group, follow_up_payment_plan):
    PaymentPlanGroupService(finished_group).sync_finished()

    finished_group.refresh_from_db()
    follow_up_payment_plan.refresh_from_db()
    assert finished_group.status == PaymentPlanGroup.Status.FINISHED
    assert follow_up_payment_plan.status == PaymentPlan.Status.OPEN


@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_ready_for_closure_leaves_follow_up_plan_untouched(mock_notify, finished_group, follow_up_payment_plan, user):
    PaymentPlanGroupService(finished_group).ready_for_closure(user)

    finished_group.refresh_from_db()
    follow_up_payment_plan.refresh_from_db()
    assert finished_group.status == PaymentPlanGroup.Status.READY_FOR_CLOSURE
    assert follow_up_payment_plan.status == PaymentPlan.Status.OPEN


@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_ready_for_closure_moves_group_and_plans(mock_notify, finished_group, locked_payment_plan, user):
    PaymentPlanGroupService(finished_group).ready_for_closure(user)

    finished_group.refresh_from_db()
    locked_payment_plan.refresh_from_db()
    assert finished_group.status == PaymentPlanGroup.Status.READY_FOR_CLOSURE
    assert locked_payment_plan.status == PaymentPlan.Status.READY_FOR_CLOSURE
    mock_notify.assert_called_once()
    assert mock_notify.call_args.args[1] == PaymentPlan.Action.MARK_READY_FOR_CLOSURE.value


def test_ready_for_closure_rejects_group_not_finished(accepted_group, user):
    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(accepted_group).ready_for_closure(user)
    assert error.value.detail[0] == "Mark as Ready for Closure is possible only within Status FINISHED"


@patch("hope.apps.payment.services.payment_plan_group_services.send_payment_plan_group_notification_emails_async_task")
def test_send_back_to_finished_moves_group_and_plans(mock_notify, ready_group, locked_payment_plan, user):
    PaymentPlanGroupService(ready_group).send_back_to_finished(user)

    ready_group.refresh_from_db()
    locked_payment_plan.refresh_from_db()
    assert ready_group.status == PaymentPlanGroup.Status.FINISHED
    assert locked_payment_plan.status == PaymentPlan.Status.FINISHED
    assert mock_notify.call_args.args[1] == PaymentPlan.Action.SEND_BACK_TO_FINISHED.value


def test_close_requires_comment_when_no_plan_was_verified(ready_group, user):
    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(ready_group).close(None, user)
    assert error.value.detail[0] == "Closure comment is required when no payment verification was carried out."


def test_close_with_comment_closes_group_and_plans(ready_group, locked_payment_plan, user):
    PaymentPlanGroupService(ready_group).close("all paid", user)

    ready_group.refresh_from_db()
    locked_payment_plan.refresh_from_db()
    assert ready_group.status == PaymentPlanGroup.Status.CLOSED
    assert ready_group.closure_comment == "all paid"
    assert ready_group.closed_by == user
    assert locked_payment_plan.status == PaymentPlan.Status.CLOSED


def test_close_without_comment_allowed_when_every_plan_was_verified(ready_group, locked_payment_plan, user):
    PaymentVerificationPlanFactory(payment_plan=locked_payment_plan, responded_count=1)

    PaymentPlanGroupService(ready_group).close(None, user)

    ready_group.refresh_from_db()
    assert ready_group.status == PaymentPlanGroup.Status.CLOSED


def test_abort_moves_group_and_plans(group_in_approval, locked_payment_plan, user):
    PaymentPlanGroupService(group_in_approval).abort("wrong amounts", user)

    group_in_approval.refresh_from_db()
    locked_payment_plan.refresh_from_db()
    assert group_in_approval.status == PaymentPlanGroup.Status.ABORTED
    assert group_in_approval.abort_comment == "wrong amounts"
    assert locked_payment_plan.status == PaymentPlan.Status.ABORTED


def test_abort_rejects_open_group(open_group, locked_payment_plan, user):
    with pytest.raises(ValidationError) as error:
        PaymentPlanGroupService(open_group).abort(None, user)
    assert error.value.detail[0] == "Abort Payment Plan Group is not possible within Status OPEN"


@patch("hope.apps.payment.services.payment_plan_services.payment_plan_full_rebuild_async_task")
def test_reactivate_abort_reopens_group_and_plans(
    mock_rebuild, group_in_approval, locked_payment_plan, user, django_capture_on_commit_callbacks
):
    PaymentPlanGroupService(group_in_approval).abort(None, user)

    with django_capture_on_commit_callbacks(execute=True):
        PaymentPlanGroupService(group_in_approval).reactivate_abort()

    group_in_approval.refresh_from_db()
    locked_payment_plan.refresh_from_db()
    assert group_in_approval.status == PaymentPlanGroup.Status.OPEN
    assert locked_payment_plan.status == PaymentPlan.Status.OPEN
    mock_rebuild.assert_called_once_with(locked_payment_plan, True)
