import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, cast

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from hope.apps.activity_log.utils import copy_model_object
from hope.apps.payment.celery_tasks import (
    recalculate_owner_exchange_rate_async_task,
    send_payment_plan_notification_emails_async_task,
)
from hope.apps.payment.flows import PaymentListFlow, PaymentPlanFlow
from hope.apps.payment.services.payment_list_services import (
    ACTION_TO_APPROVAL_TYPE,
    STAGE_REACHED_NOTIFICATION,
    PaymentListService,
    record_stage_reached,
    required_number_for,
    validate_approval_count,
)
from hope.apps.payment.utils import log_payment_list_approval, log_payment_plan_change
from hope.contrib.vision.choices import VisionStatus
from hope.models import (
    Approval,
    ApprovalProcess,
    Currency,
    DeliveryMechanism,
    FinancialServiceProvider,
    FspXlsxTemplatePerDeliveryMechanism,
    Payment,
    PaymentList,
    PaymentListSplit,
    PaymentPlan,
    log_create,
)

if TYPE_CHECKING:
    from uuid import UUID

    from hope.models import User

ACTION_TO_STATUSES = {
    PaymentList.Action.APPROVE.value: (PaymentPlan.Status.IN_APPROVAL,),
    PaymentList.Action.AUTHORIZE.value: (PaymentPlan.Status.IN_AUTHORIZATION,),
    PaymentList.Action.REVIEW.value: (PaymentPlan.Status.IN_REVIEW,),
    PaymentList.Action.REJECT.value: (
        PaymentPlan.Status.IN_APPROVAL,
        PaymentPlan.Status.IN_AUTHORIZATION,
        PaymentPlan.Status.IN_REVIEW,
    ),
}


class PaymentPlanService:
    def __init__(self, payment_plan: PaymentPlan) -> None:
        self.payment_plan = payment_plan

    @transaction.atomic
    def create_linked_payment_plan(
        self,
        plan_type: "PaymentList.PlanType",
        user: "User",
        dispersion_start_date: datetime.date,
        dispersion_end_date: datetime.date,
        top_up_amount: Decimal | dict[str, Decimal] | None = None,
    ) -> PaymentPlan:
        """Create a Follow-Up / Top-Up / Amendment of this payment plan as a new linked payment plan.

        The linked payment plan holds one child payment list per payment list of this payment plan that
        qualifies for it, takes this payment plan's FSP, currency and payment gateway flag, gets the given
        dispersion dates and starts OPEN.
        ``top_up_amount`` funds a Top-Up or Amendment: a ``Decimal`` for every eligible beneficiary, or
        ``{payment unicef_id: amount}`` from the payment plan's amount file, split here per source payment list.
        """
        source_payment_plan = self._locked_for_update()
        if source_payment_plan.plan_type not in PaymentPlan.LINKED_GROUP_SOURCE_PLAN_TYPES[plan_type]:
            raise ValidationError(
                f"A {plan_type.label} cannot be created from a "
                f"{source_payment_plan.get_plan_type_display()} payment plan."
            )
        if (
            plan_type != PaymentList.PlanType.FOLLOW_UP
            and source_payment_plan.status not in PaymentPlan.CHILD_GROUP_SOURCE_STATUSES
        ):
            raise ValidationError(
                f"A {plan_type.label} can only be created from an Accepted or Finished payment plan, "
                f"got {source_payment_plan.status}"
            )
        qualifying_plans = source_payment_plan.payment_lists_qualifying_for_linked_payment_plan(plan_type)
        amounts_by_plan = self._amounts_by_plan(qualifying_plans, top_up_amount)
        source_plans = (
            [plan for plan in qualifying_plans if amounts_by_plan[plan.id]]
            if isinstance(top_up_amount, dict)
            else qualifying_plans
        )
        if not source_plans:
            raise ValidationError(f"No Payment List in this payment plan qualifies for a {plan_type.label}.")

        linked_payment_plan = PaymentPlan.objects.create(
            cycle=source_payment_plan.cycle,
            name=self._linked_payment_plan_name(source_payment_plan, plan_type),
            plan_type=plan_type,
            source_payment_plan=source_payment_plan,
            financial_service_provider=source_payment_plan.financial_service_provider,
            currency=source_payment_plan.currency,
            use_payment_gateway=source_payment_plan.use_payment_gateway,
            dispersion_start_date=dispersion_start_date,
            dispersion_end_date=dispersion_end_date,
            created_by=user,
            status_date=timezone.now(),
        )
        for source_plan in source_plans:
            PaymentListService(source_plan).create_child_plan(
                plan_type=plan_type,
                user=user,
                payment_plan=linked_payment_plan,
                top_up_amount=amounts_by_plan.get(source_plan.id, top_up_amount),
            )
        return linked_payment_plan

    @staticmethod
    def _amounts_by_plan(payment_lists: list[PaymentList], top_up_amount: Decimal | dict[str, Decimal] | None) -> dict:
        """Split the payment plan's amount file per plan: ``{plan id: {payment unicef_id: amount}}``."""
        if not isinstance(top_up_amount, dict):
            return {}
        amounts_by_plan: dict = {plan.id: {} for plan in payment_lists}
        payment_parents = Payment.objects.filter(
            parent__in=payment_lists, unicef_id__in=top_up_amount.keys()
        ).values_list("unicef_id", "parent_id")
        for unicef_id, parent_id in payment_parents:
            amounts_by_plan[parent_id][unicef_id] = top_up_amount[cast("str", unicef_id)]
        return amounts_by_plan

    @staticmethod
    def _linked_payment_plan_name(source_payment_plan: PaymentPlan, plan_type: "PaymentList.PlanType") -> str:
        sequence_number = source_payment_plan.linked_payment_plans.filter(plan_type=plan_type).count() + 1
        name = f"{source_payment_plan.name} {plan_type.label} {sequence_number}"
        if PaymentPlan.objects.filter(cycle_id=source_payment_plan.cycle_id, name=name).exists():
            raise ValidationError(f"A payment plan named '{name}' already exists in this cycle.")
        return name

    @transaction.atomic
    def split(self, split_type: str, payments_no: int | None = None) -> PaymentPlan:
        """Split every plan in the payment plan the same way; each plan keeps its own splits for the Payment Gateway."""
        payment_plan = self._locked_for_update()
        if payment_plan.status != PaymentPlan.Status.ACCEPTED:
            raise ValidationError(f"Split is possible only within Status {PaymentPlan.Status.ACCEPTED}")
        if PaymentListSplit.objects.filter(
            payment_list__payment_plan=payment_plan, sent_to_payment_gateway=True
        ).exists():
            raise ValidationError("Payment Plan is already sent to payment gateway")
        for payment_list in self._payment_lists(payment_plan):
            try:
                PaymentListService(payment_list).split(split_type, payments_no)
            except ValidationError as error:
                raise ValidationError(f"{payment_list.unicef_id}: {' '.join(map(str, error.detail))}") from error
        payment_plan.remove_export_file_delivery()
        payment_plan.save(update_fields=["export_file_delivery", "updated_at"])
        self.payment_plan = payment_plan
        return payment_plan

    def assign_financial_service_provider(self, financial_service_provider: FinancialServiceProvider | None) -> None:
        """Set the payment plan's FSP, copy it onto its Target Populations and rebuild them.

        The caller saves the payment plan.

        Payments carry the FSP and the wallet validity from the build, so a change is only possible while
        every Target Population can still be rebuilt, i.e. is TP_OPEN.
        """
        if financial_service_provider == self.payment_plan.financial_service_provider:
            return
        self._validate_not_linked("Financial Service Provider")
        payment_lists = list(self.payment_plan.payment_lists.all())
        if any(payment_list.status != PaymentList.Status.TP_OPEN for payment_list in payment_lists):
            raise ValidationError(
                "Financial Service Provider can be changed only while every Target Population "
                "in the payment plan is Open."
            )
        self.payment_plan.financial_service_provider = financial_service_provider
        for payment_list in payment_lists:
            transaction.on_commit(
                lambda payment_list=payment_list: PaymentListService.rebuild_payment_list_population(
                    True, False, False, payment_list
                )
            )

    def assign_currency(self, currency: Currency | None) -> None:
        """Set the payment plan's currency; the caller saves it. Its payment lists copy it when they are opened."""
        if currency == self.payment_plan.currency:
            return
        self._validate_not_linked("Currency")
        if self.payment_plan.payment_lists.exclude(status__in=PaymentList.PRE_PAYMENT_LIST_STATUSES).exists():
            raise ValidationError("Currency can be changed only before any Payment List in the payment plan is opened.")
        if currency is not None:
            self._validate_currency_against_delivery_mechanisms(currency)
        elif self.payment_plan.payment_lists.exists():
            raise ValidationError("Currency cannot be removed while the payment plan has Payment Lists")
        self.payment_plan.currency = currency
        self.payment_plan.exchange_rate = None
        self.payment_plan.custom_exchange_rate = False
        self.payment_plan.custom_exchange_rate_set_by = None

    def assign_dispersion_dates(
        self, dispersion_start_date: datetime.date | None, dispersion_end_date: datetime.date | None
    ) -> None:
        """Set the payment plan's dispersion dates; the caller saves it. Its payment lists read them from it."""
        payment_plan = self.payment_plan
        if (dispersion_start_date, dispersion_end_date) == (
            payment_plan.dispersion_start_date,
            payment_plan.dispersion_end_date,
        ):
            return
        if payment_plan.status != PaymentPlan.Status.OPEN:
            raise ValidationError("Dispersion Dates can be changed only while the Payment Plan is Open.")
        self.validate_dispersion_dates(
            dispersion_start_date,
            dispersion_end_date,
            end_date_changed=dispersion_end_date != payment_plan.dispersion_end_date,
        )
        payment_plan.dispersion_start_date = dispersion_start_date
        payment_plan.dispersion_end_date = dispersion_end_date
        if not payment_plan.custom_exchange_rate:
            payment_plan.exchange_rate = None

    @staticmethod
    def validate_dispersion_dates(
        dispersion_start_date: datetime.date | None,
        dispersion_end_date: datetime.date | None,
        *,
        end_date_changed: bool = True,
    ) -> None:
        """Refuse an end date before the start date, and a new end date that is not in the future."""
        if dispersion_start_date and dispersion_end_date and dispersion_end_date < dispersion_start_date:
            raise ValidationError(
                f"Dispersion End Date [{dispersion_end_date}] cannot be earlier than "
                f"Dispersion Start Date [{dispersion_start_date}]"
            )
        if dispersion_end_date and end_date_changed and dispersion_end_date <= timezone.now().date():
            raise ValidationError(f"Dispersion End Date [{dispersion_end_date}] cannot be a past date")

    def _validate_not_linked(self, field_label: str) -> None:
        if self.payment_plan.source_payment_plan_id is not None:
            raise ValidationError(
                f"{field_label} of a Follow-Up / Top-Up / Amendment payment plan is taken from its source payment plan."
            )

    def _validate_currency_against_delivery_mechanisms(self, currency: Currency) -> None:
        delivery_mechanisms = DeliveryMechanism.objects.filter(paymentlist__payment_plan=self.payment_plan).distinct()
        for delivery_mechanism in delivery_mechanisms:
            PaymentListService.validate_currency_for_delivery_mechanism(currency, delivery_mechanism)

    @transaction.atomic
    def lock(self) -> PaymentPlan:
        """Close the payment plan to new Payment Lists and lock the FSP of every one it holds."""
        payment_plan = PaymentPlan.objects.select_for_update().get(pk=self.payment_plan.pk)
        if payment_plan.status != PaymentPlan.Status.OPEN:
            raise ValidationError(f"Lock Payment Plan is possible only within Status {PaymentPlan.Status.OPEN}")
        self._clear_background_action(payment_plan)

        payment_lists = self._payment_lists(payment_plan)
        self._validate_payment_lists_locked(payment_lists)
        self._validate_configuration(payment_plan)
        self._validate_delivery_templates(payment_plan, payment_lists)

        for payment_list in payment_lists:
            PaymentListService(payment_list).lock_fsp()

        flow = PaymentPlanFlow(payment_plan)
        flow.status_lock()
        payment_plan.save(update_fields=("status", "status_date", "background_action_status", "updated_at", "version"))

        self.payment_plan = payment_plan
        return payment_plan

    @transaction.atomic
    def send_for_approval(self, user: "User") -> PaymentPlan:
        """Send the payment plan and every plan in it for approval; one approval process, on the payment plan."""
        payment_plan = self._locked_for_update()
        if payment_plan.status != PaymentPlan.Status.LOCKED:
            raise ValidationError(f"Send for Approval is possible only within Status {PaymentPlan.Status.LOCKED}")
        # The approval numbers come from the USD totals, so a failed recalculation must be retried first.
        if payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.RECALCULATING_ERROR:
            raise ValidationError(
                "USD recalculation failed for this payment plan. Retry it before sending for approval."
            )
        self._clear_background_action(payment_plan)
        for payment_list in self._payment_lists(payment_plan):
            PaymentListService(payment_list).transition_send_for_approval()

        flow = PaymentPlanFlow(payment_plan)
        flow.status_send_for_approval()
        payment_plan.save(update_fields=("status", "status_date", "background_action_status", "updated_at", "version"))
        ApprovalProcess.objects.create(
            payment_plan=payment_plan,
            sent_for_approval_by=user,
            sent_for_approval_date=timezone.now(),
            approval_number_required=payment_plan.approval_number_required,
            authorization_number_required=payment_plan.authorization_number_required,
            finance_release_number_required=payment_plan.finance_release_number_required,
        )
        send_payment_plan_notification_emails_async_task(
            payment_plan,
            PaymentList.Action.SEND_FOR_APPROVAL.value,
            str(user.pk),
            timezone.now().isoformat(),
        )
        self.payment_plan = payment_plan
        return payment_plan

    @transaction.atomic
    def acceptance_process(self, action: str, user: "User", comment: str | None = None) -> PaymentPlan:
        """Record one approve / authorize / release / reject on the payment plan.

        When the required count is reached the payment plan moves to the next stage and the new status is
        mirrored onto every payment list (its status is read by eligibility, conflicts, verification and
        exports).
        """
        approval_type = ACTION_TO_APPROVAL_TYPE[action]
        payment_plan = self._locked_for_update()
        if payment_plan.status not in ACTION_TO_STATUSES[action]:
            raise ValidationError(
                f"Not possible to create {action} for Payment Plan within status {payment_plan.status}"
            )
        approval_process = payment_plan.approval_process.first()
        if approval_process is None:
            raise ValidationError(f"Approval Process object not found for Payment Plan {payment_plan.pk}")
        payment_lists = self._payment_lists(payment_plan)
        if action == PaymentList.Action.REVIEW.value and payment_plan.vision_managed:
            raise ValidationError("Vision-managed Payment Plans are released automatically after FC assignment")
        # The release queues a rate recalculation, which refuses to start while another background action runs.
        if approval_type == Approval.FINANCE_RELEASE and not payment_plan.can_start_background_action:
            raise ValidationError("Another background action is already in progress.")
        required_number = required_number_for(approval_process, approval_type)
        validate_approval_count(approval_process, approval_type, required_number, payment_plan.status, user)

        Approval.objects.create(approval_process=approval_process, created_by=user, type=approval_type, comment=comment)
        log_payment_list_approval(payment_plan, user, approval_type, comment)

        if approval_process.approvals.filter(type=approval_type).count() >= required_number:
            record_stage_reached(approval_process, approval_type, user)
            notify_vision = approval_type == Approval.REJECT and payment_plan.sent_to_vision
            if approval_type in (Approval.REJECT, Approval.FINANCE_RELEASE) and (
                payment_plan.sent_to_vision or payment_plan.vision_status != VisionStatus.NOT_SENT.value
            ):
                from hope.contrib.vision.services import VisionService

                VisionService.invalidate_attempt(payment_plan)
                payment_plan.save(update_fields=["internal_data"])
            self._transition_stage(payment_plan, approval_type)
            for payment_list in payment_lists:
                PaymentListService(payment_list).apply_acceptance_stage(approval_type, user)
            if approval_type == Approval.FINANCE_RELEASE:
                transaction.on_commit(lambda: recalculate_owner_exchange_rate_async_task(payment_plan, str(user.pk)))
            if approval_type == Approval.AUTHORIZATION and payment_plan.vision_managed:
                from hope.contrib.vision.tasks import send_payment_plan_to_vision_async_task

                transaction.on_commit(lambda: send_payment_plan_to_vision_async_task(payment_plan, str(user.pk)))
            if notify_vision:
                from hope.contrib.vision.tasks import notify_payment_plan_status_to_vision_async_task

                transaction.on_commit(
                    lambda: notify_payment_plan_status_to_vision_async_task(payment_plan, str(user.pk), "REJECTED"),
                    robust=True,
                )
            if notification_action := STAGE_REACHED_NOTIFICATION.get(approval_type):
                send_payment_plan_notification_emails_async_task(
                    payment_plan, notification_action.value, str(user.pk), timezone.now().isoformat()
                )
        self.payment_plan = payment_plan
        return payment_plan

    @transaction.atomic
    def release_from_vision(self) -> PaymentPlan:
        payment_plan = self._locked_for_update()
        if payment_plan.status != PaymentPlan.Status.IN_REVIEW:
            return payment_plan
        payment_lists = self._payment_lists(payment_plan)
        if not payment_lists or any(plan.status != PaymentList.Status.IN_REVIEW for plan in payment_lists):
            raise ValidationError("Every Payment List must be in review for Vision release")
        if not payment_plan.can_start_background_action:
            raise ValidationError("Another background action is already in progress.")
        approval_process = payment_plan.approval_process.first()
        if approval_process is None:
            raise ValidationError("Approval Process object not found for Payment Plan")
        user = payment_plan.created_by or payment_lists[0].created_by
        old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
        Approval.objects.create(approval_process=approval_process, created_by=user, type=Approval.FINANCE_RELEASE)
        log_payment_list_approval(payment_plan, user, Approval.FINANCE_RELEASE, None)
        record_stage_reached(approval_process, Approval.FINANCE_RELEASE, user)
        self._transition_stage(payment_plan, Approval.FINANCE_RELEASE)
        for payment_list in payment_lists:
            PaymentListService(payment_list).apply_acceptance_stage(Approval.FINANCE_RELEASE, user)
        transaction.on_commit(lambda: recalculate_owner_exchange_rate_async_task(payment_plan, str(user.pk)))
        log_payment_plan_change(payment_plan, old_payment_plan, str(user.pk))
        send_payment_plan_notification_emails_async_task(
            payment_plan,
            PaymentList.Action.REVIEW.value,
            str(user.pk),
            timezone.now().isoformat(),
        )
        for payment_list in payment_lists:
            if payment_list.can_send_to_payment_gateway:
                old_payment_list = copy_model_object(payment_list)
                sent_plan = PaymentListService(payment_list).execute_update_status_action(
                    input_data={"action": PaymentList.Action.SEND_TO_PAYMENT_GATEWAY},
                    user=user,
                    as_manager=True,
                )
                log_create(
                    mapping=PaymentList.ACTIVITY_LOG_MAPPING,
                    business_area_field="business_area",
                    user=user,
                    programs=payment_list.program.pk,
                    old_object=old_payment_list,
                    new_object=sent_plan,
                )
        self.payment_plan = payment_plan
        return payment_plan

    @transaction.atomic
    def sync_finished(self, user_id: str | None = None) -> PaymentPlan:
        """Follow the reconciliation of the payments: FINISHED once all are reconciled, ACCEPTED again if not."""
        payment_plan = self._locked_for_update()
        if payment_plan.status == PaymentPlan.Status.ACCEPTED and payment_plan.is_reconciled:
            transition = "status_finished"
        elif payment_plan.status == PaymentPlan.Status.FINISHED and not payment_plan.is_reconciled:
            transition = "status_reopen_for_reconciliation"
        else:
            return payment_plan
        old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
        getattr(PaymentPlanFlow(payment_plan), transition)()
        payment_plan.save(update_fields=("status", "status_date", "updated_at", "version"))
        for payment_list in self._payment_lists(payment_plan):
            getattr(PaymentListFlow(payment_list), transition)()
            payment_list.save(update_fields=("status", "status_date", "updated_at"))
        log_payment_plan_change(payment_plan, old_payment_plan, user_id)
        self.payment_plan = payment_plan
        return payment_plan

    @transaction.atomic
    def ready_for_closure(self, user: "User") -> PaymentPlan:
        payment_plan = self._locked_for_update()
        if payment_plan.status != PaymentPlan.Status.FINISHED:
            raise ValidationError(
                f"Mark as Ready for Closure is possible only within Status {PaymentPlan.Status.FINISHED}"
            )
        for payment_list in self._payment_lists(payment_plan):
            PaymentListService(payment_list).ready_for_closure()
        flow = PaymentPlanFlow(payment_plan)
        flow.status_ready_for_closure()
        payment_plan.save(update_fields=("status", "status_date", "updated_at", "version"))
        send_payment_plan_notification_emails_async_task(
            payment_plan,
            PaymentList.Action.MARK_READY_FOR_CLOSURE.value,
            str(user.pk),
            timezone.now().isoformat(),
        )
        self.payment_plan = payment_plan
        return payment_plan

    @transaction.atomic
    def send_back_to_finished(self, user: "User") -> PaymentPlan:
        payment_plan = self._locked_for_update()
        if payment_plan.status != PaymentPlan.Status.READY_FOR_CLOSURE:
            raise ValidationError(f"Send Back is possible only within Status {PaymentPlan.Status.READY_FOR_CLOSURE}")
        for payment_list in self._payment_lists(payment_plan):
            PaymentListService(payment_list).send_back_to_finished()
        flow = PaymentPlanFlow(payment_plan)
        flow.status_finished()
        payment_plan.save(update_fields=("status", "status_date", "updated_at", "version"))
        send_payment_plan_notification_emails_async_task(
            payment_plan,
            PaymentList.Action.SEND_BACK_TO_FINISHED.value,
            str(user.pk),
            timezone.now().isoformat(),
        )
        self.payment_plan = payment_plan
        return payment_plan

    @transaction.atomic
    def close(self, closure_comment: str | None, user: "User") -> PaymentPlan:
        payment_plan = self._locked_for_update()
        if payment_plan.status != PaymentPlan.Status.READY_FOR_CLOSURE:
            raise ValidationError(
                f"Close Payment Plan is possible only within Status {PaymentPlan.Status.READY_FOR_CLOSURE}"
            )
        payment_lists = self._payment_lists(payment_plan)
        if not payment_plan.has_verification and not closure_comment:
            raise ValidationError("Closure comment is required when no payment verification was carried out.")
        for payment_list in payment_lists:
            PaymentListService(payment_list).close(closure_comment=closure_comment, user_id=str(user.pk))
        flow = PaymentPlanFlow(payment_plan)
        flow.status_close()
        payment_plan.closure_comment = closure_comment
        payment_plan.closed_by = user
        payment_plan.save(
            update_fields=("status", "status_date", "closure_comment", "closed_by", "updated_at", "version")
        )
        self.payment_plan = payment_plan
        return payment_plan

    @transaction.atomic
    def abort(self, abort_comment: str | None, user: "User") -> PaymentPlan:
        payment_plan = self._locked_for_update()
        if payment_plan.status not in (
            PaymentPlan.Status.LOCKED,
            PaymentPlan.Status.IN_APPROVAL,
            PaymentPlan.Status.IN_AUTHORIZATION,
            PaymentPlan.Status.IN_REVIEW,
        ):
            raise ValidationError(f"Abort Payment Plan is not possible within Status {payment_plan.status}")
        self._clear_background_action(payment_plan)
        notify_vision = payment_plan.sent_to_vision
        if notify_vision or payment_plan.vision_status != VisionStatus.NOT_SENT.value:
            from hope.contrib.vision.services import VisionService

            VisionService.invalidate_attempt(payment_plan)
        for payment_list in self._payment_lists(payment_plan):
            PaymentListService(payment_list).abort(abort_comment, user_id=str(user.pk))
        flow = PaymentPlanFlow(payment_plan)
        flow.status_abort()
        payment_plan.abort_comment = abort_comment or ""
        payment_plan.save(
            update_fields=(
                "status",
                "status_date",
                "abort_comment",
                "background_action_status",
                "updated_at",
                "internal_data",
            )
        )
        if notify_vision:
            from hope.contrib.vision.tasks import notify_payment_plan_status_to_vision_async_task

            transaction.on_commit(
                lambda: notify_payment_plan_status_to_vision_async_task(payment_plan, str(user.pk), "ABORTED"),
                robust=True,
            )
        self.payment_plan = payment_plan
        return payment_plan

    @transaction.atomic
    def reactivate_abort(self, user_id: str | None = None) -> PaymentPlan:
        """Reactivate the payment lists.

        The payment plan stays ABORTED and REBUILDING while a regular payment list refreshes its payees.

        After a failed refresh (REBUILD_ERROR) the call is repeated; plans still rebuilding are left to finish.
        """
        payment_plan = self._locked_for_update()
        if payment_plan.status != PaymentPlan.Status.ABORTED:
            raise ValidationError(
                f"Reactivate Aborted Payment Plan is possible only within Status {PaymentPlan.Status.ABORTED}"
            )
        if not payment_plan.can_start_background_action:
            raise ValidationError("Another background action is already in progress.")
        payment_lists = self._payment_lists(payment_plan)
        for payment_list in payment_lists:
            if (
                payment_list.status == PaymentList.Status.ABORTED
                and payment_list.background_action_status != PaymentList.BackgroundActionStatus.REBUILDING
            ):
                PaymentListService(payment_list).reactivate_abort(user_id)
        if any(payment_list.status == PaymentList.Status.ABORTED for payment_list in payment_lists):
            payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.REBUILDING
            payment_plan.save(update_fields=("background_action_status", "updated_at", "version"))
        else:
            self._open_reactivated(payment_plan)
        self.payment_plan = payment_plan
        return payment_plan

    @staticmethod
    @transaction.atomic
    def open_after_payees_refresh(payment_plan_id: "UUID", user_id: str | None = None) -> None:
        """Open a rebuilding payment plan once none of its plans is still ABORTED."""
        payment_plan = PaymentPlan.objects.select_for_update().get(pk=payment_plan_id)
        if payment_plan.background_action_status != PaymentPlan.BackgroundActionStatus.REBUILDING:
            return
        if payment_plan.payment_lists.filter(status=PaymentList.Status.ABORTED).exists():
            return
        old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
        PaymentPlanService._open_reactivated(payment_plan)
        log_payment_plan_change(payment_plan, old_payment_plan, user_id)

    @staticmethod
    @transaction.atomic
    def mark_rebuild_error(payment_plan_id: "UUID", user_id: str | None = None) -> None:
        payment_plan = PaymentPlan.objects.select_for_update().get(pk=payment_plan_id)
        if payment_plan.background_action_status != PaymentPlan.BackgroundActionStatus.REBUILDING:
            return
        old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
        payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.REBUILD_ERROR
        payment_plan.save(update_fields=("background_action_status", "updated_at", "version"))
        log_payment_plan_change(payment_plan, old_payment_plan, user_id)

    @staticmethod
    def _open_reactivated(payment_plan: PaymentPlan) -> None:
        flow = PaymentPlanFlow(payment_plan)
        flow.status_reactivate_abort()
        payment_plan.background_action_status = None
        payment_plan.save(update_fields=("status", "status_date", "background_action_status", "updated_at", "version"))

    @staticmethod
    def _transition_stage(payment_plan: PaymentPlan, approval_type: str) -> None:
        flow = PaymentPlanFlow(payment_plan)
        {
            Approval.APPROVAL: flow.status_approve,
            Approval.AUTHORIZATION: flow.status_authorize,
            Approval.FINANCE_RELEASE: flow.status_mark_as_reviewed,
            Approval.REJECT: flow.status_reject,
        }[approval_type]()
        payment_plan.save(update_fields=("status", "status_date", "updated_at", "version"))

    def _locked_for_update(self) -> PaymentPlan:
        return PaymentPlan.objects.select_for_update().get(pk=self.payment_plan.pk)

    @transaction.atomic
    def unlock(self) -> PaymentPlan:
        """Reopen the payment plan for new Payment Lists and release the FSP lock on every one it holds."""
        payment_plan = PaymentPlan.objects.select_for_update().get(pk=self.payment_plan.pk)
        if payment_plan.status != PaymentPlan.Status.LOCKED:
            raise ValidationError(f"Unlock Payment Plan is possible only within Status {PaymentPlan.Status.LOCKED}")
        self._clear_background_action(payment_plan)

        for payment_list in self._payment_lists(payment_plan):
            PaymentListService(payment_list).unlock_fsp()

        flow = PaymentPlanFlow(payment_plan)
        flow.status_unlock()
        payment_plan.save(update_fields=("status", "status_date", "background_action_status", "updated_at", "version"))

        self.payment_plan = payment_plan
        return payment_plan

    @staticmethod
    def _clear_background_action(payment_plan: PaymentPlan) -> None:
        """Refuse while a background action runs.

        A failed FSP extra fields import is dropped as the payment plan moves on.

        A failed USD recalculation stays, so it can still be retried from the admin.
        """
        if not payment_plan.can_start_background_action:
            raise ValidationError("Another background action is already in progress.")
        if payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.XLSX_IMPORT_ERROR:
            payment_plan.background_action_status = None

    @staticmethod
    def _payment_lists(payment_plan: PaymentPlan) -> list[PaymentList]:
        return list(
            payment_plan.payment_lists.select_related(
                "business_area", "delivery_mechanism", "payment_plan__financial_service_provider"
            ).order_by("created_at")
        )

    @staticmethod
    def _validate_payment_lists_locked(payment_lists: list[PaymentList]) -> None:
        if not payment_lists:
            raise ValidationError("Lock is not possible for a Payment Plan without Payment Lists.")
        not_locked = [
            str(payment_list.unicef_id)
            for payment_list in payment_lists
            if payment_list.status != PaymentList.Status.LOCKED
        ]
        if not_locked:
            raise ValidationError(
                f"Every Payment List must be locked before the Payment Plan can be locked. "
                f"Not locked: {', '.join(not_locked)}."
            )

    @staticmethod
    def _validate_configuration(payment_plan: PaymentPlan) -> None:
        if payment_plan.financial_service_provider_id is None:
            raise ValidationError("Payment Plan needs a Financial Service Provider before it can be locked.")
        if payment_plan.currency_id is None:
            raise ValidationError("Payment Plan needs a Currency before it can be locked.")

    @staticmethod
    def _validate_delivery_templates(payment_plan: PaymentPlan, payment_lists: list[PaymentList]) -> None:
        """Reject up front what the payment plan export would otherwise drop with only a warning."""
        mapped_delivery_mechanism_ids = set(
            FspXlsxTemplatePerDeliveryMechanism.objects.filter(
                financial_service_provider_id=payment_plan.financial_service_provider_id,
                delivery_mechanism_id__in={payment_list.delivery_mechanism_id for payment_list in payment_lists},
            ).values_list("delivery_mechanism_id", flat=True)
        )
        missing = [
            str(payment_list.unicef_id)
            for payment_list in payment_lists
            if payment_list.delivery_mechanism_id not in mapped_delivery_mechanism_ids
        ]
        if missing:
            raise ValidationError(
                f"Every Payment List needs an FSP XLSX Template for its Financial Service Provider and "
                f"Delivery Mechanism. Missing for: {', '.join(missing)}."
            )
