from __future__ import annotations

from typing import IO, TYPE_CHECKING, Any, cast

from django.db import transaction
from django.db.models import Exists, OuterRef
from rest_framework.exceptions import ValidationError

from hope.apps.activity_log.utils import copy_model_object
from hope.apps.payment.celery_tasks import (
    create_follow_up_instruction_delivery_xlsx_async_task,
    import_follow_up_instruction_reconciliation_from_xlsx_async_task,
)
from hope.apps.payment.flows import FollowUpInstructionFlow
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.models import FollowUpInstruction, Payment, PaymentPlan, PaymentPlanGroup, log_create

if TYPE_CHECKING:
    import datetime

    from hope.models import Program, User


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
                "currency",
                "delivery_mechanism",
                "financial_service_provider",
                "payment_plan_group",
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
        fsp_ids = {payment_plan.financial_service_provider_id for payment_plan in source_plans}
        delivery_mechanism_ids = {payment_plan.delivery_mechanism_id for payment_plan in source_plans}
        currency_ids = {payment_plan.currency_id for payment_plan in source_plans}
        if None in fsp_ids or len(fsp_ids) != 1:
            raise ValidationError("Applicable Payment Plans must share the same Financial Service Provider.")
        if None in delivery_mechanism_ids or len(delivery_mechanism_ids) != 1:
            raise ValidationError("Applicable Payment Plans must share the same Delivery Mechanism.")
        if None in currency_ids or len(currency_ids) != 1:
            raise ValidationError("Applicable Payment Plans must share the same Currency.")

    @transaction.atomic
    def create(
        self,
        user: "User",
        payment_plan_group_ids: list[str],
        dispersion_start_date: datetime.date,
        dispersion_end_date: datetime.date,
    ) -> FollowUpInstruction:
        source_plans = self._get_applicable_source_payment_plans(payment_plan_group_ids)
        instruction = FollowUpInstruction.objects.create(
            business_area=self.program.business_area,
            program=self.program,
            created_by=user,
        )
        for source_plan in source_plans:
            follow_up_payment_plan = PaymentPlanService(source_plan).create_follow_up(
                user=user,
                dispersion_start_date=dispersion_start_date,
                dispersion_end_date=dispersion_end_date,
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
                allow_instruction_managed=True,
            )
            self._log_payment_plan_change(updated_payment_plan, user, old_payment_plan)
        return instruction

    @transaction.atomic
    def close(self, user: "User") -> FollowUpInstruction:
        instruction = self._require_instruction()
        self._validate_child_payment_plans_statuses(
            {PaymentPlan.Status.FINISHED},
            "Close instruction",
        )
        for payment_plan in self._get_child_payment_plans():
            old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
            service = PaymentPlanService(payment_plan)
            service.ready_for_closure()
            updated_payment_plan = service.close(
                closure_comment="Comment",
                user_id=str(user.pk),
            )
            self._log_payment_plan_change(updated_payment_plan, user, old_payment_plan)
        return instruction

    @transaction.atomic
    def abort(self, user: "User", abort_comment: str | None) -> FollowUpInstruction:
        instruction = self._require_instruction()
        for payment_plan in self._get_child_payment_plans():
            old_payment_plan = cast("PaymentPlan", copy_model_object(payment_plan))
            updated_payment_plan = PaymentPlanService(payment_plan).abort(abort_comment)
            self._log_payment_plan_change(updated_payment_plan, user, old_payment_plan)
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
