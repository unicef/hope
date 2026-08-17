from dataclasses import dataclass

from hope.contrib.vision.choices import VisionErrorCode, VisionStatus
from hope.contrib.vision.models import FundsCommitmentItem
from hope.models import PaymentPlan


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

    @staticmethod
    def assign_funds_commitment(payment_plan: PaymentPlan, fc_num: str) -> None:
        matching_items = FundsCommitmentItem.objects.filter(
            funds_commitment_group__funds_commitment_number=fc_num,
            office=payment_plan.business_area,
        )
        group_ids = list(matching_items.values_list("funds_commitment_group_id", flat=True).distinct())
        if not group_ids:
            raise FundsCommitmentAssignmentError(VisionStatus.FC_NOT_FOUND)
        if len(group_ids) != 1:
            raise FundsCommitmentAssignmentError(
                VisionStatus.CALLBACK_FAILED,
                VisionErrorCode.FC_AMBIGUOUS,
            )

        group_id = group_ids[0]
        items = list(
            FundsCommitmentItem.objects.select_for_update().filter(
                funds_commitment_group_id=group_id,
                office=payment_plan.business_area,
            )
        )
        if any(item.payment_plan_id not in {None, payment_plan.pk} for item in items):
            raise FundsCommitmentAssignmentError(
                VisionStatus.CALLBACK_FAILED,
                VisionErrorCode.FC_CONFLICT,
            )

        has_items_from_another_group = (
            FundsCommitmentItem.objects.select_for_update()
            .filter(payment_plan=payment_plan)
            .exclude(funds_commitment_group_id=group_id)
            .exists()
        )
        if has_items_from_another_group:
            raise FundsCommitmentAssignmentError(
                VisionStatus.CALLBACK_FAILED,
                VisionErrorCode.FC_CONFLICT,
            )

        # TODO(Vision decision): Confirm whether fc_num identifies an FC group or a specific item. Treating it as a
        # group number and assigning every BA-scoped item is provisional until the callback contract is confirmed.
        FundsCommitmentItem.objects.filter(
            pk__in=[item.pk for item in items],
            payment_plan__isnull=True,
        ).update(payment_plan=payment_plan)

    @classmethod
    def _has_fc_assignment_failure(cls, payment_plan: PaymentPlan) -> bool:
        vision_data = cls.vision_data(payment_plan)
        if payment_plan.vision_status in {
            VisionStatus.FC_MISSING.value,
            VisionStatus.FC_NOT_FOUND.value,
        }:
            return True
        return payment_plan.vision_status == VisionStatus.CALLBACK_FAILED.value and vision_data.get("error_code") in {
            VisionErrorCode.FC_AMBIGUOUS.value,
            VisionErrorCode.FC_CONFLICT.value,
        }

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
        from hope.apps.payment.services.payment_plan_services import PaymentPlanService

        vision_data = cls.vision_data(payment_plan)
        released = vision_data.get("status") == VisionStatus.RELEASED.value
        # TODO(Vision decision): A completed callback is terminal for idempotency. Confirm whether a later callback
        # with a different Vision ID or FC should be ignored, rejected, or escalated for manual investigation.
        if (
            released
            or not payment_plan.vision_integration_enabled
            or payment_plan.status != PaymentPlan.Status.IN_REVIEW
        ):
            # Disabled flags and abort/reject both return the plan to the manual flow. The callback is logged by the
            # view but must not assign FC data or release the plan.
            return False
        if payment_plan.vision_status != VisionStatus.WAITING_FOR_CALLBACK.value:
            # TODO(Vision decision): The callback is logged by the view but acknowledged with OK for now. Confirm
            # whether an unexpected callback state should instead return KO to Vision or notify an administrator.
            return cls._has_fc_assignment_failure(payment_plan)

        vision_data["vision_id"] = vision_payment_plan_id
        if fc_num:
            vision_data["fc_num"] = fc_num
        if vision_result != "SUCCESS":
            cls.set_status(
                payment_plan,
                VisionStatus.CALLBACK_FAILED,
                error_code=VisionErrorCode.VISION_STATUS_FAILED,
            )
            return False

        if not fc_num:
            cls.set_status(payment_plan, VisionStatus.FC_MISSING)
            return True

        try:
            cls.assign_funds_commitment(payment_plan, fc_num)
        except FundsCommitmentAssignmentError as error:
            cls.set_status(payment_plan, error.status, error_code=error.error_code)
            return True

        cls.set_status(payment_plan, VisionStatus.FC_ASSOCIATED)
        PaymentPlanService(payment_plan).release_from_vision()
        cls.set_status(payment_plan, VisionStatus.RELEASED)
        PaymentPlan.objects.filter(pk=payment_plan.pk).update(internal_data=payment_plan.internal_data)

        if payment_plan.can_send_to_payment_gateway:
            PaymentPlanService(payment_plan).execute_update_status_action(
                input_data={"action": PaymentPlan.Action.SEND_TO_PAYMENT_GATEWAY},
                user=payment_plan.created_by,
            )
        return False
