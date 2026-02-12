from typing import TYPE_CHECKING

from django.utils import timezone
from viewflow import fsm

if TYPE_CHECKING:
    from hope.models.payment_plan import PaymentPlan


def _get_payment_plan_model():
    """Lazy import to avoid circular dependencies."""
    from hope.models.payment_plan import PaymentPlan

    return PaymentPlan


class PaymentPlanFlow:
    status = fsm.State(lambda: _get_payment_plan_model().Status)

    background_action_status = fsm.State(lambda: _get_payment_plan_model().BackgroundActionStatus)

    build_status = fsm.State(lambda: _get_payment_plan_model().BuildStatus)

    def __init__(self, payment_plan: "PaymentPlan"):
        self.payment_plan = payment_plan

    @status.setter()
    def _set_status(self, value):
        self.payment_plan.status = value

    @status.getter()
    def _get_status(self):
        return self.payment_plan.status

    @background_action_status.setter()
    def _set_background_action_status(self, value):
        self.payment_plan.background_action_status = value

    @background_action_status.getter()
    def _get_background_action_status(self):
        return self.payment_plan.background_action_status

    @build_status.setter()
    def _set_build_status(self, value):
        self.payment_plan.build_status = value

    @build_status.getter()
    def _get_build_status(self):
        return self.payment_plan.build_status

    @background_action_status.transition(
        source=[None] + list(_get_payment_plan_model().BACKGROUND_ACTION_ERROR_STATES),
        target=_get_payment_plan_model().BackgroundActionStatus.XLSX_EXPORTING,
        conditions=[
            lambda obj: obj.payment_plan.status
            in [
                obj.payment_plan.Status.LOCKED,
                obj.payment_plan.Status.ACCEPTED,
                obj.payment_plan.Status.FINISHED,
            ]
        ],
    )
    def background_action_status_xlsx_exporting(self):
        pass

    @background_action_status.transition(
        source=[
            _get_payment_plan_model().BackgroundActionStatus.XLSX_EXPORTING,
            _get_payment_plan_model().BackgroundActionStatus.XLSX_EXPORT_ERROR,
        ],
        target=_get_payment_plan_model().BackgroundActionStatus.XLSX_EXPORT_ERROR,
        conditions=[
            lambda obj: obj.payment_plan.status
            in [
                obj.payment_plan.Status.LOCKED,
                obj.payment_plan.Status.ACCEPTED,
                obj.payment_plan.Status.FINISHED,
            ]
        ],
    )
    def background_action_status_xlsx_export_error(self):
        pass

    @background_action_status.transition(
        source=[None] + list(_get_payment_plan_model().BACKGROUND_ACTION_ERROR_STATES),
        target=_get_payment_plan_model().BackgroundActionStatus.RULE_ENGINE_RUN,
        conditions=[lambda obj: obj.payment_plan.status == obj.payment_plan.Status.LOCKED],
    )
    def background_action_status_steficon_run(self):
        pass

    @background_action_status.transition(
        source=[
            _get_payment_plan_model().BackgroundActionStatus.RULE_ENGINE_RUN,
            _get_payment_plan_model().BackgroundActionStatus.RULE_ENGINE_ERROR,
        ],
        target=_get_payment_plan_model().BackgroundActionStatus.RULE_ENGINE_ERROR,
        conditions=[lambda obj: obj.payment_plan.status == obj.payment_plan.Status.LOCKED],
    )
    def background_action_status_steficon_error(self):
        pass

    @background_action_status.transition(
        source=[None] + list(_get_payment_plan_model().BACKGROUND_ACTION_ERROR_STATES),
        target=_get_payment_plan_model().BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS,
        conditions=[lambda obj: obj.payment_plan.status == obj.payment_plan.Status.LOCKED],
    )
    def background_action_status_xlsx_importing_entitlements(self):
        pass

    @background_action_status.transition(
        source=[None] + list(_get_payment_plan_model().BACKGROUND_ACTION_ERROR_STATES),
        target=_get_payment_plan_model().BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
        conditions=[
            lambda obj: obj.payment_plan.status
            in [
                obj.payment_plan.Status.LOCKED,
                obj.payment_plan.Status.ACCEPTED,
                obj.payment_plan.Status.FINISHED,
            ]
        ],
    )
    def background_action_status_xlsx_importing_reconciliation(self):
        pass

    @background_action_status.transition(
        source=[
            _get_payment_plan_model().BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS,
            _get_payment_plan_model().BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
            _get_payment_plan_model().BackgroundActionStatus.XLSX_IMPORT_ERROR,
        ],
        target=_get_payment_plan_model().BackgroundActionStatus.XLSX_IMPORT_ERROR,
        conditions=[
            lambda obj: obj.payment_plan.status
            in [
                obj.payment_plan.Status.LOCKED,
                obj.payment_plan.Status.ACCEPTED,
                obj.payment_plan.Status.FINISHED,
            ]
        ],
    )
    def background_action_status_xlsx_import_error(self):
        pass

    @background_action_status.transition(
        source=[None] + list(_get_payment_plan_model().BackgroundActionStatus), target=None
    )
    def background_action_status_none(self):
        self.payment_plan.background_action_status = None

    @background_action_status.transition(
        source=[
            None,
            _get_payment_plan_model().BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR,
        ],
        target=_get_payment_plan_model().BackgroundActionStatus.EXCLUDE_BENEFICIARIES,
        conditions=[
            lambda obj: obj.payment_plan.status
            in [
                obj.payment_plan.Status.OPEN,
                obj.payment_plan.Status.LOCKED,
            ]
        ],
    )
    def background_action_status_excluding_beneficiaries(self):
        pass

    @background_action_status.transition(
        source=[
            _get_payment_plan_model().BackgroundActionStatus.EXCLUDE_BENEFICIARIES,
            _get_payment_plan_model().BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR,
        ],
        target=_get_payment_plan_model().BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR,
        conditions=[
            lambda obj: obj.payment_plan.status
            in [
                obj.payment_plan.Status.OPEN,
                obj.payment_plan.Status.LOCKED,
            ]
        ],
    )
    def background_action_status_exclude_beneficiaries_error(self):
        pass

    @background_action_status.transition(
        source=[
            None,
            _get_payment_plan_model().BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY_ERROR,
        ],
        target=_get_payment_plan_model().BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY,
        conditions=[lambda obj: obj.payment_plan.status == obj.payment_plan.Status.ACCEPTED],
    )
    def background_action_status_send_to_payment_gateway(self):
        pass

    @background_action_status.transition(
        source=[
            _get_payment_plan_model().BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY,
            _get_payment_plan_model().BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY_ERROR,
        ],
        target=_get_payment_plan_model().BackgroundActionStatus.SEND_TO_PAYMENT_GATEWAY_ERROR,
        conditions=[lambda obj: obj.payment_plan.status == obj.payment_plan.Status.ACCEPTED],
    )
    def background_action_status_send_to_payment_gateway_error(self):
        pass

    # Build Status Transitions
    @build_status.transition(
        source=[None] + list(_get_payment_plan_model().BuildStatus),
        target=_get_payment_plan_model().BuildStatus.BUILD_STATUS_PENDING,
        conditions=[
            lambda obj: obj.payment_plan.status
            in [
                obj.payment_plan.Status.TP_OPEN,
                obj.payment_plan.Status.TP_LOCKED,
                obj.payment_plan.Status.TP_STEFICON_COMPLETED,
                obj.payment_plan.Status.TP_STEFICON_ERROR,
                obj.payment_plan.Status.DRAFT,
                obj.payment_plan.Status.OPEN,
            ]
        ],
    )
    def build_status_pending(self):
        self.payment_plan.built_at = timezone.now()

    @build_status.transition(
        source=[
            _get_payment_plan_model().BuildStatus.BUILD_STATUS_PENDING,
            _get_payment_plan_model().BuildStatus.BUILD_STATUS_FAILED,
            _get_payment_plan_model().BuildStatus.BUILD_STATUS_OK,
        ],
        target=_get_payment_plan_model().BuildStatus.BUILD_STATUS_BUILDING,
        conditions=[
            lambda obj: obj.payment_plan.status
            in [
                obj.payment_plan.Status.TP_OPEN,
                obj.payment_plan.Status.TP_LOCKED,
                obj.payment_plan.Status.TP_STEFICON_WAIT,
                obj.payment_plan.Status.TP_STEFICON_COMPLETED,
                obj.payment_plan.Status.TP_STEFICON_ERROR,
                obj.payment_plan.Status.OPEN,
            ]
        ],
    )
    def build_status_building(self):
        self.payment_plan.built_at = timezone.now()

    @build_status.transition(
        source=_get_payment_plan_model().BuildStatus.BUILD_STATUS_BUILDING,
        target=_get_payment_plan_model().BuildStatus.BUILD_STATUS_FAILED,
        conditions=[
            lambda obj: obj.payment_plan.status
            in [
                obj.payment_plan.Status.TP_OPEN,
                obj.payment_plan.Status.TP_LOCKED,
                obj.payment_plan.Status.TP_STEFICON_WAIT,
                obj.payment_plan.Status.TP_STEFICON_COMPLETED,
                obj.payment_plan.Status.TP_STEFICON_ERROR,
            ]
        ],
    )
    def build_status_failed(self):
        self.payment_plan.built_at = timezone.now()

    @build_status.transition(
        source=_get_payment_plan_model().BuildStatus.BUILD_STATUS_BUILDING,
        target=_get_payment_plan_model().BuildStatus.BUILD_STATUS_OK,
        conditions=[
            lambda obj: obj.payment_plan.status
            in [
                obj.payment_plan.Status.TP_OPEN,
                obj.payment_plan.Status.TP_LOCKED,
                obj.payment_plan.Status.TP_STEFICON_COMPLETED,
                obj.payment_plan.Status.TP_STEFICON_ERROR,
                obj.payment_plan.Status.TP_STEFICON_WAIT,
            ]
        ],
    )
    def build_status_ok(self):
        self.payment_plan.built_at = timezone.now()

    # Status Transitions
    @status.transition(
        source=_get_payment_plan_model().Status.TP_OPEN,
        target=_get_payment_plan_model().Status.TP_LOCKED,
    )
    def status_tp_lock(self):
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=[
            _get_payment_plan_model().Status.TP_LOCKED,
            _get_payment_plan_model().Status.TP_STEFICON_COMPLETED,
            _get_payment_plan_model().Status.TP_STEFICON_ERROR,
        ],
        target=_get_payment_plan_model().Status.TP_OPEN,
    )
    def status_tp_open(self):
        self.payment_plan.payment_items(manager="all_objects").filter(is_removed=True).update(is_removed=False)
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=_get_payment_plan_model().Status.OPEN,
        target=_get_payment_plan_model().Status.LOCKED,
    )
    def status_lock(self):
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=_get_payment_plan_model().Status.LOCKED,
        target=_get_payment_plan_model().Status.OPEN,
    )
    def status_unlock(self):
        self.background_action_status_none()
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=_get_payment_plan_model().Status.LOCKED_FSP,
        target=_get_payment_plan_model().Status.LOCKED,
    )
    def status_unlock_fsp(self):
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=_get_payment_plan_model().Status.LOCKED,
        target=_get_payment_plan_model().Status.LOCKED_FSP,
    )
    def status_lock_fsp(self):
        self.background_action_status_none()
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=[
            _get_payment_plan_model().Status.IN_APPROVAL,
            _get_payment_plan_model().Status.IN_AUTHORIZATION,
            _get_payment_plan_model().Status.IN_REVIEW,
        ],
        target=_get_payment_plan_model().Status.LOCKED_FSP,
    )
    def status_reject(self):
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=_get_payment_plan_model().Status.LOCKED_FSP,
        target=_get_payment_plan_model().Status.IN_APPROVAL,
    )
    def status_send_to_approval(self):
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=_get_payment_plan_model().Status.IN_APPROVAL,
        target=_get_payment_plan_model().Status.IN_AUTHORIZATION,
    )
    def status_approve(self):
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=_get_payment_plan_model().Status.IN_AUTHORIZATION,
        target=_get_payment_plan_model().Status.IN_REVIEW,
    )
    def status_authorize(self):
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=_get_payment_plan_model().Status.IN_REVIEW,
        target=_get_payment_plan_model().Status.ACCEPTED,
    )
    def status_mark_as_reviewed(self):
        from hope.models.payment_verification_summary import PaymentVerificationSummary

        self.payment_plan.status_date = timezone.now()

        if not hasattr(self.payment_plan, "payment_verification_summary"):
            PaymentVerificationSummary.objects.create(payment_plan=self.payment_plan)

    @status.transition(
        source=[
            _get_payment_plan_model().Status.ACCEPTED,
            _get_payment_plan_model().Status.FINISHED,
        ],
        target=_get_payment_plan_model().Status.FINISHED,
    )
    def status_finished(self):
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=_get_payment_plan_model().Status.FINISHED,
        target=_get_payment_plan_model().Status.CLOSED,
    )
    def status_close(self):
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=[
            _get_payment_plan_model().Status.TP_LOCKED,
            _get_payment_plan_model().Status.TP_STEFICON_COMPLETED,
            _get_payment_plan_model().Status.TP_STEFICON_ERROR,
            _get_payment_plan_model().Status.OPEN,
        ],
        target=_get_payment_plan_model().Status.DRAFT,
    )
    def status_draft(self):
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=_get_payment_plan_model().Status.DRAFT,
        target=_get_payment_plan_model().Status.OPEN,
    )
    def status_open(self):
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=[
            _get_payment_plan_model().Status.OPEN,
            _get_payment_plan_model().Status.LOCKED,
            _get_payment_plan_model().Status.LOCKED_FSP,
            _get_payment_plan_model().Status.IN_APPROVAL,
            _get_payment_plan_model().Status.IN_AUTHORIZATION,
            _get_payment_plan_model().Status.IN_REVIEW,
            _get_payment_plan_model().Status.ACCEPTED,
        ],
        target=_get_payment_plan_model().Status.ABORTED,
    )
    def status_abort(self):
        self.payment_plan.status_date = timezone.now()

    @status.transition(
        source=_get_payment_plan_model().Status.ABORTED,
        target=_get_payment_plan_model().Status.OPEN,
    )
    def status_reactivate_abort(self):
        self.payment_plan.status_date = timezone.now()
        self.payment_plan.build_status = self.payment_plan.BuildStatus.BUILD_STATUS_PENDING
