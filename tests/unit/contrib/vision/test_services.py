from unittest.mock import ANY, MagicMock, PropertyMock, patch

from flags.models import FlagState
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    ApprovalProcessFactory,
    BusinessAreaFactory,
    FollowUpInstructionFactory,
    FundsCommitmentGroupFactory,
    FundsCommitmentItemFactory,
    PaymentPlanFactory,
)
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.contrib.vision.api import VisionAPI, VisionAPIError, VisionAPIMissingCredentialsError
from hope.contrib.vision.choices import VisionErrorCode, VisionLogEntryType, VisionStatus
from hope.contrib.vision.services import FundsCommitmentAssignmentError, VisionService
from hope.contrib.vision.tasks import (
    send_payment_plan_to_vision_async_task,
    send_payment_plan_to_vision_async_task_action,
)
from hope.models import Approval, AsyncJob, PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def vision_payment_plan() -> PaymentPlan:
    business_area = BusinessAreaFactory(vision_integration_active=True)
    FlagState.objects.get_or_create(
        name="VISION_INTEGRATION_ACTIVE",
        condition="boolean",
        value="True",
    )
    payment_plan = PaymentPlanFactory(
        business_area=business_area,
        program_cycle__program__business_area=business_area,
        status=PaymentPlan.Status.IN_REVIEW,
    )
    ApprovalProcessFactory(payment_plan=payment_plan)
    return payment_plan


@pytest.fixture
def vision_enabled_payment_plan(vision_payment_plan: PaymentPlan) -> PaymentPlan:
    FlagState.objects.get_or_create(
        name="VISION_INTEGRATION_ACTIVE",
        condition="boolean",
        value="True",
    )
    return vision_payment_plan


@pytest.fixture(params=["global", "business-area"])
def vision_disabled_payment_plan(request, vision_payment_plan: PaymentPlan) -> PaymentPlan:
    if request.param == "global":
        FlagState.objects.filter(name="VISION_INTEGRATION_ACTIVE", condition="boolean").update(value="False")
    else:
        vision_payment_plan.business_area.vision_integration_active = False
        vision_payment_plan.business_area.save(update_fields=["vision_integration_active"])
    return vision_payment_plan


@pytest.fixture
def instruction_managed_payment_plan(vision_enabled_payment_plan: PaymentPlan) -> PaymentPlan:
    instruction = FollowUpInstructionFactory(
        business_area=vision_enabled_payment_plan.business_area,
        program=vision_enabled_payment_plan.program,
        created_by=vision_enabled_payment_plan.created_by,
    )
    vision_enabled_payment_plan.follow_up_instruction = instruction
    vision_enabled_payment_plan.save(update_fields=["follow_up_instruction"])
    return vision_enabled_payment_plan


@pytest.fixture
def matching_fc_items(vision_payment_plan: PaymentPlan) -> list:
    group = FundsCommitmentGroupFactory(funds_commitment_number="FC123")
    return [
        FundsCommitmentItemFactory(funds_commitment_group=group, office=vision_payment_plan.business_area),
        FundsCommitmentItemFactory(funds_commitment_group=group, office=vision_payment_plan.business_area),
    ]


@pytest.fixture
def ambiguous_fc_items(vision_payment_plan: PaymentPlan) -> list:
    first_group = FundsCommitmentGroupFactory(funds_commitment_number="FC123")
    second_group = FundsCommitmentGroupFactory(funds_commitment_number="FC123")
    return [
        FundsCommitmentItemFactory(funds_commitment_group=first_group, office=vision_payment_plan.business_area),
        FundsCommitmentItemFactory(funds_commitment_group=second_group, office=vision_payment_plan.business_area),
    ]


@pytest.fixture
def conflicting_fc_items(vision_payment_plan: PaymentPlan) -> list:
    other_payment_plan = PaymentPlanFactory()
    group = FundsCommitmentGroupFactory(funds_commitment_number="FC123")
    return [
        FundsCommitmentItemFactory(
            funds_commitment_group=group,
            office=vision_payment_plan.business_area,
            payment_plan=other_payment_plan,
        ),
        FundsCommitmentItemFactory(funds_commitment_group=group, office=vision_payment_plan.business_area),
    ]


@pytest.fixture
def fc_items_with_existing_group_assignment(vision_payment_plan: PaymentPlan) -> tuple[list, object]:
    target_group = FundsCommitmentGroupFactory(funds_commitment_number="FC123")
    matching_items = [
        FundsCommitmentItemFactory(
            funds_commitment_group=target_group,
            office=vision_payment_plan.business_area,
        )
    ]
    existing_item = FundsCommitmentItemFactory(
        funds_commitment_group=FundsCommitmentGroupFactory(funds_commitment_number="FC999"),
        office=vision_payment_plan.business_area,
        payment_plan=vision_payment_plan,
    )
    return matching_items, existing_item


@pytest.fixture
def malformed_vision_payment_plan(vision_payment_plan: PaymentPlan) -> PaymentPlan:
    vision_payment_plan.internal_data = {"vision": "invalid"}
    return vision_payment_plan


@pytest.fixture
def accepted_vision_payment_plan(vision_payment_plan: PaymentPlan) -> PaymentPlan:
    vision_payment_plan.status = PaymentPlan.Status.ACCEPTED
    return vision_payment_plan


@pytest.fixture
def vision_payment_plan_without_approval(vision_payment_plan: PaymentPlan) -> PaymentPlan:
    vision_payment_plan.approval_process.all().delete()
    return vision_payment_plan


@pytest.fixture(
    params=[
        (VisionStatus.FC_MISSING, None),
        (VisionStatus.FC_NOT_FOUND, None),
        (VisionStatus.CALLBACK_FAILED, VisionErrorCode.FC_AMBIGUOUS),
        (VisionStatus.CALLBACK_FAILED, VisionErrorCode.FC_CONFLICT),
    ]
)
def payment_plan_with_fc_assignment_failure(request, vision_payment_plan: PaymentPlan) -> PaymentPlan:
    vision_status, error_code = request.param
    VisionService.set_status(vision_payment_plan, vision_status, error_code=error_code)
    return vision_payment_plan


@pytest.fixture
def vision_disabled_payment_plan_with_fc_failure(
    vision_disabled_payment_plan: PaymentPlan,
) -> PaymentPlan:
    VisionService.set_status(vision_disabled_payment_plan, VisionStatus.FC_NOT_FOUND)
    return vision_disabled_payment_plan


def test_vision_data_replaces_malformed_state(
    malformed_vision_payment_plan: PaymentPlan,
    django_assert_num_queries,
) -> None:
    with django_assert_num_queries(0):
        vision_data = VisionService.vision_data(malformed_vision_payment_plan)

    assert vision_data == {}
    assert malformed_vision_payment_plan.internal_data == {"vision": {}}


def test_vision_status_treats_malformed_state_as_not_sent(
    malformed_vision_payment_plan: PaymentPlan,
    django_assert_num_queries,
) -> None:
    with django_assert_num_queries(0):
        vision_status = malformed_vision_payment_plan.vision_status

    assert vision_status == VisionStatus.NOT_SENT.value


def test_assign_funds_commitment_assigns_all_matching_items(
    vision_payment_plan: PaymentPlan,
    matching_fc_items: list,
    django_assert_num_queries,
) -> None:
    with django_assert_num_queries(4):
        VisionService.assign_funds_commitment(vision_payment_plan, "FC123")

    assert all(item.payment_plan_id is None for item in matching_fc_items)
    assert all(
        item.payment_plan_id == vision_payment_plan.pk
        for item in type(matching_fc_items[0]).objects.filter(pk__in=[item.pk for item in matching_fc_items])
    )


def test_assign_funds_commitment_reports_missing_items(
    vision_payment_plan: PaymentPlan,
    django_assert_num_queries,
) -> None:
    with django_assert_num_queries(1), pytest.raises(FundsCommitmentAssignmentError) as error:
        VisionService.assign_funds_commitment(vision_payment_plan, "UNKNOWN")

    assert error.value.status == VisionStatus.FC_NOT_FOUND
    assert error.value.error_code is None


def test_assign_funds_commitment_rejects_ambiguous_group(
    vision_payment_plan: PaymentPlan,
    ambiguous_fc_items: list,
    django_assert_num_queries,
) -> None:
    with django_assert_num_queries(1), pytest.raises(FundsCommitmentAssignmentError) as error:
        VisionService.assign_funds_commitment(vision_payment_plan, "FC123")

    assert error.value.status == VisionStatus.CALLBACK_FAILED
    assert error.value.error_code == VisionErrorCode.FC_AMBIGUOUS
    assert all(item.payment_plan_id is None for item in ambiguous_fc_items)


def test_assign_funds_commitment_rejects_item_assigned_to_another_plan(
    vision_payment_plan: PaymentPlan,
    conflicting_fc_items: list,
    django_assert_num_queries,
) -> None:
    original_assignments = [item.payment_plan_id for item in conflicting_fc_items]

    with django_assert_num_queries(2), pytest.raises(FundsCommitmentAssignmentError) as error:
        VisionService.assign_funds_commitment(vision_payment_plan, "FC123")

    assert error.value.status == VisionStatus.CALLBACK_FAILED
    assert error.value.error_code == VisionErrorCode.FC_CONFLICT
    assert [item.payment_plan_id for item in conflicting_fc_items] == original_assignments


def test_assign_funds_commitment_rejects_plan_items_from_another_group(
    vision_payment_plan: PaymentPlan,
    fc_items_with_existing_group_assignment: tuple[list, object],
    django_assert_num_queries,
) -> None:
    matching_items, existing_item = fc_items_with_existing_group_assignment

    with django_assert_num_queries(3), pytest.raises(FundsCommitmentAssignmentError) as error:
        VisionService.assign_funds_commitment(vision_payment_plan, "FC123")

    assert error.value.status == VisionStatus.CALLBACK_FAILED
    assert error.value.error_code == VisionErrorCode.FC_CONFLICT
    assert matching_items[0].payment_plan_id is None
    assert existing_item.payment_plan_id == vision_payment_plan.pk


def test_process_callback_without_fc_keeps_plan_blocked(
    vision_payment_plan: PaymentPlan,
    django_assert_num_queries,
) -> None:
    VisionService.set_status(vision_payment_plan, VisionStatus.WAITING_FOR_CALLBACK)
    with django_assert_num_queries(1):
        fc_assignment_failed = VisionService.process_callback(
            vision_payment_plan,
            vision_payment_plan_id="VISION-1",
            vision_result="SUCCESS",
            fc_num="",
        )

    assert fc_assignment_failed is True
    assert vision_payment_plan.status == PaymentPlan.Status.IN_REVIEW
    assert vision_payment_plan.vision_data == {
        "vision_id": "VISION-1",
        "status": VisionStatus.FC_MISSING.value,
    }


def test_process_callback_records_fc_assignment_failure(
    vision_payment_plan: PaymentPlan,
    django_assert_num_queries,
) -> None:
    VisionService.set_status(vision_payment_plan, VisionStatus.WAITING_FOR_CALLBACK)

    with django_assert_num_queries(2):
        fc_assignment_failed = VisionService.process_callback(
            vision_payment_plan,
            vision_payment_plan_id="VISION-1",
            vision_result="SUCCESS",
            fc_num="UNKNOWN",
        )

    assert fc_assignment_failed is True
    assert vision_payment_plan.status == PaymentPlan.Status.IN_REVIEW
    assert vision_payment_plan.vision_data == {
        "vision_id": "VISION-1",
        "fc_num": "UNKNOWN",
        "status": VisionStatus.FC_NOT_FOUND.value,
    }


def test_process_callback_failure_stores_returned_fc_number(
    vision_payment_plan: PaymentPlan,
    django_assert_num_queries,
) -> None:
    VisionService.set_status(vision_payment_plan, VisionStatus.WAITING_FOR_CALLBACK)
    with django_assert_num_queries(1):
        fc_assignment_failed = VisionService.process_callback(
            vision_payment_plan,
            vision_payment_plan_id="VISION-1",
            vision_result="ERROR",
            fc_num="FC123",
        )

    assert fc_assignment_failed is False
    assert vision_payment_plan.status == PaymentPlan.Status.IN_REVIEW
    assert vision_payment_plan.vision_data == {
        "vision_id": "VISION-1",
        "fc_num": "FC123",
        "status": VisionStatus.CALLBACK_FAILED.value,
        "error_code": VisionErrorCode.VISION_STATUS_FAILED.value,
    }


def test_process_callback_repeats_existing_fc_assignment_failure(
    payment_plan_with_fc_assignment_failure: PaymentPlan,
    django_assert_num_queries,
) -> None:
    payment_plan = payment_plan_with_fc_assignment_failure

    with django_assert_num_queries(1):
        fc_assignment_failed = VisionService.process_callback(
            payment_plan,
            vision_payment_plan_id="VISION-RETRY",
            vision_result="SUCCESS",
            fc_num="FC123",
        )

    assert fc_assignment_failed is True


def test_process_callback_ignores_plan_that_is_not_waiting_for_vision(
    vision_payment_plan: PaymentPlan,
    matching_fc_items: list,
    django_assert_num_queries,
) -> None:
    with django_assert_num_queries(1):
        VisionService.process_callback(
            vision_payment_plan,
            vision_payment_plan_id="VISION-UNEXPECTED",
            vision_result="SUCCESS",
            fc_num="FC123",
        )

    assert vision_payment_plan.status == PaymentPlan.Status.IN_REVIEW
    assert vision_payment_plan.vision_data == {}
    assert all(item.payment_plan_id is None for item in matching_fc_items)


@pytest.mark.parametrize("payment_plan_status", [PaymentPlan.Status.LOCKED_FSP, PaymentPlan.Status.ABORTED])
def test_process_callback_ignores_plan_that_has_left_review(
    vision_payment_plan: PaymentPlan,
    matching_fc_items: list,
    payment_plan_status: str,
    django_assert_num_queries,
) -> None:
    vision_payment_plan.status = payment_plan_status
    VisionService.set_status(vision_payment_plan, VisionStatus.WAITING_FOR_CALLBACK)

    with django_assert_num_queries(1):
        VisionService.process_callback(
            vision_payment_plan,
            vision_payment_plan_id="VISION-LATE",
            vision_result="SUCCESS",
            fc_num="FC123",
        )

    assert vision_payment_plan.vision_status == VisionStatus.WAITING_FOR_CALLBACK.value
    assert all(item.payment_plan_id is None for item in matching_fc_items)


def test_process_callback_does_not_change_released_plan(
    vision_payment_plan: PaymentPlan,
    django_assert_num_queries,
) -> None:
    vision_payment_plan.status = PaymentPlan.Status.FINISHED
    vision_payment_plan.internal_data = {
        "vision": {
            "vision_id": "VISION-1",
            "fc_num": "FC123",
            "status": VisionStatus.RELEASED.value,
        }
    }

    with django_assert_num_queries(0):
        VisionService.process_callback(
            vision_payment_plan,
            vision_payment_plan_id="VISION-2",
            vision_result="ERROR",
            fc_num="FC999",
        )

    assert vision_payment_plan.vision_data == {
        "vision_id": "VISION-1",
        "fc_num": "FC123",
        "status": VisionStatus.RELEASED.value,
    }


def test_existing_accepted_plan_without_vision_state_remains_on_manual_delivery_path(
    vision_enabled_payment_plan: PaymentPlan,
) -> None:
    vision_enabled_payment_plan.status = PaymentPlan.Status.ACCEPTED
    vision_enabled_payment_plan.internal_data = {}

    assert vision_enabled_payment_plan.vision_integration_enabled is True
    assert vision_enabled_payment_plan.vision_managed is False


def test_callback_log_without_workflow_state_does_not_make_plan_vision_managed(
    vision_payment_plan: PaymentPlan,
) -> None:
    vision_payment_plan.status = PaymentPlan.Status.ACCEPTED
    vision_payment_plan.internal_data = {"vision": {"log": [{"type": VisionLogEntryType.PUSH_NOTIFICATION.value}]}}

    assert vision_payment_plan.vision_managed is False


def test_disabled_vision_flag_makes_existing_workflow_not_managed(
    vision_disabled_payment_plan: PaymentPlan,
) -> None:
    payment_plan = vision_disabled_payment_plan
    payment_plan.internal_data = {
        "vision": {
            "sent": True,
            "status": VisionStatus.WAITING_FOR_CALLBACK.value,
            "vision_id": "VISION-1",
        }
    }

    assert payment_plan.vision_integration_enabled is False
    assert payment_plan.vision_managed is False


def test_callback_does_not_process_when_vision_flag_is_disabled(
    vision_disabled_payment_plan: PaymentPlan,
    django_assert_num_queries,
) -> None:
    payment_plan = vision_disabled_payment_plan
    payment_plan.internal_data = {
        "vision": {
            "sent": True,
            "status": VisionStatus.WAITING_FOR_CALLBACK.value,
        }
    }

    with django_assert_num_queries(1):
        VisionService.process_callback(
            payment_plan,
            vision_payment_plan_id="VISION-1",
            vision_result="SUCCESS",
            fc_num="FC123",
        )

    assert payment_plan.vision_data == {
        "sent": True,
        "status": VisionStatus.WAITING_FOR_CALLBACK.value,
    }


def test_disabled_vision_flag_keeps_stored_fc_failure_log_only(
    vision_disabled_payment_plan_with_fc_failure: PaymentPlan,
    django_assert_num_queries,
) -> None:
    with django_assert_num_queries(1):
        fc_assignment_failed = VisionService.process_callback(
            vision_disabled_payment_plan_with_fc_failure,
            vision_payment_plan_id="VISION-1",
            vision_result="SUCCESS",
            fc_num="FC123",
        )

    assert fc_assignment_failed is False


def test_instruction_managed_plan_is_excluded_from_vision(
    instruction_managed_payment_plan: PaymentPlan,
) -> None:
    assert instruction_managed_payment_plan.vision_integration_enabled is False
    assert instruction_managed_payment_plan.can_send_to_vision is False
    assert instruction_managed_payment_plan.vision_managed is False


def test_send_result_merges_callback_state_instead_of_overwriting_it(
    vision_payment_plan: PaymentPlan,
    django_assert_num_queries,
) -> None:
    vision_payment_plan.internal_data = {
        "vision": {
            "status": VisionStatus.WAITING_FOR_CALLBACK.value,
        }
    }
    vision_payment_plan.save(update_fields=["internal_data"])
    stale_payment_plan = PaymentPlan.objects.get(pk=vision_payment_plan.pk)

    vision_payment_plan.status = PaymentPlan.Status.ACCEPTED
    vision_payment_plan.internal_data = {
        "vision": {
            "status": VisionStatus.RELEASED.value,
            "vision_id": "VISION-1",
            "fc_num": "FC123",
            "log": [{"type": VisionLogEntryType.PUSH_NOTIFICATION.value}],
        }
    }
    vision_payment_plan.save(update_fields=["status", "internal_data"])
    send_log = {
        "type": VisionLogEntryType.API_CALL.value,
        "response": {"status": "ok"},
    }

    with django_assert_num_queries(4):
        VisionAPI._persist_send_result(
            stale_payment_plan,
            send_log,
            VisionStatus.WAITING_FOR_CALLBACK,
            sent=True,
        )

    stale_payment_plan.refresh_from_db()
    assert stale_payment_plan.vision_data["status"] == VisionStatus.RELEASED.value
    assert stale_payment_plan.vision_data["vision_id"] == "VISION-1"
    assert stale_payment_plan.vision_data["fc_num"] == "FC123"
    assert "sent" not in stale_payment_plan.vision_data
    assert [entry["type"] for entry in stale_payment_plan.vision_data["log"]] == [
        VisionLogEntryType.PUSH_NOTIFICATION.value,
        VisionLogEntryType.API_CALL.value,
    ]


@patch("hope.apps.payment.services.payment_plan_services.send_payment_notification_emails_async_task")
@patch("hope.apps.payment.services.payment_plan_services.update_exchange_rate_on_release_payments_async_task")
@patch("hope.apps.payment.services.payment_plan_services.log_create")
@patch("hope.apps.payment.services.payment_plan_services.log_payment_plan_approval")
def test_release_from_vision_uses_payment_plan_creator(
    mock_approval_log,
    mock_activity_log,
    mock_exchange_rate,
    mock_notification,
    vision_payment_plan: PaymentPlan,
) -> None:
    PaymentPlanService(vision_payment_plan).release_from_vision()

    vision_payment_plan.refresh_from_db()
    release = vision_payment_plan.approval_process.first().approvals.get(type=Approval.FINANCE_RELEASE)
    assert vision_payment_plan.status == PaymentPlan.Status.ACCEPTED
    assert release.created_by == vision_payment_plan.created_by
    assert release.comment is None
    mock_notification.assert_called_once_with(
        vision_payment_plan,
        PaymentPlan.Action.REVIEW.value,
        str(vision_payment_plan.created_by_id),
        ANY,
    )


def test_release_from_vision_rejects_non_review_plan(
    accepted_vision_payment_plan: PaymentPlan,
    django_assert_num_queries,
) -> None:
    with django_assert_num_queries(0), pytest.raises(ValidationError, match="Only an in-review"):
        PaymentPlanService(accepted_vision_payment_plan).release_from_vision()


def test_release_from_vision_requires_approval_process(
    vision_payment_plan_without_approval: PaymentPlan,
    django_assert_num_queries,
) -> None:
    with django_assert_num_queries(1), pytest.raises(ValidationError, match="Approval Process object not found"):
        PaymentPlanService(vision_payment_plan_without_approval).release_from_vision()


def test_manual_review_is_rejected_for_vision_managed_plan(
    vision_payment_plan: PaymentPlan,
    django_assert_num_queries,
) -> None:
    with django_assert_num_queries(1), pytest.raises(ValidationError, match="released automatically"):
        PaymentPlanService(vision_payment_plan).execute_update_status_action(
            input_data={"action": PaymentPlan.Action.REVIEW},
            user=vision_payment_plan.created_by,
        )


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.execute_update_status_action")
@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.release_from_vision")
def test_process_callback_assigns_fc_releases_and_sends_to_pg(
    mock_release,
    mock_send_to_pg,
    vision_payment_plan: PaymentPlan,
    matching_fc_items: list,
    django_assert_num_queries,
) -> None:
    VisionService.set_status(vision_payment_plan, VisionStatus.WAITING_FOR_CALLBACK)
    with (
        patch.object(PaymentPlan, "can_send_to_payment_gateway", new_callable=PropertyMock, return_value=True),
        django_assert_num_queries(6),
    ):
        VisionService.process_callback(
            vision_payment_plan,
            vision_payment_plan_id="VISION-1",
            vision_result="SUCCESS",
            fc_num="FC123",
        )

    mock_release.assert_called_once_with()
    mock_send_to_pg.assert_called_once_with(
        input_data={"action": PaymentPlan.Action.SEND_TO_PAYMENT_GATEWAY},
        user=vision_payment_plan.created_by,
    )
    assert vision_payment_plan.vision_status == VisionStatus.RELEASED.value


@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.execute_update_status_action")
@patch("hope.apps.payment.services.payment_plan_services.PaymentPlanService.release_from_vision")
def test_process_callback_assigns_fc_releases_without_pg_send(
    mock_release,
    mock_send_to_pg,
    vision_payment_plan: PaymentPlan,
    matching_fc_items: list,
    django_assert_num_queries,
) -> None:
    VisionService.set_status(vision_payment_plan, VisionStatus.WAITING_FOR_CALLBACK)
    with (
        patch.object(PaymentPlan, "can_send_to_payment_gateway", new_callable=PropertyMock, return_value=False),
        django_assert_num_queries(6),
    ):
        VisionService.process_callback(
            vision_payment_plan,
            vision_payment_plan_id="VISION-1",
            vision_result="SUCCESS",
            fc_num="FC123",
        )

    mock_release.assert_called_once_with()
    mock_send_to_pg.assert_not_called()
    assert vision_payment_plan.vision_status == VisionStatus.RELEASED.value


@patch("hope.contrib.vision.tasks.VisionAPI")
def test_send_payment_plan_to_vision_task_calls_api(
    mock_vision_api,
    vision_enabled_payment_plan: PaymentPlan,
) -> None:
    job = MagicMock(config={"payment_plan_id": str(vision_enabled_payment_plan.pk)})

    send_payment_plan_to_vision_async_task_action(job)

    sent_payment_plan = mock_vision_api.return_value.send_payment_plan.call_args.args[0]
    assert sent_payment_plan.pk == vision_enabled_payment_plan.pk


@patch("hope.contrib.vision.tasks.VisionAPI")
def test_send_payment_plan_to_vision_task_skips_ineligible_plan(
    mock_vision_api,
    vision_disabled_payment_plan: PaymentPlan,
    django_assert_num_queries,
) -> None:
    job = MagicMock(config={"payment_plan_id": str(vision_disabled_payment_plan.pk)})

    with django_assert_num_queries(2):
        send_payment_plan_to_vision_async_task_action(job)

    mock_vision_api.assert_not_called()


@patch("hope.contrib.vision.tasks.VisionAPI")
def test_send_payment_plan_to_vision_task_records_failure(
    mock_vision_api,
    vision_enabled_payment_plan: PaymentPlan,
) -> None:
    mock_vision_api.side_effect = VisionAPIMissingCredentialsError("Missing credentials")
    job = MagicMock(config={"payment_plan_id": str(vision_enabled_payment_plan.pk)})

    with pytest.raises(VisionAPIMissingCredentialsError):
        send_payment_plan_to_vision_async_task_action(job)

    vision_enabled_payment_plan.refresh_from_db()
    assert vision_enabled_payment_plan.vision_status == VisionStatus.SEND_FAILED.value


@patch("hope.contrib.vision.tasks.VisionAPI")
def test_send_payment_plan_to_vision_task_does_not_duplicate_persisted_failure_log(
    mock_vision_api,
    vision_enabled_payment_plan: PaymentPlan,
    django_assert_num_queries,
) -> None:
    def persist_failure_then_raise(payment_plan: PaymentPlan) -> None:
        persisted_payment_plan = PaymentPlan.objects.get(pk=payment_plan.pk)
        persisted_payment_plan.internal_data = {
            "vision": {
                "status": VisionStatus.SEND_FAILED.value,
                "log": [{"type": VisionLogEntryType.API_CALL.value}],
            }
        }
        PaymentPlan.objects.filter(pk=persisted_payment_plan.pk).update(
            internal_data=persisted_payment_plan.internal_data
        )
        raise VisionAPIError("Vision request failed")

    mock_vision_api.return_value.send_payment_plan.side_effect = persist_failure_then_raise
    job = MagicMock(config={"payment_plan_id": str(vision_enabled_payment_plan.pk)})

    with django_assert_num_queries(22), pytest.raises(VisionAPIError):
        send_payment_plan_to_vision_async_task_action(job)

    vision_enabled_payment_plan.refresh_from_db()
    assert vision_enabled_payment_plan.vision_data["log"] == [{"type": VisionLogEntryType.API_CALL.value}]


@patch("hope.contrib.vision.tasks.VisionAPI")
def test_send_payment_plan_to_vision_task_preserves_completed_callback_state(
    mock_vision_api,
    vision_enabled_payment_plan: PaymentPlan,
) -> None:
    def complete_callback_then_fail(payment_plan: PaymentPlan) -> None:
        persisted_payment_plan = PaymentPlan.objects.get(pk=payment_plan.pk)
        persisted_payment_plan.status = PaymentPlan.Status.ACCEPTED
        persisted_payment_plan.internal_data = {
            "vision": {
                "status": VisionStatus.RELEASED.value,
                "vision_id": "VISION-1",
                "fc_num": "FC123",
            }
        }
        persisted_payment_plan.save(update_fields=["status", "internal_data"])
        raise VisionAPIError("Request timed out after callback")

    mock_vision_api.return_value.send_payment_plan.side_effect = complete_callback_then_fail
    job = MagicMock(config={"payment_plan_id": str(vision_enabled_payment_plan.pk)})

    with pytest.raises(VisionAPIError):
        send_payment_plan_to_vision_async_task_action(job)

    vision_enabled_payment_plan.refresh_from_db()
    assert vision_enabled_payment_plan.vision_status == VisionStatus.RELEASED.value


@patch("hope.contrib.vision.tasks.AsyncJob.requeue")
def test_send_payment_plan_to_vision_task_requeues_async_job(
    mock_requeue,
    vision_payment_plan: PaymentPlan,
    django_assert_num_queries,
) -> None:
    expected_job = MagicMock(spec=AsyncJob)
    mock_requeue.return_value = expected_job

    with django_assert_num_queries(0):
        job = send_payment_plan_to_vision_async_task(vision_payment_plan, str(vision_payment_plan.created_by_id))

    assert job == expected_job
    mock_requeue.assert_called_once_with(
        instance=vision_payment_plan,
        owner_id=str(vision_payment_plan.created_by_id),
        job_name="send_payment_plan_to_vision_async_task",
        action="hope.contrib.vision.tasks.send_payment_plan_to_vision_async_task_action",
        config={"payment_plan_id": str(vision_payment_plan.pk)},
        group_key="payment",
        description=f"Send payment plan {vision_payment_plan.pk} to Vision",
    )
