from __future__ import annotations

from django.utils import timezone
from viewflow import fsm

from hope.models.follow_up_instruction import FollowUpInstruction
from hope.models.payment_list import PaymentList
from hope.models.payment_plan import PaymentPlan


class PaymentListFlow:
    status = fsm.State(PaymentList.Status)

    background_action_status = fsm.State(PaymentList.BackgroundActionStatus)

    build_status = fsm.State(PaymentList.BuildStatus)

    def __init__(self, payment_list: "PaymentList"):
        self.payment_list = payment_list

    # Looks unused, but viewflow calls this getter/setter pair on every status_* transition.
    @status.setter()
    def _set_status(self, value: str) -> None:
        self.payment_list.status = value

    @status.getter()
    def _get_status(self) -> str:
        return self.payment_list.status

    # Looks unused, but viewflow calls this getter/setter pair on every background_action_status_* transition.
    @background_action_status.setter()
    def _set_background_action_status(self, value: str | None) -> None:
        self.payment_list.background_action_status = value

    @background_action_status.getter()
    def _get_background_action_status(self) -> str | None:
        return self.payment_list.background_action_status

    # Looks unused, but viewflow calls this getter/setter pair on every build_status_* transition.
    @build_status.setter()
    def _set_build_status(self, value: str | None) -> None:
        self.payment_list.build_status = value

    @build_status.getter()
    def _get_build_status(self) -> str | None:
        return self.payment_list.build_status

    @background_action_status.transition(
        source=[None] + list(PaymentList.BACKGROUND_ACTION_ERROR_STATES),
        target=PaymentList.BackgroundActionStatus.XLSX_EXPORTING,
        conditions=[
            lambda obj: (
                obj.payment_list.status
                in [
                    obj.payment_list.Status.LOCKED,
                    obj.payment_list.Status.ACCEPTED,
                    obj.payment_list.Status.FINISHED,
                ]
            )
        ],
    )
    def background_action_status_xlsx_exporting(self) -> None:
        pass

    @background_action_status.transition(
        source=[
            PaymentList.BackgroundActionStatus.XLSX_EXPORTING,
            PaymentList.BackgroundActionStatus.XLSX_EXPORT_ERROR,
        ],
        target=PaymentList.BackgroundActionStatus.XLSX_EXPORT_ERROR,
        conditions=[
            lambda obj: (
                obj.payment_list.status
                in [
                    obj.payment_list.Status.LOCKED,
                    obj.payment_list.Status.ACCEPTED,
                    obj.payment_list.Status.FINISHED,
                ]
            )
        ],
    )
    def background_action_status_xlsx_export_error(self) -> None:
        pass

    @background_action_status.transition(
        source=[None] + list(PaymentList.BACKGROUND_ACTION_ERROR_STATES),
        target=PaymentList.BackgroundActionStatus.RULE_ENGINE_RUN,
        conditions=[lambda obj: obj.payment_list.status == obj.payment_list.Status.LOCKED],
    )
    def background_action_status_steficon_run(self) -> None:
        pass

    @background_action_status.transition(
        source=[
            PaymentList.BackgroundActionStatus.RULE_ENGINE_RUN,
            PaymentList.BackgroundActionStatus.RULE_ENGINE_ERROR,
        ],
        target=PaymentList.BackgroundActionStatus.RULE_ENGINE_ERROR,
        conditions=[lambda obj: obj.payment_list.status == obj.payment_list.Status.LOCKED],
    )
    def background_action_status_steficon_error(self) -> None:
        pass

    @background_action_status.transition(
        source=[None] + list(PaymentList.BACKGROUND_ACTION_ERROR_STATES),
        target=PaymentList.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS,
        conditions=[lambda obj: obj.payment_list.status == obj.payment_list.Status.LOCKED],
    )
    def background_action_status_xlsx_importing_entitlements(self) -> None:
        pass

    @background_action_status.transition(
        source=[None] + list(PaymentList.BACKGROUND_ACTION_ERROR_STATES),
        target=PaymentList.BackgroundActionStatus.IMPORTING_ENTITLEMENTS,
        conditions=[lambda obj: obj.payment_list.status == obj.payment_list.Status.LOCKED],
    )
    def background_action_status_importing_entitlements(self) -> None:
        pass

    @background_action_status.transition(
        source=[None] + list(PaymentList.BACKGROUND_ACTION_ERROR_STATES),
        target=PaymentList.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
        conditions=[
            lambda obj: (
                obj.payment_list.status
                in [
                    obj.payment_list.Status.LOCKED,
                    obj.payment_list.Status.ACCEPTED,
                    obj.payment_list.Status.FINISHED,
                ]
            )
        ],
    )
    def background_action_status_xlsx_importing_reconciliation(self) -> None:
        pass

    @background_action_status.transition(
        source=[
            PaymentList.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS,
            PaymentList.BackgroundActionStatus.IMPORTING_ENTITLEMENTS,
            PaymentList.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
            PaymentList.BackgroundActionStatus.XLSX_IMPORTING_FSP_EXTRA_FIELDS,
            PaymentList.BackgroundActionStatus.XLSX_IMPORT_ERROR,
        ],
        target=PaymentList.BackgroundActionStatus.XLSX_IMPORT_ERROR,
        conditions=[
            lambda obj: (
                obj.payment_list.status
                in [
                    obj.payment_list.Status.LOCKED_FSP,
                    obj.payment_list.Status.LOCKED,
                    obj.payment_list.Status.ACCEPTED,
                    obj.payment_list.Status.FINISHED,
                ]
            )
        ],
    )
    def background_action_status_xlsx_import_error(self) -> None:
        pass

    @background_action_status.transition(source=[None] + list(PaymentList.BackgroundActionStatus))
    def background_action_status_none(self) -> None:
        self.payment_list.background_action_status = None

    @background_action_status.transition(
        source=[
            None,
            PaymentList.BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR,
        ],
        target=PaymentList.BackgroundActionStatus.EXCLUDE_BENEFICIARIES,
        conditions=[
            lambda obj: (
                obj.payment_list.status
                in [
                    obj.payment_list.Status.OPEN,
                    obj.payment_list.Status.LOCKED,
                ]
            )
        ],
    )
    def background_action_status_excluding_beneficiaries(self) -> None:
        pass

    @background_action_status.transition(
        source=[
            PaymentList.BackgroundActionStatus.EXCLUDE_BENEFICIARIES,
            PaymentList.BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR,
        ],
        target=PaymentList.BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR,
        conditions=[
            lambda obj: (
                obj.payment_list.status
                in [
                    obj.payment_list.Status.OPEN,
                    obj.payment_list.Status.LOCKED,
                ]
            )
        ],
    )
    def background_action_status_exclude_beneficiaries_error(self) -> None:
        pass

    @background_action_status.transition(
        source=[
            None,
            PaymentList.BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY_ERROR,
        ],
        target=PaymentList.BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY,
        conditions=[lambda obj: obj.payment_list.status == obj.payment_list.Status.ACCEPTED],
    )
    def background_action_status_send_to_payment_gateway(self) -> None:
        pass

    @background_action_status.transition(
        source=[
            PaymentList.BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY,
            PaymentList.BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY_ERROR,
        ],
        target=PaymentList.BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY_ERROR,
        conditions=[lambda obj: obj.payment_list.status == obj.payment_list.Status.ACCEPTED],
    )
    def background_action_status_send_to_payment_gateway_error(self) -> None:
        pass

    @background_action_status.transition(
        source=[None] + list(PaymentList.BACKGROUND_ACTION_ERROR_STATES),
        target=PaymentList.BackgroundActionStatus.REBUILDING,
        conditions=[lambda obj: obj.payment_list.status == obj.payment_list.Status.ABORTED],
    )
    def background_action_status_rebuilding(self) -> None:
        pass

    @background_action_status.transition(
        source=[
            PaymentList.BackgroundActionStatus.REBUILDING,
            PaymentList.BackgroundActionStatus.REBUILD_ERROR,
        ],
        target=PaymentList.BackgroundActionStatus.REBUILD_ERROR,
        conditions=[lambda obj: obj.payment_list.status == obj.payment_list.Status.ABORTED],
    )
    def background_action_status_rebuild_error(self) -> None:
        pass

    # Build Status Transitions
    @build_status.transition(
        source=[None] + list(PaymentList.BuildStatus),
        target=PaymentList.BuildStatus.BUILD_STATUS_PENDING,
        conditions=[
            lambda obj: (
                obj.payment_list.status
                in [
                    obj.payment_list.Status.TP_OPEN,
                    obj.payment_list.Status.TP_LOCKED,
                    obj.payment_list.Status.TP_STEFICON_COMPLETED,
                    obj.payment_list.Status.TP_STEFICON_ERROR,
                    obj.payment_list.Status.DRAFT,
                    obj.payment_list.Status.OPEN,
                    obj.payment_list.Status.ABORTED,
                ]
            )
        ],
    )
    def build_status_pending(self) -> None:
        self.payment_list.built_at = timezone.now()

    @build_status.transition(
        source=[
            PaymentList.BuildStatus.BUILD_STATUS_PENDING,
            PaymentList.BuildStatus.BUILD_STATUS_FAILED,
            PaymentList.BuildStatus.BUILD_STATUS_OK,
        ],
        target=PaymentList.BuildStatus.BUILD_STATUS_BUILDING,
        conditions=[
            lambda obj: (
                obj.payment_list.status
                in [
                    obj.payment_list.Status.TP_OPEN,
                    obj.payment_list.Status.TP_LOCKED,
                    obj.payment_list.Status.TP_STEFICON_WAIT,
                    obj.payment_list.Status.TP_STEFICON_COMPLETED,
                    obj.payment_list.Status.TP_STEFICON_ERROR,
                    obj.payment_list.Status.OPEN,
                    obj.payment_list.Status.ABORTED,
                ]
            )
        ],
    )
    def build_status_building(self) -> None:
        self.payment_list.built_at = timezone.now()

    @build_status.transition(
        source=PaymentList.BuildStatus.BUILD_STATUS_BUILDING,
        target=PaymentList.BuildStatus.BUILD_STATUS_FAILED,
        conditions=[
            lambda obj: (
                obj.payment_list.status
                in [
                    obj.payment_list.Status.TP_OPEN,
                    obj.payment_list.Status.TP_LOCKED,
                    obj.payment_list.Status.TP_STEFICON_WAIT,
                    obj.payment_list.Status.TP_STEFICON_COMPLETED,
                    obj.payment_list.Status.TP_STEFICON_ERROR,
                    obj.payment_list.Status.OPEN,
                    obj.payment_list.Status.ABORTED,
                ]
            )
        ],
    )
    def build_status_failed(self) -> None:
        self.payment_list.built_at = timezone.now()

    @build_status.transition(
        source=PaymentList.BuildStatus.BUILD_STATUS_BUILDING,
        target=PaymentList.BuildStatus.BUILD_STATUS_OK,
        conditions=[
            lambda obj: (
                obj.payment_list.status
                in [
                    obj.payment_list.Status.TP_OPEN,
                    obj.payment_list.Status.TP_LOCKED,
                    obj.payment_list.Status.TP_STEFICON_COMPLETED,
                    obj.payment_list.Status.TP_STEFICON_ERROR,
                    obj.payment_list.Status.TP_STEFICON_WAIT,
                    obj.payment_list.Status.OPEN,
                    obj.payment_list.Status.ABORTED,
                ]
            )
        ],
    )
    def build_status_ok(self) -> None:
        self.payment_list.built_at = timezone.now()

    # Status Transitions
    @status.transition(
        source=PaymentList.Status.TP_OPEN,
        target=PaymentList.Status.TP_LOCKED,
    )
    def status_tp_lock(self) -> None:
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=[
            PaymentList.Status.TP_LOCKED,
            PaymentList.Status.TP_STEFICON_COMPLETED,
            PaymentList.Status.TP_STEFICON_ERROR,
        ],
        target=PaymentList.Status.TP_OPEN,
    )
    def status_tp_open(self) -> None:
        self.payment_list.payment_items(manager="all_objects").filter(is_removed=True).update(is_removed=False)
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=PaymentList.Status.OPEN,
        target=PaymentList.Status.LOCKED,
    )
    def status_lock(self) -> None:
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=PaymentList.Status.LOCKED,
        target=PaymentList.Status.OPEN,
    )
    def status_unlock(self) -> None:
        self.background_action_status_none()
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=PaymentList.Status.LOCKED_FSP,
        target=PaymentList.Status.LOCKED,
    )
    def status_unlock_fsp(self) -> None:
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=PaymentList.Status.LOCKED,
        target=PaymentList.Status.LOCKED_FSP,
    )
    def status_lock_fsp(self) -> None:
        self.background_action_status_none()
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=[
            PaymentList.Status.IN_APPROVAL,
            PaymentList.Status.IN_AUTHORIZATION,
            PaymentList.Status.IN_REVIEW,
        ],
        target=PaymentList.Status.LOCKED_FSP,
    )
    def status_reject(self) -> None:
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=PaymentList.Status.LOCKED_FSP,
        target=PaymentList.Status.IN_APPROVAL,
    )
    def status_send_to_approval(self) -> None:
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=PaymentList.Status.IN_APPROVAL,
        target=PaymentList.Status.IN_AUTHORIZATION,
    )
    def status_approve(self) -> None:
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=PaymentList.Status.IN_AUTHORIZATION,
        target=PaymentList.Status.IN_REVIEW,
    )
    def status_authorize(self) -> None:
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=PaymentList.Status.IN_REVIEW,
        target=PaymentList.Status.ACCEPTED,
    )
    def status_mark_as_reviewed(self) -> None:
        from hope.models.payment_verification_summary import PaymentVerificationSummary

        self.payment_list.status_date = timezone.now()

        if not hasattr(self.payment_list, "payment_verification_summary"):
            PaymentVerificationSummary.objects.create(payment_list=self.payment_list)

    @status.transition(
        source=[
            PaymentList.Status.ACCEPTED,
            PaymentList.Status.FINISHED,
            PaymentList.Status.READY_FOR_CLOSURE,
        ],
        target=PaymentList.Status.FINISHED,
    )
    def status_finished(self) -> None:
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=PaymentList.Status.FINISHED,
        target=PaymentList.Status.ACCEPTED,
    )
    def status_reopen_for_reconciliation(self) -> None:
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=PaymentList.Status.FINISHED,
        target=PaymentList.Status.READY_FOR_CLOSURE,
    )
    def status_ready_for_closure(self) -> None:
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=PaymentList.Status.READY_FOR_CLOSURE,
        target=PaymentList.Status.CLOSED,
    )
    def status_close(self) -> None:
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=[
            PaymentList.Status.TP_LOCKED,
            PaymentList.Status.TP_STEFICON_COMPLETED,
            PaymentList.Status.TP_STEFICON_ERROR,
            PaymentList.Status.OPEN,
        ],
        target=PaymentList.Status.DRAFT,
    )
    def status_draft(self) -> None:
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=PaymentList.Status.DRAFT,
        target=PaymentList.Status.OPEN,
    )
    def status_open(self) -> None:
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=[
            PaymentList.Status.OPEN,
            PaymentList.Status.LOCKED,
            PaymentList.Status.LOCKED_FSP,
            PaymentList.Status.IN_APPROVAL,
            PaymentList.Status.IN_AUTHORIZATION,
            PaymentList.Status.IN_REVIEW,
            PaymentList.Status.ACCEPTED,
        ],
        target=PaymentList.Status.ABORTED,
    )
    def status_abort(self) -> None:
        self.payment_list.status_date = timezone.now()

    @status.transition(
        source=PaymentList.Status.ABORTED,
        target=PaymentList.Status.OPEN,
    )
    def status_reactivate_abort(self) -> None:
        self.payment_list.status_date = timezone.now()


class PaymentPlanFlow:
    status = fsm.State(PaymentPlan.Status)

    def __init__(self, payment_plan: "PaymentPlan"):
        self.payment_plan = payment_plan

    @status.setter()
    def _set_status(self, value: str) -> None:
        self.payment_plan.status = value

    @status.getter()
    def _get_status(self) -> str:
        return self.payment_plan.status

    @status.transition(
        source=PaymentPlan.Status.OPEN,
        target=PaymentPlan.Status.LOCKED,
    )
    def status_lock(self) -> None:
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=PaymentPlan.Status.LOCKED,
        target=PaymentPlan.Status.OPEN,
    )
    def status_unlock(self) -> None:
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=PaymentPlan.Status.LOCKED,
        target=PaymentPlan.Status.IN_APPROVAL,
    )
    def status_send_for_approval(self) -> None:
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=PaymentPlan.Status.IN_APPROVAL,
        target=PaymentPlan.Status.IN_AUTHORIZATION,
    )
    def status_approve(self) -> None:
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=PaymentPlan.Status.IN_AUTHORIZATION,
        target=PaymentPlan.Status.IN_REVIEW,
    )
    def status_authorize(self) -> None:
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=PaymentPlan.Status.IN_REVIEW,
        target=PaymentPlan.Status.ACCEPTED,
    )
    def status_mark_as_reviewed(self) -> None:
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=[
            PaymentPlan.Status.IN_APPROVAL,
            PaymentPlan.Status.IN_AUTHORIZATION,
            PaymentPlan.Status.IN_REVIEW,
        ],
        target=PaymentPlan.Status.LOCKED,
    )
    def status_reject(self) -> None:
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=[
            PaymentPlan.Status.ACCEPTED,
            PaymentPlan.Status.FINISHED,
            PaymentPlan.Status.READY_FOR_CLOSURE,
        ],
        target=PaymentPlan.Status.FINISHED,
    )
    def status_finished(self) -> None:
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=PaymentPlan.Status.FINISHED,
        target=PaymentPlan.Status.ACCEPTED,
    )
    def status_reopen_for_reconciliation(self) -> None:
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=PaymentPlan.Status.FINISHED,
        target=PaymentPlan.Status.READY_FOR_CLOSURE,
    )
    def status_ready_for_closure(self) -> None:
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=PaymentPlan.Status.READY_FOR_CLOSURE,
        target=PaymentPlan.Status.CLOSED,
    )
    def status_close(self) -> None:
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=[
            PaymentPlan.Status.LOCKED,
            PaymentPlan.Status.IN_APPROVAL,
            PaymentPlan.Status.IN_AUTHORIZATION,
            PaymentPlan.Status.IN_REVIEW,
        ],
        target=PaymentPlan.Status.ABORTED,
    )
    def status_abort(self) -> None:
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=PaymentPlan.Status.ABORTED,
        target=PaymentPlan.Status.OPEN,
    )
    def status_reactivate_abort(self) -> None:
        self.payment_plan.status_date = timezone.now()


class FollowUpInstructionFlow:
    background_action_status = fsm.State(FollowUpInstruction.BackgroundActionStatus)

    def __init__(self, instruction: "FollowUpInstruction"):
        self.instruction = instruction

    # Looks unused, but viewflow calls this getter/setter pair on every background_action_status_* transition.
    @background_action_status.setter()
    def _set_background_action_status(self, value: str | None) -> None:
        self.instruction.background_action_status = value

    @background_action_status.getter()
    def _get_background_action_status(self) -> str | None:
        return self.instruction.background_action_status

    @background_action_status.transition(
        source=[None] + list(FollowUpInstruction.BACKGROUND_ACTION_ERROR_STATES),
        target=FollowUpInstruction.BackgroundActionStatus.XLSX_EXPORTING,
    )
    def background_action_status_xlsx_exporting(self) -> None:
        pass

    @background_action_status.transition(
        source=[
            FollowUpInstruction.BackgroundActionStatus.XLSX_EXPORTING,
            FollowUpInstruction.BackgroundActionStatus.XLSX_EXPORT_ERROR,
        ],
        target=FollowUpInstruction.BackgroundActionStatus.XLSX_EXPORT_ERROR,
    )
    def background_action_status_xlsx_export_error(self) -> None:
        pass

    @background_action_status.transition(
        source=[None] + list(FollowUpInstruction.BACKGROUND_ACTION_ERROR_STATES),
        target=FollowUpInstruction.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
    )
    def background_action_status_xlsx_importing_reconciliation(self) -> None:
        pass

    @background_action_status.transition(
        source=[
            FollowUpInstruction.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
            FollowUpInstruction.BackgroundActionStatus.XLSX_IMPORT_ERROR,
        ],
        target=FollowUpInstruction.BackgroundActionStatus.XLSX_IMPORT_ERROR,
    )
    def background_action_status_xlsx_import_error(self) -> None:
        pass

    @background_action_status.transition(source=[None] + list(FollowUpInstruction.BackgroundActionStatus))
    def background_action_status_none(self) -> None:
        self.instruction.background_action_status = None
