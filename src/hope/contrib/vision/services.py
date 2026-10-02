from collections.abc import Iterable
from dataclasses import dataclass

from hope.apps.activity_log.utils import copy_model_object
from hope.contrib.vision.choices import (
    VISION_CREATION_ACKNOWLEDGEMENT_MUTABLE_STATUSES,
    VISION_RECOVERABLE_STATUSES,
    VisionErrorCode,
    VisionStatus,
)
from hope.contrib.vision.models import FundsCommitmentHeader, FundsCommitmentItem
from hope.models import PaymentPlan, log_create


@dataclass(frozen=True)
class FundsCommitmentAssignmentError(Exception):
    status: VisionStatus
    error_code: VisionErrorCode | None = None


class VisionService:
    @staticmethod
    def vision_data(payment_plan: PaymentPlan) -> dict:
        vision_data = payment_plan.internal_data.setdefault("vision", {})
        if not isinstance(vision_data, dict):
            vision_data = {}
            payment_plan.internal_data["vision"] = vision_data
        return vision_data

    @classmethod
    def set_status(
        cls,
        payment_plan: PaymentPlan,
        vision_status: VisionStatus,
        *,
        error_code: VisionErrorCode | None = None,
    ) -> None:
        vision_data = cls.vision_data(payment_plan)
        vision_data["status"] = vision_status.value
        if error_code is None:
            vision_data.pop("error_code", None)
        else:
            vision_data["error_code"] = error_code.value

    @classmethod
    def invalidate_attempt(cls, payment_plan: PaymentPlan) -> None:
        vision_data = cls.vision_data(payment_plan)
        cls.set_status(payment_plan, VisionStatus.NOT_SENT)
        vision_data.pop("sent", None)
        vision_data.pop("vision_id", None)
        vision_data.pop("fc_numbers", None)

    @classmethod
    def assign_funds_commitment_headers_from_callback(
        cls,
        payment_plan: PaymentPlan,
        fc_numbers: list[str],
    ) -> list[FundsCommitmentHeader]:
        requested_numbers = set(fc_numbers)
        eligible_header_ids = FundsCommitmentItem.objects.filter(
            office_id=payment_plan.business_area_id,
        ).values("funds_commitment_header_id")
        matching_headers = list(
            FundsCommitmentHeader.objects.select_for_update().filter(
                funds_commitment_number__in=requested_numbers,
                pk__in=eligible_header_ids,
            )
        )
        matched_numbers = {header.funds_commitment_number for header in matching_headers}
        if not requested_numbers or matched_numbers != requested_numbers:
            raise FundsCommitmentAssignmentError(VisionStatus.FC_NOT_FOUND)
        payment_plan.funds_commitment_headers.set(matching_headers)
        return matching_headers

    @classmethod
    def assign_selected_funds_commitment_headers(
        cls,
        payment_plan: PaymentPlan,
        funds_commitment_headers: Iterable[FundsCommitmentHeader],
    ) -> None:
        header_ids = {header.pk for header in funds_commitment_headers}
        if not header_ids:
            raise FundsCommitmentAssignmentError(VisionStatus.FC_NOT_FOUND)

        eligible_header_ids = FundsCommitmentItem.objects.filter(
            office_id=payment_plan.business_area_id,
        ).values("funds_commitment_header_id")
        headers = list(
            FundsCommitmentHeader.objects.select_for_update()
            .filter(pk__in=header_ids)
            .filter(pk__in=eligible_header_ids)
        )
        if len(headers) != len(header_ids):
            raise FundsCommitmentAssignmentError(VisionStatus.FC_NOT_FOUND)
        payment_plan.funds_commitment_headers.set(headers)

    @classmethod
    def process_callback(
        cls,
        payment_plan: PaymentPlan,
        *,
        vision_payment_plan_id: str,
        vision_result: str,
        fc_numbers: list[str],
    ) -> bool:
        """Return whether the callback must be rejected because its FC could not be assigned."""
        vision_data = cls.vision_data(payment_plan)
        released = vision_data.get("status") == VisionStatus.RELEASED.value
        # Callbacks for completed, disabled, aborted, or rejected workflows are logged by the view but must not
        # change FC assignments or Payment Plan status.
        if (
            released
            or not payment_plan.vision_integration_enabled
            or payment_plan.status != PaymentPlan.Status.IN_REVIEW
        ):
            return False

        # Failed attempts remain recoverable through a later corrected callback. NOT_SENT is excluded so an
        # unsolicited callback cannot start a Vision workflow.
        if payment_plan.vision_status not in VISION_RECOVERABLE_STATUSES:
            return False

        normalized_fc_numbers = list(dict.fromkeys(fc_numbers))
        is_payment_plan_created_acknowledgement = not vision_result and not normalized_fc_numbers
        fc_assignment_failed = False
        if is_payment_plan_created_acknowledgement:
            # The acknowledgement confirms receipt even if HOPE did not record the original POST response.
            vision_data["sent"] = True
            # A repeated creation acknowledgement must not replace a later FC result or failure.
            if payment_plan.vision_status in VISION_CREATION_ACKNOWLEDGEMENT_MUTABLE_STATUSES:
                vision_data["vision_id"] = vision_payment_plan_id
                vision_data.pop("fc_numbers", None)
                cls.set_status(payment_plan, VisionStatus.PP_CREATED)
        else:
            vision_data["vision_id"] = vision_payment_plan_id
            if normalized_fc_numbers:
                vision_data["fc_numbers"] = normalized_fc_numbers
            else:
                # Do not display FC numbers from an earlier callback when the latest callback did not provide any.
                vision_data.pop("fc_numbers", None)
            if vision_result != "SUCCESS":
                cls.set_status(
                    payment_plan,
                    VisionStatus.CALLBACK_FAILED,
                    error_code=VisionErrorCode.VISION_STATUS_FAILED,
                )
            elif not normalized_fc_numbers:
                cls.set_status(payment_plan, VisionStatus.FC_MISSING)
                fc_assignment_failed = True
            else:
                try:
                    cls.assign_funds_commitment_headers_from_callback(payment_plan, normalized_fc_numbers)
                except FundsCommitmentAssignmentError as error:
                    cls.set_status(payment_plan, error.status, error_code=error.error_code)
                    fc_assignment_failed = True
                else:
                    # Successful assignment completes release and continues to PG or XLSX delivery.
                    cls.complete_funds_commitment_assignment(payment_plan)

        return fc_assignment_failed

    @classmethod
    def complete_funds_commitment_assignment(cls, payment_plan: PaymentPlan) -> None:
        from hope.apps.payment.services.payment_plan_services import PaymentPlanService

        cls.set_status(payment_plan, VisionStatus.FC_ASSOCIATED)
        PaymentPlanService(payment_plan).release_from_vision()
        cls.set_status(payment_plan, VisionStatus.RELEASED)
        PaymentPlan.objects.filter(pk=payment_plan.pk).update(internal_data=payment_plan.internal_data)

        if payment_plan.can_send_to_payment_gateway:
            automatic_actor = payment_plan.created_by
            program_id = payment_plan.program.pk
            old_payment_plan = copy_model_object(payment_plan)
            payment_plan = PaymentPlanService(payment_plan).execute_update_status_action(
                input_data={"action": PaymentPlan.Action.SEND_TO_PAYMENT_GATEWAY},
                user=automatic_actor,
            )
            log_create(
                mapping=PaymentPlan.ACTIVITY_LOG_MAPPING,
                business_area_field="business_area",
                user=automatic_actor,
                programs=program_id,
                old_object=old_payment_plan,
                new_object=payment_plan,
            )

    @classmethod
    def recover_with_funds_commitment_headers(
        cls,
        payment_plan: PaymentPlan,
        funds_commitment_headers: Iterable[FundsCommitmentHeader],
    ) -> None:
        if not cls.can_recover_with_funds_commitment_headers(payment_plan):
            raise FundsCommitmentAssignmentError(
                VisionStatus.CALLBACK_FAILED,
                VisionErrorCode.FC_CONFLICT,
            )
        cls.assign_selected_funds_commitment_headers(payment_plan, funds_commitment_headers)
        cls.complete_funds_commitment_assignment(payment_plan)

    @classmethod
    def can_recover_with_funds_commitment_headers(cls, payment_plan: PaymentPlan) -> bool:
        vision_status = payment_plan.vision_status
        return (
            payment_plan.status == PaymentPlan.Status.IN_REVIEW
            and vision_status in VISION_RECOVERABLE_STATUSES
            and payment_plan.vision_integration_enabled
        )
