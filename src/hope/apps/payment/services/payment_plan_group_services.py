import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, cast

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from hope.apps.activity_log.utils import copy_model_object
from hope.apps.payment.celery_tasks import send_payment_plan_group_notification_emails_async_task
from hope.apps.payment.flows import PaymentPlanFlow, PaymentPlanGroupFlow
from hope.apps.payment.services.payment_plan_services import (
    ACTION_TO_APPROVAL_TYPE,
    STAGE_REACHED_NOTIFICATION,
    PaymentPlanService,
    record_stage_reached,
    required_number_for,
    validate_approval_count,
)
from hope.apps.payment.utils import log_payment_plan_approval, log_payment_plan_group_change
from hope.models import (
    Approval,
    ApprovalProcess,
    Currency,
    DeliveryMechanism,
    FinancialServiceProvider,
    FspXlsxTemplatePerDeliveryMechanism,
    Payment,
    PaymentPlan,
    PaymentPlanGroup,
)

if TYPE_CHECKING:
    from hope.models import User

ACTION_TO_STATUSES = {
    PaymentPlan.Action.APPROVE.value: (PaymentPlanGroup.Status.IN_APPROVAL,),
    PaymentPlan.Action.AUTHORIZE.value: (PaymentPlanGroup.Status.IN_AUTHORIZATION,),
    PaymentPlan.Action.REVIEW.value: (PaymentPlanGroup.Status.IN_REVIEW,),
    PaymentPlan.Action.REJECT.value: (
        PaymentPlanGroup.Status.IN_APPROVAL,
        PaymentPlanGroup.Status.IN_AUTHORIZATION,
        PaymentPlanGroup.Status.IN_REVIEW,
    ),
}


class PaymentPlanGroupService:
    def __init__(self, payment_plan_group: PaymentPlanGroup) -> None:
        self.payment_plan_group = payment_plan_group

    @transaction.atomic
    def create_linked_group(
        self,
        plan_type: "PaymentPlan.PlanType",
        user: "User",
        dispersion_start_date: datetime.date,
        dispersion_end_date: datetime.date,
        top_up_amount: Decimal | dict[str, Decimal] | None = None,
    ) -> PaymentPlanGroup:
        """Create a Follow-Up / Top-Up / Amendment of this group as a new linked group.

        The linked group holds one child plan per plan of this group that qualifies for it, takes this
        group's FSP and currency, and starts OPEN. ``top_up_amount`` funds a Top-Up or Amendment:
        a ``Decimal`` for every eligible beneficiary, or ``{payment unicef_id: amount}`` from the
        group's amount file, split here per source plan.
        """
        source_group = self._locked_for_update()
        if source_group.plan_type not in PaymentPlanGroup.LINKED_GROUP_SOURCE_PLAN_TYPES[plan_type]:
            raise ValidationError(
                f"A {plan_type.label} cannot be created from a {source_group.get_plan_type_display()} group."
            )
        if (
            plan_type != PaymentPlan.PlanType.FOLLOW_UP
            and source_group.status not in PaymentPlanGroup.CHILD_GROUP_SOURCE_STATUSES
        ):
            raise ValidationError(
                f"A {plan_type.label} can only be created from an Accepted or Finished group, got {source_group.status}"
            )
        qualifying_plans = source_group.plans_qualifying_for_linked_group(plan_type)
        amounts_by_plan = self._amounts_by_plan(qualifying_plans, top_up_amount)
        source_plans = (
            [plan for plan in qualifying_plans if amounts_by_plan[plan.id]]
            if isinstance(top_up_amount, dict)
            else qualifying_plans
        )
        if not source_plans:
            raise ValidationError(f"No Payment Plan in this group qualifies for a {plan_type.label}.")

        linked_group = PaymentPlanGroup.objects.create(
            cycle=source_group.cycle,
            name=self._linked_group_name(source_group, plan_type),
            plan_type=plan_type,
            source_group=source_group,
            financial_service_provider=source_group.financial_service_provider,
            currency=source_group.currency,
            created_by=user,
            status_date=timezone.now(),
        )
        for source_plan in source_plans:
            PaymentPlanService(source_plan).create_child_plan(
                plan_type=plan_type,
                user=user,
                dispersion_start_date=dispersion_start_date,
                dispersion_end_date=dispersion_end_date,
                payment_plan_group=linked_group,
                top_up_amount=amounts_by_plan.get(source_plan.id, top_up_amount),
            )
        return linked_group

    @staticmethod
    def _amounts_by_plan(payment_plans: list[PaymentPlan], top_up_amount: Decimal | dict[str, Decimal] | None) -> dict:
        """Split the group's amount file per plan: ``{plan id: {payment unicef_id: amount}}``."""
        if not isinstance(top_up_amount, dict):
            return {}
        amounts_by_plan: dict = {plan.id: {} for plan in payment_plans}
        payment_parents = Payment.objects.filter(
            parent__in=payment_plans, unicef_id__in=top_up_amount.keys()
        ).values_list("unicef_id", "parent_id")
        for unicef_id, parent_id in payment_parents:
            amounts_by_plan[parent_id][unicef_id] = top_up_amount[cast("str", unicef_id)]
        return amounts_by_plan

    @staticmethod
    def _linked_group_name(source_group: PaymentPlanGroup, plan_type: "PaymentPlan.PlanType") -> str:
        sequence_number = source_group.linked_groups.filter(plan_type=plan_type).count() + 1
        name = f"{source_group.name} {plan_type.label} {sequence_number}"
        if PaymentPlanGroup.objects.filter(cycle_id=source_group.cycle_id, name=name).exists():
            raise ValidationError(f"A group named '{name}' already exists in this cycle.")
        return name

    def assign_financial_service_provider(self, financial_service_provider: FinancialServiceProvider | None) -> None:
        """Set the group's FSP, copy it onto its Target Populations and rebuild them; the caller saves the group.

        Payments carry the FSP and the wallet validity from the build, so a change is only possible while
        every Target Population can still be rebuilt, i.e. is TP_OPEN.
        """
        if financial_service_provider == self.payment_plan_group.financial_service_provider:
            return
        self._validate_not_linked("Financial Service Provider")
        payment_plans = list(self.payment_plan_group.payment_plans.all())
        if any(payment_plan.status != PaymentPlan.Status.TP_OPEN for payment_plan in payment_plans):
            raise ValidationError(
                "Financial Service Provider can be changed only while every Target Population in the group is Open."
            )
        self.payment_plan_group.financial_service_provider = financial_service_provider
        for payment_plan in payment_plans:
            transaction.on_commit(
                lambda payment_plan=payment_plan: PaymentPlanService.rebuild_payment_plan_population(
                    True, False, False, payment_plan
                )
            )

    def assign_currency(self, currency: Currency | None) -> None:
        """Set the group's currency; the caller saves the group. Payment Plans copy it when they are opened."""
        if currency == self.payment_plan_group.currency:
            return
        self._validate_not_linked("Currency")
        if self.payment_plan_group.payment_plans.exclude(status__in=PaymentPlan.PRE_PAYMENT_PLAN_STATUSES).exists():
            raise ValidationError("Currency can be changed only before any Payment Plan in the group is opened.")
        if currency is not None:
            self._validate_currency_against_delivery_mechanisms(currency)
        self.payment_plan_group.currency = currency

    def _validate_not_linked(self, field_label: str) -> None:
        if self.payment_plan_group.source_group_id is not None:
            raise ValidationError(
                f"{field_label} of a Follow-Up / Top-Up / Amendment group is taken from its source group."
            )

    def _validate_currency_against_delivery_mechanisms(self, currency: Currency) -> None:
        delivery_mechanisms = DeliveryMechanism.objects.filter(
            paymentplan__payment_plan_group=self.payment_plan_group
        ).distinct()
        for delivery_mechanism in delivery_mechanisms:
            PaymentPlanService.validate_currency_for_delivery_mechanism(currency, delivery_mechanism)

    @transaction.atomic
    def lock(self) -> PaymentPlanGroup:
        """Close the group to new Payment Plans and lock the FSP of every one it holds."""
        payment_plan_group = PaymentPlanGroup.objects.select_for_update().get(pk=self.payment_plan_group.pk)
        if payment_plan_group.status != PaymentPlanGroup.Status.OPEN:
            raise ValidationError(
                f"Lock Payment Plan Group is possible only within Status {PaymentPlanGroup.Status.OPEN}"
            )

        payment_plans = self._payment_plans(payment_plan_group)
        self._validate_payment_plans_locked(payment_plans)
        self._validate_configuration(payment_plan_group)
        self._validate_delivery_templates(payment_plan_group, payment_plans)

        for payment_plan in payment_plans:
            PaymentPlanService(payment_plan).lock_fsp()

        flow = PaymentPlanGroupFlow(payment_plan_group)
        flow.status_lock()
        payment_plan_group.save(update_fields=("status", "status_date", "updated_at"))

        self.payment_plan_group = payment_plan_group
        return payment_plan_group

    @transaction.atomic
    def send_for_approval(self, user: "User") -> PaymentPlanGroup:
        """Send the group and every plan in it for approval; one approval process, on the group."""
        payment_plan_group = self._locked_for_update()
        if payment_plan_group.status != PaymentPlanGroup.Status.LOCKED:
            raise ValidationError(f"Send for Approval is possible only within Status {PaymentPlanGroup.Status.LOCKED}")
        for payment_plan in self._payment_plans(payment_plan_group):
            PaymentPlanService(payment_plan).transition_send_for_approval()

        flow = PaymentPlanGroupFlow(payment_plan_group)
        flow.status_send_for_approval()
        payment_plan_group.save(update_fields=("status", "status_date", "updated_at"))
        ApprovalProcess.objects.create(
            payment_plan_group=payment_plan_group,
            sent_for_approval_by=user,
            sent_for_approval_date=timezone.now(),
            approval_number_required=payment_plan_group.approval_number_required,
            authorization_number_required=payment_plan_group.authorization_number_required,
            finance_release_number_required=payment_plan_group.finance_release_number_required,
        )
        send_payment_plan_group_notification_emails_async_task(
            payment_plan_group,
            PaymentPlan.Action.SEND_FOR_APPROVAL.value,
            str(user.pk),
            timezone.now().isoformat(),
        )
        self.payment_plan_group = payment_plan_group
        return payment_plan_group

    @transaction.atomic
    def acceptance_process(self, action: str, user: "User", comment: str | None = None) -> PaymentPlanGroup:
        """Record one approve / authorize / release / reject on the group.

        When the required count is reached the group moves to the next stage and the new status is
        mirrored onto every plan (plan status is read by eligibility, conflicts, verification and exports).
        """
        approval_type = ACTION_TO_APPROVAL_TYPE[action]
        payment_plan_group = self._locked_for_update()
        if payment_plan_group.status not in ACTION_TO_STATUSES[action]:
            raise ValidationError(
                f"Not possible to create {action} for Payment Plan Group within status {payment_plan_group.status}"
            )
        approval_process = payment_plan_group.approval_process.first()
        if approval_process is None:
            raise ValidationError(f"Approval Process object not found for Payment Plan Group {payment_plan_group.pk}")
        payment_plans = self._payment_plans(payment_plan_group)
        if action == PaymentPlan.Action.REVIEW.value and any(
            payment_plan.vision_managed for payment_plan in payment_plans
        ):
            raise ValidationError("Vision-managed Payment Plans are released automatically after FC assignment")
        required_number = required_number_for(approval_process, approval_type)
        validate_approval_count(approval_process, approval_type, required_number, payment_plan_group.status, user)

        Approval.objects.create(approval_process=approval_process, created_by=user, type=approval_type, comment=comment)
        log_payment_plan_approval(payment_plan_group, user, approval_type, comment)

        if approval_process.approvals.filter(type=approval_type).count() >= required_number:
            record_stage_reached(approval_process, approval_type, user)
            self._transition_stage(payment_plan_group, approval_type)
            for payment_plan in payment_plans:
                PaymentPlanService(payment_plan).apply_acceptance_stage(approval_type, user)
            if notification_action := STAGE_REACHED_NOTIFICATION.get(approval_type):
                send_payment_plan_group_notification_emails_async_task(
                    payment_plan_group, notification_action.value, str(user.pk), timezone.now().isoformat()
                )
        self.payment_plan_group = payment_plan_group
        return payment_plan_group

    @transaction.atomic
    def sync_finished(self, user_id: str | None = None) -> PaymentPlanGroup:
        """Follow the reconciliation of the payments: FINISHED once all are reconciled, ACCEPTED again if not."""
        payment_plan_group = self._locked_for_update()
        if payment_plan_group.status == PaymentPlanGroup.Status.ACCEPTED and payment_plan_group.is_reconciled:
            transition = "status_finished"
        elif payment_plan_group.status == PaymentPlanGroup.Status.FINISHED and not payment_plan_group.is_reconciled:
            transition = "status_reopen_for_reconciliation"
        else:
            return payment_plan_group
        old_payment_plan_group = cast("PaymentPlanGroup", copy_model_object(payment_plan_group))
        getattr(PaymentPlanGroupFlow(payment_plan_group), transition)()
        payment_plan_group.save(update_fields=("status", "status_date", "updated_at"))
        for payment_plan in self._payment_plans(payment_plan_group):
            getattr(PaymentPlanFlow(payment_plan), transition)()
            payment_plan.save(update_fields=("status", "status_date", "updated_at"))
        log_payment_plan_group_change(payment_plan_group, old_payment_plan_group, user_id)
        self.payment_plan_group = payment_plan_group
        return payment_plan_group

    @transaction.atomic
    def ready_for_closure(self, user: "User") -> PaymentPlanGroup:
        payment_plan_group = self._locked_for_update()
        if payment_plan_group.status != PaymentPlanGroup.Status.FINISHED:
            raise ValidationError(
                f"Mark as Ready for Closure is possible only within Status {PaymentPlanGroup.Status.FINISHED}"
            )
        for payment_plan in self._payment_plans(payment_plan_group):
            PaymentPlanService(payment_plan).ready_for_closure()
        flow = PaymentPlanGroupFlow(payment_plan_group)
        flow.status_ready_for_closure()
        payment_plan_group.save(update_fields=("status", "status_date", "updated_at"))
        send_payment_plan_group_notification_emails_async_task(
            payment_plan_group,
            PaymentPlan.Action.MARK_READY_FOR_CLOSURE.value,
            str(user.pk),
            timezone.now().isoformat(),
        )
        self.payment_plan_group = payment_plan_group
        return payment_plan_group

    @transaction.atomic
    def send_back_to_finished(self, user: "User") -> PaymentPlanGroup:
        payment_plan_group = self._locked_for_update()
        if payment_plan_group.status != PaymentPlanGroup.Status.READY_FOR_CLOSURE:
            raise ValidationError(
                f"Send Back is possible only within Status {PaymentPlanGroup.Status.READY_FOR_CLOSURE}"
            )
        for payment_plan in self._payment_plans(payment_plan_group):
            PaymentPlanService(payment_plan).send_back_to_finished()
        flow = PaymentPlanGroupFlow(payment_plan_group)
        flow.status_finished()
        payment_plan_group.save(update_fields=("status", "status_date", "updated_at"))
        send_payment_plan_group_notification_emails_async_task(
            payment_plan_group,
            PaymentPlan.Action.SEND_BACK_TO_FINISHED.value,
            str(user.pk),
            timezone.now().isoformat(),
        )
        self.payment_plan_group = payment_plan_group
        return payment_plan_group

    @transaction.atomic
    def close(self, closure_comment: str | None, user: "User") -> PaymentPlanGroup:
        payment_plan_group = self._locked_for_update()
        if payment_plan_group.status != PaymentPlanGroup.Status.READY_FOR_CLOSURE:
            raise ValidationError(
                f"Close Payment Plan Group is possible only within Status {PaymentPlanGroup.Status.READY_FOR_CLOSURE}"
            )
        payment_plans = self._payment_plans(payment_plan_group)
        every_plan_verified = all(
            payment_plan.payment_verification_plans.filter(responded_count__gt=0).exists()
            for payment_plan in payment_plans
        )
        if not every_plan_verified and not closure_comment:
            raise ValidationError("Closure comment is required when no payment verification was carried out.")
        for payment_plan in payment_plans:
            PaymentPlanService(payment_plan).close(closure_comment=closure_comment, user_id=str(user.pk))
        flow = PaymentPlanGroupFlow(payment_plan_group)
        flow.status_close()
        payment_plan_group.closure_comment = closure_comment
        payment_plan_group.closed_by = user
        payment_plan_group.save(update_fields=("status", "status_date", "closure_comment", "closed_by", "updated_at"))
        self.payment_plan_group = payment_plan_group
        return payment_plan_group

    @transaction.atomic
    def abort(self, abort_comment: str | None, user: "User") -> PaymentPlanGroup:
        payment_plan_group = self._locked_for_update()
        if payment_plan_group.status not in (
            PaymentPlanGroup.Status.LOCKED,
            PaymentPlanGroup.Status.IN_APPROVAL,
            PaymentPlanGroup.Status.IN_AUTHORIZATION,
            PaymentPlanGroup.Status.IN_REVIEW,
        ):
            raise ValidationError(f"Abort Payment Plan Group is not possible within Status {payment_plan_group.status}")
        for payment_plan in self._payment_plans(payment_plan_group):
            PaymentPlanService(payment_plan).abort(abort_comment, user_id=str(user.pk))
        flow = PaymentPlanGroupFlow(payment_plan_group)
        flow.status_abort()
        payment_plan_group.abort_comment = abort_comment or ""
        payment_plan_group.save(update_fields=("status", "status_date", "abort_comment", "updated_at"))
        self.payment_plan_group = payment_plan_group
        return payment_plan_group

    @transaction.atomic
    def reactivate_abort(self) -> PaymentPlanGroup:
        payment_plan_group = self._locked_for_update()
        if payment_plan_group.status != PaymentPlanGroup.Status.ABORTED:
            raise ValidationError(
                "Reactivate Aborted Payment Plan Group is possible only within Status "
                f"{PaymentPlanGroup.Status.ABORTED}"
            )
        for payment_plan in self._payment_plans(payment_plan_group):
            PaymentPlanService(payment_plan).reactivate_abort()
        flow = PaymentPlanGroupFlow(payment_plan_group)
        flow.status_reactivate_abort()
        payment_plan_group.save(update_fields=("status", "status_date", "updated_at"))
        self.payment_plan_group = payment_plan_group
        return payment_plan_group

    @staticmethod
    def _transition_stage(payment_plan_group: PaymentPlanGroup, approval_type: str) -> None:
        flow = PaymentPlanGroupFlow(payment_plan_group)
        {
            Approval.APPROVAL: flow.status_approve,
            Approval.AUTHORIZATION: flow.status_authorize,
            Approval.FINANCE_RELEASE: flow.status_mark_as_reviewed,
            Approval.REJECT: flow.status_reject,
        }[approval_type]()
        payment_plan_group.save(update_fields=("status", "status_date", "updated_at"))

    def _locked_for_update(self) -> PaymentPlanGroup:
        return PaymentPlanGroup.objects.select_for_update().get(pk=self.payment_plan_group.pk)

    @transaction.atomic
    def unlock(self) -> PaymentPlanGroup:
        """Reopen the group for new Payment Plans and release the FSP lock on every one it holds."""
        payment_plan_group = PaymentPlanGroup.objects.select_for_update().get(pk=self.payment_plan_group.pk)
        if payment_plan_group.status != PaymentPlanGroup.Status.LOCKED:
            raise ValidationError(
                f"Unlock Payment Plan Group is possible only within Status {PaymentPlanGroup.Status.LOCKED}"
            )

        for payment_plan in self._payment_plans(payment_plan_group):
            PaymentPlanService(payment_plan).unlock_fsp()

        flow = PaymentPlanGroupFlow(payment_plan_group)
        flow.status_unlock()
        payment_plan_group.save(update_fields=("status", "status_date", "updated_at"))

        self.payment_plan_group = payment_plan_group
        return payment_plan_group

    @staticmethod
    def _payment_plans(payment_plan_group: PaymentPlanGroup) -> list[PaymentPlan]:
        return list(
            payment_plan_group.payment_plans.select_related(
                "business_area", "delivery_mechanism", "payment_plan_group__financial_service_provider"
            ).order_by("created_at")
        )

    @staticmethod
    def _validate_payment_plans_locked(payment_plans: list[PaymentPlan]) -> None:
        if not payment_plans:
            raise ValidationError("Lock is not possible for a Payment Plan Group without Payment Plans.")
        not_locked = [
            str(payment_plan.unicef_id)
            for payment_plan in payment_plans
            if payment_plan.status != PaymentPlan.Status.LOCKED
        ]
        if not_locked:
            raise ValidationError(
                f"Every Payment Plan must be locked before the Payment Plan Group can be locked. "
                f"Not locked: {', '.join(not_locked)}."
            )

    @staticmethod
    def _validate_configuration(payment_plan_group: PaymentPlanGroup) -> None:
        if payment_plan_group.financial_service_provider_id is None:
            raise ValidationError("Payment Plan Group needs a Financial Service Provider before it can be locked.")
        if payment_plan_group.currency_id is None:
            raise ValidationError("Payment Plan Group needs a Currency before it can be locked.")

    @staticmethod
    def _validate_delivery_templates(payment_plan_group: PaymentPlanGroup, payment_plans: list[PaymentPlan]) -> None:
        """Reject up front what the group export would otherwise drop with only a warning."""
        mapped_delivery_mechanism_ids = set(
            FspXlsxTemplatePerDeliveryMechanism.objects.filter(
                financial_service_provider_id=payment_plan_group.financial_service_provider_id,
                delivery_mechanism_id__in={payment_plan.delivery_mechanism_id for payment_plan in payment_plans},
            ).values_list("delivery_mechanism_id", flat=True)
        )
        missing = [
            str(payment_plan.unicef_id)
            for payment_plan in payment_plans
            if payment_plan.delivery_mechanism_id not in mapped_delivery_mechanism_ids
        ]
        if missing:
            raise ValidationError(
                f"Every Payment Plan needs an FSP XLSX Template for its Financial Service Provider and "
                f"Delivery Mechanism. Missing for: {', '.join(missing)}."
            )
