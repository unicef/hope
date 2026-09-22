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
        vision_data.pop("fc_num", None)

    @classmethod
    def assign_funds_commitment_from_callback(
        cls,
        payment_plan: PaymentPlan,
        fc_num: str,
    ) -> FundsCommitmentHeader:
        matching_header_ids = FundsCommitmentItem.objects.filter(
            funds_commitment_header__funds_commitment_number=fc_num,
            office=payment_plan.business_area,
        ).values("funds_commitment_header_id")
        matching_headers = list(FundsCommitmentHeader.objects.select_for_update().filter(pk__in=matching_header_ids))
        if not matching_headers:
            raise FundsCommitmentAssignmentError(VisionStatus.FC_NOT_FOUND)
        if len(matching_headers) != 1:
            raise FundsCommitmentAssignmentError(
                VisionStatus.CALLBACK_FAILED,
                VisionErrorCode.FC_AMBIGUOUS,
            )

        funds_commitment_header = matching_headers[0]
        items = list(
            FundsCommitmentItem.objects.select_for_update().filter(funds_commitment_header=funds_commitment_header)
        )
        if any(item.payment_plan_id not in {None, payment_plan.pk} for item in items):
            raise FundsCommitmentAssignmentError(
                VisionStatus.CALLBACK_FAILED,
                VisionErrorCode.FC_CONFLICT,
            )

        if (
            FundsCommitmentItem.objects.select_for_update()
            .filter(payment_plan=payment_plan)
            .exclude(funds_commitment_header=funds_commitment_header)
            .exists()
        ):
            raise FundsCommitmentAssignmentError(
                VisionStatus.CALLBACK_FAILED,
                VisionErrorCode.FC_CONFLICT,
            )

        FundsCommitmentItem.objects.filter(
            pk__in=[item.pk for item in items],
            payment_plan__isnull=True,
        ).update(payment_plan=payment_plan)
        return funds_commitment_header

    @classmethod
    def assign_selected_funds_commitment_items(
        cls,
        payment_plan: PaymentPlan,
        funds_commitment_items: Iterable[FundsCommitmentItem],
    ) -> None:
        item_ids = {item.pk for item in funds_commitment_items}
        if not item_ids:
            raise FundsCommitmentAssignmentError(VisionStatus.FC_NOT_FOUND)

        items = list(FundsCommitmentItem.objects.select_for_update().filter(pk__in=item_ids))
        if len(items) != len(item_ids) or any(item.office_id != payment_plan.business_area_id for item in items):
            raise FundsCommitmentAssignmentError(VisionStatus.FC_NOT_FOUND)
        header_ids = {item.funds_commitment_header_id for item in items}
        if len(header_ids) != 1:
            raise FundsCommitmentAssignmentError(
                VisionStatus.CALLBACK_FAILED,
                VisionErrorCode.FC_AMBIGUOUS,
            )
        if any(item.payment_plan_id not in {None, payment_plan.pk} for item in items):
            raise FundsCommitmentAssignmentError(
                VisionStatus.CALLBACK_FAILED,
                VisionErrorCode.FC_CONFLICT,
            )

        header_id = header_ids.pop()
        if (
            FundsCommitmentItem.objects.select_for_update()
            .filter(payment_plan=payment_plan)
            .exclude(funds_commitment_header_id=header_id)
            .exists()
        ):
            raise FundsCommitmentAssignmentError(
                VisionStatus.CALLBACK_FAILED,
                VisionErrorCode.FC_CONFLICT,
            )

        FundsCommitmentItem.objects.filter(pk__in=item_ids, payment_plan__isnull=True).update(payment_plan=payment_plan)

    @classmethod
    def process_callback(
        cls,
        payment_plan: PaymentPlan,
        *,
        vision_payment_plan_id: str,
        vision_result: str,
        fc_num: str,
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

        is_payment_plan_created_acknowledgement = not vision_result and not fc_num
        fc_assignment_failed = False
        if is_payment_plan_created_acknowledgement:
            # The acknowledgement confirms receipt even if HOPE did not record the original POST response.
            vision_data["sent"] = True
            # A repeated creation acknowledgement must not replace a later FC result or failure.
            if payment_plan.vision_status in VISION_CREATION_ACKNOWLEDGEMENT_MUTABLE_STATUSES:
                vision_data["vision_id"] = vision_payment_plan_id
                vision_data.pop("fc_num", None)
                cls.set_status(payment_plan, VisionStatus.PP_CREATED)
        else:
            vision_data["vision_id"] = vision_payment_plan_id
            if fc_num:
                vision_data["fc_num"] = fc_num
            else:
                # Do not display an FC number from an earlier callback when the latest callback did not provide one.
                vision_data.pop("fc_num", None)
            if vision_result != "SUCCESS":
                cls.set_status(
                    payment_plan,
                    VisionStatus.CALLBACK_FAILED,
                    error_code=VisionErrorCode.VISION_STATUS_FAILED,
                )
            elif not fc_num:
                cls.set_status(payment_plan, VisionStatus.FC_MISSING)
                fc_assignment_failed = True
            else:
                try:
                    cls.assign_funds_commitment_from_callback(payment_plan, fc_num)
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
    def recover_with_funds_commitment_items(
        cls,
        payment_plan: PaymentPlan,
        funds_commitment_items: Iterable[FundsCommitmentItem],
    ) -> None:
        if not cls.can_recover_with_funds_commitment_items(payment_plan):
            raise FundsCommitmentAssignmentError(
                VisionStatus.CALLBACK_FAILED,
                VisionErrorCode.FC_CONFLICT,
            )
        cls.assign_selected_funds_commitment_items(payment_plan, funds_commitment_items)
        cls.complete_funds_commitment_assignment(payment_plan)

    @classmethod
    def can_recover_with_funds_commitment_items(cls, payment_plan: PaymentPlan) -> bool:
        vision_status = payment_plan.vision_status
        return (
            payment_plan.status == PaymentPlan.Status.IN_REVIEW
            and vision_status in VISION_RECOVERABLE_STATUSES
            and payment_plan.vision_integration_enabled
        )
