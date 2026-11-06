from unittest.mock import MagicMock, patch

from flags.models import FlagState
import pytest

from extras.test_utils.factories import (
    ApprovalProcessFactory,
    BusinessAreaFactory,
    FundsCommitmentHeaderFactory,
    FundsCommitmentItemFactory,
    PaymentListFactory,
    PaymentPlanFactory,
)
from hope.contrib.vision.api import VisionAPIError, VisionAPIMissingCredentialsError
from hope.contrib.vision.choices import VisionErrorCode, VisionStatus
from hope.contrib.vision.services import FundsCommitmentAssignmentError, VisionService
from hope.contrib.vision.tasks import (
    notify_payment_plan_status_to_vision_async_task,
    notify_payment_plan_status_to_vision_async_task_action,
    send_payment_plan_to_vision_async_task,
    send_payment_plan_to_vision_async_task_action,
)
from hope.models import AsyncJob, PaymentList, PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def vision_group() -> PaymentPlan:
    business_area = BusinessAreaFactory(vision_integration_active=True)
    FlagState.objects.update_or_create(
        name="VISION_INTEGRATION_ACTIVE",
        condition="boolean",
        defaults={"value": "True"},
    )
    plan = PaymentListFactory(
        business_area=business_area,
        program_cycle__program__business_area=business_area,
        status=PaymentList.Status.IN_REVIEW,
    )
    group = plan.payment_plan
    group.status = PaymentPlan.Status.IN_REVIEW
    group.save(update_fields=["status"])
    ApprovalProcessFactory(payment_plan=group)
    return group


@pytest.fixture
def matching_headers(vision_group: PaymentPlan) -> list:
    headers = [
        FundsCommitmentHeaderFactory(funds_commitment_number="FC123"),
        FundsCommitmentHeaderFactory(funds_commitment_number="FC456"),
    ]
    for header in headers:
        FundsCommitmentItemFactory(funds_commitment_header=header, office=vision_group.business_area)
    return headers


@pytest.fixture
def group_waiting_for_vision(vision_group: PaymentPlan) -> PaymentPlan:
    VisionService.set_status(vision_group, VisionStatus.WAITING_FOR_CALLBACK)
    vision_group.save(update_fields=["internal_data"])
    return vision_group


@pytest.fixture
def group_with_failed_fc(group_waiting_for_vision: PaymentPlan) -> PaymentPlan:
    VisionService.set_status(group_waiting_for_vision, VisionStatus.FC_NOT_FOUND)
    group_waiting_for_vision.save(update_fields=["internal_data"])
    return group_waiting_for_vision


@pytest.fixture
def disabled_vision_group(group_waiting_for_vision: PaymentPlan) -> PaymentPlan:
    FlagState.objects.filter(name="VISION_INTEGRATION_ACTIVE", condition="boolean").update(value="False")
    return group_waiting_for_vision


@pytest.fixture
def shared_header_group(vision_group: PaymentPlan, matching_headers: list) -> PaymentPlan:
    other = PaymentListFactory()
    matching_headers[0].payment_plans.add(other.payment_plan)
    return other.payment_plan


@pytest.fixture
def wrong_office_header() -> None:
    header = FundsCommitmentHeaderFactory(funds_commitment_number="FC123")
    FundsCommitmentItemFactory(funds_commitment_header=header, office=None)


@pytest.fixture
def follow_up_group(vision_group: PaymentPlan) -> PaymentPlan:
    return PaymentPlanFactory(
        cycle=vision_group.cycle,
        source_payment_plan=vision_group,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
        status=PaymentPlan.Status.IN_REVIEW,
    )


def test_malformed_group_vision_data_is_replaced(vision_group: PaymentPlan, django_assert_num_queries) -> None:
    vision_group.internal_data = {"vision": "invalid"}

    with django_assert_num_queries(0):
        data = VisionService.vision_data(vision_group)

    assert data == {}
    assert vision_group.vision_status == VisionStatus.NOT_SENT.value


def test_group_vision_attempt_reset_preserves_log(group_waiting_for_vision: PaymentPlan) -> None:
    VisionService.vision_data(group_waiting_for_vision).update(
        sent=True, vision_id="VISION-1", fc_numbers=["FC123"], log=[{"type": "api-call"}]
    )

    VisionService.invalidate_attempt(group_waiting_for_vision)

    assert group_waiting_for_vision.vision_data == {
        "status": VisionStatus.NOT_SENT.value,
        "log": [{"type": "api-call"}],
    }


def test_callback_assigns_multiple_headers(
    vision_group: PaymentPlan, matching_headers: list, django_assert_num_queries
) -> None:
    VisionService.assign_funds_commitment_headers_from_callback(vision_group, ["FC123", "FC456"])

    with django_assert_num_queries(1):
        assigned = set(vision_group.funds_commitment_headers.all())
    assert assigned == set(matching_headers)


def test_callback_rejects_missing_header_without_partial_assignment(
    vision_group: PaymentPlan, matching_headers: list
) -> None:
    with pytest.raises(FundsCommitmentAssignmentError) as error:
        VisionService.assign_funds_commitment_headers_from_callback(vision_group, ["FC123", "UNKNOWN"])

    assert error.value.status == VisionStatus.FC_NOT_FOUND
    assert not vision_group.funds_commitment_headers.exists()


def test_callback_rejects_header_from_another_business_area(
    vision_group: PaymentPlan, wrong_office_header: None
) -> None:
    with pytest.raises(FundsCommitmentAssignmentError) as error:
        VisionService.assign_funds_commitment_headers_from_callback(vision_group, ["FC123"])

    assert error.value.status == VisionStatus.FC_NOT_FOUND


def test_callback_can_reuse_header_assigned_to_another_group(
    vision_group: PaymentPlan, matching_headers: list, shared_header_group: PaymentPlan
) -> None:
    VisionService.assign_funds_commitment_headers_from_callback(vision_group, ["FC123"])

    assert set(matching_headers[0].payment_plans.all()) == {vision_group, shared_header_group}


@pytest.mark.parametrize("current_status", [VisionStatus.WAITING_FOR_CALLBACK, VisionStatus.PP_CREATED])
def test_creation_callback_records_group_acknowledgement(
    vision_group: PaymentPlan, current_status: VisionStatus
) -> None:
    VisionService.set_status(vision_group, current_status)

    failed = VisionService.process_callback(
        vision_group, vision_payment_plan_id="VISION-1", vision_result="SUCCESS", fc_numbers=[]
    )

    assert failed is False
    assert vision_group.status == PaymentPlan.Status.IN_REVIEW
    assert vision_group.vision_data == {
        "sent": True,
        "vision_id": "VISION-1",
        "status": VisionStatus.PP_CREATED.value,
    }


def test_callback_records_vision_error(group_waiting_for_vision: PaymentPlan) -> None:
    failed = VisionService.process_callback(
        group_waiting_for_vision,
        vision_payment_plan_id="VISION-1",
        vision_result="ERROR",
        fc_numbers=["FC123"],
    )

    assert failed is False
    assert group_waiting_for_vision.vision_status == VisionStatus.CALLBACK_FAILED.value
    assert group_waiting_for_vision.vision_data["fc_numbers"] == ["FC123"]
    assert group_waiting_for_vision.vision_data["error_code"] == VisionErrorCode.VISION_STATUS_FAILED.value


def test_callback_records_missing_fc(group_waiting_for_vision: PaymentPlan) -> None:
    failed = VisionService.process_callback(
        group_waiting_for_vision,
        vision_payment_plan_id="VISION-1",
        vision_result="SUCCESS",
        fc_numbers=["UNKNOWN"],
    )

    assert failed is True
    assert group_waiting_for_vision.vision_status == VisionStatus.FC_NOT_FOUND.value
    assert group_waiting_for_vision.sent_to_vision is True


def test_corrected_callback_releases_group(
    group_with_failed_fc: PaymentPlan, matching_headers: list, monkeypatch
) -> None:
    monkeypatch.setattr(
        "hope.apps.payment.services.payment_plan_services.send_payment_plan_notification_emails_async_task",
        lambda *args: None,
    )

    failed = VisionService.process_callback(
        group_with_failed_fc,
        vision_payment_plan_id="VISION-1",
        vision_result="SUCCESS",
        fc_numbers=["FC123"],
    )

    group_with_failed_fc.refresh_from_db()
    assert failed is False
    assert group_with_failed_fc.status == PaymentPlan.Status.ACCEPTED
    assert group_with_failed_fc.vision_status == VisionStatus.RELEASED.value
    assert list(group_with_failed_fc.funds_commitment_headers.all()) == [matching_headers[0]]


def test_unsolicited_callback_does_not_start_group_workflow(vision_group: PaymentPlan) -> None:
    failed = VisionService.process_callback(
        vision_group, vision_payment_plan_id="VISION-1", vision_result="SUCCESS", fc_numbers=["FC123"]
    )

    assert failed is False
    assert vision_group.vision_data == {}


def test_disabled_vision_callback_does_not_change_group(disabled_vision_group: PaymentPlan) -> None:
    failed = VisionService.process_callback(
        disabled_vision_group, vision_payment_plan_id="VISION-1", vision_result="SUCCESS", fc_numbers=["FC123"]
    )

    assert failed is False
    assert disabled_vision_group.vision_status == VisionStatus.WAITING_FOR_CALLBACK.value


def test_follow_up_group_does_not_request_new_fc(follow_up_group: PaymentPlan) -> None:
    assert follow_up_group.vision_managed is False
    assert follow_up_group.can_send_to_vision is False


def test_manual_recovery_available_after_fc_failure(group_with_failed_fc: PaymentPlan) -> None:
    assert VisionService.can_recover_payment_plan_with_funds_commitment_headers(group_with_failed_fc) is True


def test_manual_recovery_rejects_group_without_active_attempt(vision_group: PaymentPlan) -> None:
    with pytest.raises(FundsCommitmentAssignmentError) as error:
        VisionService.recover_payment_plan_with_funds_commitment_headers(vision_group, [])

    assert error.value.status == VisionStatus.CALLBACK_FAILED
    assert error.value.error_code == VisionErrorCode.FC_CONFLICT


def test_manual_recovery_releases_group(group_with_failed_fc: PaymentPlan, matching_headers: list, monkeypatch) -> None:
    monkeypatch.setattr(
        "hope.apps.payment.services.payment_plan_services.send_payment_plan_notification_emails_async_task",
        lambda *args: None,
    )

    VisionService.recover_payment_plan_with_funds_commitment_headers(group_with_failed_fc, [matching_headers[0]])

    group_with_failed_fc.refresh_from_db()
    assert group_with_failed_fc.status == PaymentPlan.Status.ACCEPTED
    assert group_with_failed_fc.vision_status == VisionStatus.RELEASED.value


@patch("hope.contrib.vision.tasks.VisionAPI")
def test_group_send_task_calls_api(mock_vision_api, vision_group: PaymentPlan) -> None:
    job = MagicMock(config={"payment_plan_id": str(vision_group.pk)})

    send_payment_plan_to_vision_async_task_action(job)

    sent_group = mock_vision_api.return_value.send_payment_plan.call_args.args[0]
    assert sent_group.pk == vision_group.pk


@patch("hope.contrib.vision.tasks.VisionAPI")
def test_group_send_task_skips_ineligible_group(mock_vision_api, disabled_vision_group: PaymentPlan) -> None:
    job = MagicMock(config={"payment_plan_id": str(disabled_vision_group.pk)})

    send_payment_plan_to_vision_async_task_action(job)

    mock_vision_api.assert_not_called()


@patch("hope.contrib.vision.tasks.VisionAPI")
def test_group_send_task_records_failure(mock_vision_api, vision_group: PaymentPlan) -> None:
    mock_vision_api.side_effect = VisionAPIMissingCredentialsError("Missing credentials")
    job = MagicMock(config={"payment_plan_id": str(vision_group.pk)})

    with pytest.raises(VisionAPIMissingCredentialsError):
        send_payment_plan_to_vision_async_task_action(job)

    vision_group.refresh_from_db()
    assert vision_group.vision_status == VisionStatus.SEND_FAILED.value


@patch("hope.contrib.vision.tasks.VisionAPI")
def test_group_send_task_preserves_completed_callback(mock_vision_api, vision_group: PaymentPlan) -> None:
    def complete_then_fail(group: PaymentPlan) -> None:
        PaymentPlan.objects.filter(pk=group.pk).update(
            status=PaymentPlan.Status.ACCEPTED,
            internal_data={"vision": {"status": VisionStatus.RELEASED.value, "vision_id": "VISION-1"}},
        )
        raise VisionAPIError("Request timed out after callback")

    mock_vision_api.return_value.send_payment_plan.side_effect = complete_then_fail
    job = MagicMock(config={"payment_plan_id": str(vision_group.pk)})

    with pytest.raises(VisionAPIError):
        send_payment_plan_to_vision_async_task_action(job)

    vision_group.refresh_from_db()
    assert vision_group.vision_status == VisionStatus.RELEASED.value


@patch("hope.contrib.vision.tasks.VisionAPI")
def test_group_notification_task_calls_api(mock_vision_api, vision_group: PaymentPlan) -> None:
    job = MagicMock(config={"payment_plan_id": str(vision_group.pk), "vision_status": "ABORTED"})

    notify_payment_plan_status_to_vision_async_task_action(job)

    notified_group, status = mock_vision_api.return_value.notify_payment_plan_status.call_args.args
    assert notified_group.pk == vision_group.pk
    assert status == "ABORTED"


@patch("hope.models.AsyncJob.requeue")
def test_group_notification_queues_job(mock_requeue, vision_group: PaymentPlan) -> None:
    notify_payment_plan_status_to_vision_async_task(vision_group, "user-id", "REJECTED")

    mock_requeue.assert_called_once_with(
        instance=vision_group,
        owner_id="user-id",
        job_name="notify_payment_plan_rejected_to_vision",
        action="hope.contrib.vision.tasks.notify_payment_plan_status_to_vision_async_task_action",
        config={"payment_plan_id": str(vision_group.pk), "vision_status": "REJECTED"},
        group_key="payment",
        description=f"Notify Vision that Payment Plan {vision_group.pk} is REJECTED",
    )


@patch("hope.models.AsyncJob.requeue")
def test_group_send_task_queues_job(mock_requeue, vision_group: PaymentPlan) -> None:
    expected_job = MagicMock(spec=AsyncJob)
    mock_requeue.return_value = expected_job

    job = send_payment_plan_to_vision_async_task(vision_group, "user-id")

    assert job == expected_job
    mock_requeue.assert_called_once_with(
        instance=vision_group,
        owner_id="user-id",
        job_name="send_payment_plan_to_vision_async_task",
        action="hope.contrib.vision.tasks.send_payment_plan_to_vision_async_task_action",
        config={"payment_plan_id": str(vision_group.pk)},
        group_key="payment",
        description=f"Send Payment Plan {vision_group.pk} to Vision",
    )
