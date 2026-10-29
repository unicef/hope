from __future__ import annotations

from typing import IO, TYPE_CHECKING, Any, cast

from django.db import transaction
from django.db.models import Exists, OuterRef
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from hope.apps.activity_log.utils import copy_model_object
from hope.apps.payment.celery_tasks import (
    create_follow_up_instruction_delivery_xlsx_async_task,
    import_follow_up_instruction_reconciliation_from_xlsx_async_task,
    recalculate_owner_exchange_rate_async_task,
    send_follow_up_instruction_notification_emails_async_task,
)
from hope.apps.payment.flows import FollowUpInstructionFlow
from hope.apps.payment.services.payment_plan_services import (
    ACTION_TO_APPROVAL_TYPE,
    STAGE_REACHED_NOTIFICATION,
    PaymentPlanService,
    record_stage_reached,
    required_number_for,
    validate_approval_count,
)
from hope.apps.payment.utils import inactive_currency_reason, log_payment_plan_approval
from hope.models import (
    Approval,
    ApprovalProcess,
    FollowUpInstruction,
    Payment,
    PaymentPlan,
    PaymentPlanGroup,
    log_create,
)

if TYPE_CHECKING:
    import datetime

    from hope.models import Program, User


ACTION_TO_STATUSES = {
    PaymentPlan.Action.APPROVE.value: (FollowUpInstruction.Status.IN_APPROVAL,),
    PaymentPlan.Action.AUTHORIZE.value: (FollowUpInstruction.Status.IN_AUTHORIZATION,),
    PaymentPlan.Action.REVIEW.value: (FollowUpInstruction.Status.IN_REVIEW,),
    PaymentPlan.Action.REJECT.value: (
        FollowUpInstruction.Status.IN_APPROVAL,
        FollowUpInstruction.Status.IN_AUTHORIZATION,
        FollowUpInstruction.Status.IN_REVIEW,
    ),
}


class FollowUpInstructionService:
    def __init__(self, program: "Program | None" = None, instruction: FollowUpInstruction | None = None):
        self.instruction = instruction
        self.program = program or (instruction.program if instruction else None)
        if self.program is None:
            raise ValueError("Program or instruction is required.")

    def _get_source_groups(self, payment_plan_group_ids: list[str]) -> list[PaymentPlanGroup]:
        groups = list(PaymentPlanGroup.objects.filter(id__in=payment_plan_group_ids, cycle__program=self.program))
        if len(groups) != len(payment_plan_group_ids):
            raise ValidationError("One or more Payment Plan Groups do not exist in the selected program.")
        return groups

    def _get_applicable_source_payment_plans(self, payment_plan_group_ids: list[str]) -> list[PaymentPlan]:
        self._get_source_groups(payment_plan_group_ids)
        follow_up_children = PaymentPlan.objects.filter(
            source_payment_plan_id=OuterRef("pk"),
            plan_type=PaymentPlan.PlanType.FOLLOW_UP,
        )
        source_plans = (
            PaymentPlan.objects.filter(
                payment_plan_group_id__in=payment_plan_group_ids,
                program_cycle__program=self.program,
                plan_type=PaymentPlan.PlanType.REGULAR,
            )
            .annotate(has_follow_up_child=Exists(follow_up_children))
            .exclude(follow_up_instruction__isnull=False)
            .filter(has_follow_up_child=False)
            .select_related(
                "business_area",
                "delivery_mechanism",
                "payment_plan_group__currency",
                "payment_plan_group__financial_service_provider",
                "program_cycle",
            )
            .prefetch_related("payment_plan_purposes")
            .order_by("created_at")
        )
        applicable = cast(
            "list[PaymentPlan]",
            [
                payment_plan
                for payment_plan in source_plans
                if payment_plan.unsuccessful_payments_for_follow_up().exists()
            ],
        )
        if not applicable:
            raise ValidationError("No applicable Payment Plans were found for the selected Payment Plan Groups.")
        self._validate_shared_configuration(applicable)
        return applicable

    @staticmethod
    def _validate_shared_configuration(source_plans: list[PaymentPlan]) -> None:
        fsp_ids = {payment_plan.payment_plan_group.financial_service_provider_id for payment_plan in source_plans}
        delivery_mechanism_ids = {payment_plan.delivery_mechanism_id for payment_plan in source_plans}
        currency_ids = {payment_plan.payment_plan_group.currency_id for payment_plan in source_plans}
        use_payment_gateway_values = {
            payment_plan.payment_plan_group.use_payment_gateway for payment_plan in source_plans
        }
        if None in fsp_ids or len(fsp_ids) != 1:
            raise ValidationError("Applicable Payment Plans must share the same Financial Service Provider.")
        if len(use_payment_gateway_values) != 1:
            raise ValidationError("Applicable Payment Plans must share the same Use Payment Gateway setting.")
        if None in delivery_mechanism_ids or len(delivery_mechanism_ids) != 1:
            raise ValidationError("Applicable Payment Plans must share the same Delivery Mechanism.")
        if None in currency_ids or len(currency_ids) != 1:
            # Variants of one redenominated currency share `code`; str() carries `vision_code` to tell them apart.
            found = sorted(
                {str(payment_plan.currency) if payment_plan.currency else "none" for payment_plan in source_plans}
            )
            raise ValidationError(f"Applicable Payment Plans must share the same Currency. Found: {', '.join(found)}.")

    @transaction.atomic
    def create(
        self,
        user: "User",
        payment_plan_group_ids: list[str],
        dispersion_start_date: datetime.date,
        dispersion_end_date: datetime.date,
    ) -> FollowUpInstruction:
        source_plans = self._get_applicable_source_payment_plans(payment_plan_group_ids)
        source_group = source_plans[0].payment_plan_group
        instruction = FollowUpInstruction.objects.create(
            business_area=self.program.business_area,
            program=self.program,
            created_by=user,
            financial_service_provider=source_group.financial_service_provider,
            currency=source_group.currency,
            use_payment_gateway=source_group.use_payment_gateway,
            dispersion_start_date=dispersion_start_date,
            dispersion_end_date=dispersion_end_date,
        )
        for source_plan in source_plans:
            follow_up_payment_plan = PaymentPlanService(source_plan).create_follow_up(
                user=user,
                follow_up_instruction=instruction,
            )
            log_create(
                mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
                business_area_field="business_area",
                user=user,
                programs=follow_up_payment_plan.program.pk,
                old_object=None,
                new_object=follow_up_payment_plan,
            )
        return instruction

    def _get_child_payment_plans(self) -> list[PaymentPlan]:
        instruction = self._require_instruction()
        return list(instruction.payment_plans.select_related("program_cycle__program").order_by("created_at"))

    def _require_instruction(self) -> FollowUpInstruction:
        if self.instruction is None:
            raise ValueError("Instruction is required.")
        return self.instruction

    def _locked_for_update(self) -> FollowUpInstruction:
        instruction = FollowUpInstruction.objects.select_for_update().get(pk=self._require_instruction().pk)
        self.instruction = instruction
        return instruction

    def _validate_child_payment_plans_statuses(self, allowed_statuses: set[str], action_label: str) -> None:
        child_payment_plans = self._get_child_payment_plans()
        if not child_payment_plans:
            raise ValidationError("This Follow Up Instruction has no child Payment Plans.")
        if any(payment_plan.status not in allowed_statuses for payment_plan in child_payment_plans):
            raise ValidationError(
                f"{action_label} is not available for child Payment Plans outside statuses: "
                f"{', '.join(sorted(allowed_statuses))}."
            )

    def _validate_instruction_has_eligible_payments(self) -> None:
        instruction = self._require_instruction()
        if not Payment.objects.filter(parent__follow_up_instruction=instruction).eligible().exists():
            raise ValidationError("Export failed: The Payment List is empty.")

    def _validate_delivery_template_exists(self) -> None:
        from hope.models import FinancialServiceProviderXlsxTemplate

        child_payment_plans = self._get_child_payment_plans()
        first_payment_plan = child_payment_plans[0]
        fsp = first_payment_plan.financial_service_provider
        delivery_mechanism = first_payment_plan.delivery_mechanism
        if fsp is None or delivery_mechanism is None:
            raise ValidationError(
                "Instruction delivery export requires child Payment Plans with a Financial Service Provider "
                "and Delivery Mechanism."
            )
        template = fsp.get_xlsx_template(delivery_mechanism)
        if template is None or not FinancialServiceProviderXlsxTemplate.objects.filter(pk=template.pk).exists():
            raise ValidationError(
                "Instruction delivery export requires an FSP XLSX Template for the shared Financial Service Provider "
                "and Delivery Mechanism."
            )

    def _validate_currency_is_active(self) -> None:
        # Child plans share one currency (_validate_shared_configuration), so the first one speaks for all.
        if reason := inactive_currency_reason(self._get_child_payment_plans()[0]):
            raise ValidationError(reason)

    def _validate_no_background_action_in_progress(self, action_label: str) -> None:
        instruction = self._require_instruction()
        if instruction.background_action_status not in (
            None,
            *FollowUpInstruction.BACKGROUND_ACTION_ERROR_STATES,
        ):
            raise ValidationError(f"{action_label} is not available while another background action is in progress.")

    @staticmethod
    def _log_payment_plan_change(
        payment_plan: PaymentPlan,
        user: "User",
        old_payment_plan: PaymentPlan,
    ) -> None:
        log_create(
            mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
            business_area_field="business_area",
            user=user,
            programs=payment_plan.program.pk,
            old_object=old_payment_plan,
            new_object=payment_plan,
        )

    @transaction.atomic
    def execute_payment_plan_action(
        self,
        action: str,
        user: "User",
        extra_input_data: dict[str, Any] | None = None,
    ) -> FollowUpInstruction:
        instruction = self._require_instruction()
        for payment_plan in self._get_child_payment_plans():
            old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
            input_data = {"action": action, **(extra_input_data or {})}
            updated_payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(
                input_data=input_data,
                user=user,
                as_manager=True,
            )
            self._log_payment_plan_change(updated_payment_plan, user, old_payment_plan)
        return instruction

    @transaction.atomic
    def send_for_approval(self, user: "User") -> FollowUpInstruction:
        """Send every child plan for approval; one approval process, on the instruction, sized by its total."""
        instruction = self._locked_for_update()
        self._validate_child_payment_plans_statuses({PaymentPlan.Status.LOCKED_FSP}, "Send for Approval")
        for payment_plan in self._get_child_payment_plans():
            old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
            PaymentPlanService(payment_plan).transition_send_for_approval()
            self._log_payment_plan_change(payment_plan, user, old_payment_plan)
        ApprovalProcess.objects.create(
            follow_up_instruction=instruction,
            sent_for_approval_by=user,
            sent_for_approval_date=timezone.now(),
            approval_number_required=instruction.approval_number_required,
            authorization_number_required=instruction.authorization_number_required,
            finance_release_number_required=instruction.finance_release_number_required,
        )
        send_follow_up_instruction_notification_emails_async_task(
            instruction, PaymentPlan.Action.SEND_FOR_APPROVAL.value, str(user.pk), timezone.now().isoformat()
        )
        return instruction

    @transaction.atomic
    def acceptance_process(self, action: str, user: "User", comment: str | None = None) -> FollowUpInstruction:
        """Record one approve / authorize / release / reject on the instruction.

        When the required count is reached every child plan moves to the next stage together.
        """
        approval_type = ACTION_TO_APPROVAL_TYPE[action]
        instruction = self._locked_for_update()
        instruction_status = instruction.status
        if instruction_status not in ACTION_TO_STATUSES[action]:
            raise ValidationError(
                f"Not possible to create {action} for Follow Up Instruction within status {instruction_status}"
            )
        approval_process = instruction.approval_process.first()
        if approval_process is None:
            raise ValidationError(f"Approval Process object not found for Follow Up Instruction {instruction.pk}")
        required_number = required_number_for(approval_process, approval_type)
        validate_approval_count(approval_process, approval_type, required_number, instruction_status, user)

        Approval.objects.create(approval_process=approval_process, created_by=user, type=approval_type, comment=comment)
        log_payment_plan_approval(instruction, user, approval_type, comment)

        if approval_process.approvals.filter(type=approval_type).count() >= required_number:
            record_stage_reached(approval_process, approval_type, user)
            for payment_plan in self._get_child_payment_plans():
                old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
                PaymentPlanService(payment_plan).apply_acceptance_stage(approval_type, user)
                self._log_payment_plan_change(payment_plan, user, old_payment_plan)
            if approval_type == Approval.FINANCE_RELEASE:
                transaction.on_commit(lambda: recalculate_owner_exchange_rate_async_task(instruction, str(user.pk)))
            if notification_action := STAGE_REACHED_NOTIFICATION.get(approval_type):
                send_follow_up_instruction_notification_emails_async_task(
                    instruction, notification_action.value, str(user.pk), timezone.now().isoformat()
                )
        return instruction

    @transaction.atomic
    def ready_for_closure(self, user: "User") -> FollowUpInstruction:
        instruction = self._locked_for_update()
        self._validate_child_payment_plans_statuses({PaymentPlan.Status.FINISHED}, "Mark as Ready for Closure")
        for payment_plan in self._get_child_payment_plans():
            old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
            updated_payment_plan = PaymentPlanService(payment_plan).ready_for_closure()
            self._log_payment_plan_change(updated_payment_plan, user, old_payment_plan)
        send_follow_up_instruction_notification_emails_async_task(
            instruction, PaymentPlan.Action.MARK_READY_FOR_CLOSURE.value, str(user.pk), timezone.now().isoformat()
        )
        return instruction

    @transaction.atomic
    def send_back_to_finished(self, user: "User") -> FollowUpInstruction:
        instruction = self._locked_for_update()
        self._validate_child_payment_plans_statuses({PaymentPlan.Status.READY_FOR_CLOSURE}, "Send Back")
        for payment_plan in self._get_child_payment_plans():
            old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
            updated_payment_plan = PaymentPlanService(payment_plan).send_back_to_finished()
            self._log_payment_plan_change(updated_payment_plan, user, old_payment_plan)
        send_follow_up_instruction_notification_emails_async_task(
            instruction, PaymentPlan.Action.SEND_BACK_TO_FINISHED.value, str(user.pk), timezone.now().isoformat()
        )
        return instruction

    @transaction.atomic
    def close(self, user: "User", closure_comment: str | None) -> FollowUpInstruction:
        instruction = self._locked_for_update()
        self._validate_child_payment_plans_statuses({PaymentPlan.Status.READY_FOR_CLOSURE}, "Close instruction")
        for payment_plan in self._get_child_payment_plans():
            old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
            updated_payment_plan = PaymentPlanService(payment_plan).close(
                closure_comment=closure_comment, user_id=str(user.pk)
            )
            self._log_payment_plan_change(updated_payment_plan, user, old_payment_plan)
        instruction.closure_comment = closure_comment
        instruction.closed_by = user
        instruction.save(update_fields=["closure_comment", "closed_by", "updated_at"])
        return instruction

    @transaction.atomic
    def abort(self, user: "User", abort_comment: str | None) -> FollowUpInstruction:
        instruction = self._locked_for_update()
        for payment_plan in self._get_child_payment_plans():
            old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
            updated_payment_plan = PaymentPlanService(payment_plan).abort(abort_comment, user_id=str(user.pk))
            self._log_payment_plan_change(updated_payment_plan, user, old_payment_plan)
        instruction.abort_comment = abort_comment or ""
        instruction.save(update_fields=["abort_comment", "updated_at"])
        return instruction

    @transaction.atomic
    def reactivate_abort(self, user: "User") -> FollowUpInstruction:
        instruction = self._require_instruction()
        for payment_plan in self._get_child_payment_plans():
            old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
            updated_payment_plan = PaymentPlanService(payment_plan).reactivate_abort()
            self._log_payment_plan_change(updated_payment_plan, user, old_payment_plan)
        return instruction

    @transaction.atomic
    def delivery_export_xlsx(self, user: "User") -> FollowUpInstruction:
        instruction = self._require_instruction()
        self._validate_child_payment_plans_statuses(
            {
                PaymentPlan.Status.ACCEPTED,
                PaymentPlan.Status.FINISHED,
            },
            "Instruction reconciliation export",
        )
        self._validate_no_background_action_in_progress("Instruction reconciliation export")
        self._validate_instruction_has_eligible_payments()
        self._validate_delivery_template_exists()
        self._validate_currency_is_active()
        flow = FollowUpInstructionFlow(instruction)
        flow.background_action_status_xlsx_exporting()
        instruction.save(update_fields=["background_action_status", "updated_at"])
        create_follow_up_instruction_delivery_xlsx_async_task(instruction, str(user.id))
        instruction.refresh_from_db(fields=["background_action_status", "export_file"])
        return instruction

    @transaction.atomic
    def import_delivery_xlsx(
        self,
        user: "User",
        file: IO[bytes],
    ) -> FollowUpInstruction:
        from django.contrib.admin.options import get_content_type_for_model

        from hope.models import FileTemp

        instruction = self._require_instruction()
        self._validate_child_payment_plans_statuses(
            {
                PaymentPlan.Status.ACCEPTED,
                PaymentPlan.Status.FINISHED,
            },
            "Instruction reconciliation import",
        )
        self._validate_no_background_action_in_progress("Instruction reconciliation import")
        file.seek(0)
        file_temp = FileTemp.objects.create(
            object_id=instruction.pk,
            content_type=get_content_type_for_model(instruction),
            created_by=user,
            file=file,
        )
        flow = FollowUpInstructionFlow(instruction)
        flow.background_action_status_xlsx_importing_reconciliation()
        instruction.reconciliation_import_file = file_temp
        instruction.save(update_fields=["background_action_status", "reconciliation_import_file", "updated_at"])
        import_follow_up_instruction_reconciliation_from_xlsx_async_task(instruction, str(user.id))
        instruction.refresh_from_db(fields=["background_action_status", "reconciliation_import_file"])
        return instruction
