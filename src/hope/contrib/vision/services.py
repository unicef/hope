from collections.abc import Iterable
from dataclasses import dataclass

from django.db import transaction

from hope.contrib.vision.choices import (
    VISION_CREATION_ACKNOWLEDGEMENT_MUTABLE_STATUSES,
    VISION_RECOVERABLE_STATUSES,
    VisionErrorCode,
    VisionStatus,
)
from hope.contrib.vision.models import FundsCommitmentHeader, FundsCommitmentItem
from hope.models import PaymentPlan, PaymentPlanGroup


@dataclass(frozen=True)
class FundsCommitmentAssignmentError(Exception):
    status: VisionStatus
    error_code: VisionErrorCode | None = None


class VisionService:
    @staticmethod
    def vision_data(group: PaymentPlanGroup) -> dict:
        vision_data = group.internal_data.setdefault("vision", {})
        if not isinstance(vision_data, dict):
            vision_data = {}
            group.internal_data["vision"] = vision_data
        return vision_data

    @classmethod
    def set_status(
        cls,
        group: PaymentPlanGroup,
        vision_status: VisionStatus,
        *,
        error_code: VisionErrorCode | None = None,
    ) -> None:
        vision_data = cls.vision_data(group)
        vision_data["status"] = vision_status.value
        if error_code is None:
            vision_data.pop("error_code", None)
        else:
            vision_data["error_code"] = error_code.value

    @classmethod
    def invalidate_attempt(cls, group: PaymentPlanGroup) -> None:
        vision_data = cls.vision_data(group)
        cls.set_status(group, VisionStatus.NOT_SENT)
        vision_data.pop("sent", None)
        vision_data.pop("vision_id", None)
        vision_data.pop("fc_numbers", None)

    @classmethod
    def assign_funds_commitment_headers_from_callback(
        cls,
        group: PaymentPlanGroup,
        fc_numbers: list[str],
    ) -> list[FundsCommitmentHeader]:
        requested_numbers = set(fc_numbers)
        eligible_header_ids = FundsCommitmentItem.objects.filter(
            office_id=group.business_area.id,
        ).values("funds_commitment_header_id")
        matching_headers = list(
            FundsCommitmentHeader.objects.select_for_update()
            .filter(
                funds_commitment_number__in=requested_numbers,
                pk__in=eligible_header_ids,
            )
            .order_by("pk")
        )
        matched_numbers = {header.funds_commitment_number for header in matching_headers}
        if not requested_numbers or matched_numbers != requested_numbers:
            raise FundsCommitmentAssignmentError(VisionStatus.FC_NOT_FOUND)
        group.funds_commitment_headers.add(*matching_headers)
        return matching_headers

    @classmethod
    def assign_selected_funds_commitment_headers(
        cls,
        payment_plan_group: PaymentPlanGroup,
        funds_commitment_headers: Iterable[FundsCommitmentHeader],
        *,
        replace: bool = True,
    ) -> None:
        header_ids = {header.pk for header in funds_commitment_headers}
        if not header_ids:
            raise FundsCommitmentAssignmentError(VisionStatus.FC_NOT_FOUND)

        group = (
            PaymentPlanGroup.objects.select_for_update().select_related("cycle__program").get(pk=payment_plan_group.pk)
        )
        eligible_header_ids = FundsCommitmentItem.objects.filter(
            office_id=group.cycle.program.business_area_id,
        ).values("funds_commitment_header_id")
        headers = list(
            FundsCommitmentHeader.objects.select_for_update()
            .filter(pk__in=header_ids)
            .filter(pk__in=eligible_header_ids)
            .order_by("pk")
        )
        if len(headers) != len(header_ids):
            raise FundsCommitmentAssignmentError(VisionStatus.FC_NOT_FOUND)
        if replace:
            group.funds_commitment_headers.set(headers)
        else:
            group.funds_commitment_headers.add(*headers)

    @classmethod
    def process_callback(
        cls,
        group: PaymentPlanGroup,
        *,
        vision_payment_plan_id: str,
        vision_result: str,
        fc_numbers: list[str],
    ) -> bool:
        """Return whether the callback must be rejected because its FC could not be assigned."""
        vision_data = cls.vision_data(group)
        released = vision_data.get("status") == VisionStatus.RELEASED.value
        # Callbacks for completed, disabled, aborted, or rejected workflows are logged by the view but must not
        # change FC assignments or group status.
        if released or not group.vision_managed or group.status != PaymentPlanGroup.Status.IN_REVIEW:
            return False

        # Failed attempts remain recoverable through a later corrected callback. NOT_SENT is excluded so an
        # unsolicited callback cannot start a Vision workflow.
        if group.vision_status not in VISION_RECOVERABLE_STATUSES:
            return False

        normalized_fc_numbers = list(dict.fromkeys(fc_numbers))
        # Any callback for the active request confirms that Vision received the group.
        vision_data["sent"] = True
        is_payment_plan_created_acknowledgement = vision_result == "SUCCESS" and not normalized_fc_numbers
        fc_assignment_failed = False
        if is_payment_plan_created_acknowledgement:
            # A repeated creation acknowledgement must not replace a later FC result or failure.
            if group.vision_status in VISION_CREATION_ACKNOWLEDGEMENT_MUTABLE_STATUSES:
                vision_data["vision_id"] = vision_payment_plan_id
                vision_data.pop("fc_numbers", None)
                cls.set_status(group, VisionStatus.PP_CREATED)
        else:
            vision_data["vision_id"] = vision_payment_plan_id
            if normalized_fc_numbers:
                vision_data["fc_numbers"] = normalized_fc_numbers
            else:
                # Do not display FC numbers from an earlier callback when the latest callback did not provide any.
                vision_data.pop("fc_numbers", None)
            if vision_result != "SUCCESS":
                cls.set_status(
                    group,
                    VisionStatus.CALLBACK_FAILED,
                    error_code=VisionErrorCode.VISION_STATUS_FAILED,
                )
            else:
                try:
                    cls.assign_funds_commitment_headers_from_callback(group, normalized_fc_numbers)
                except FundsCommitmentAssignmentError as error:
                    cls.set_status(group, error.status, error_code=error.error_code)
                    fc_assignment_failed = True
                else:
                    # Successful assignment completes release and continues to PG or XLSX delivery.
                    cls.complete_funds_commitment_assignment(group)
        return fc_assignment_failed

    @classmethod
    def complete_funds_commitment_assignment(cls, group: PaymentPlanGroup) -> None:
        from hope.apps.payment.services.payment_plan_group_services import PaymentPlanGroupService

        cls.set_status(group, VisionStatus.FC_ASSOCIATED)
        PaymentPlanGroupService(group).release_from_vision()
        cls.set_status(group, VisionStatus.RELEASED)
        group.save(update_fields=["internal_data"])

    @classmethod
    @transaction.atomic
    def recover_group_with_funds_commitment_headers(
        cls,
        payment_plan_group: PaymentPlanGroup,
        funds_commitment_headers: Iterable[FundsCommitmentHeader],
    ) -> None:
        group = PaymentPlanGroup.objects.select_for_update().get(pk=payment_plan_group.pk)
        if not cls.can_recover_group_with_funds_commitment_headers(group):
            raise FundsCommitmentAssignmentError(
                VisionStatus.CALLBACK_FAILED,
                VisionErrorCode.FC_CONFLICT,
            )
        cls.assign_selected_funds_commitment_headers(group, funds_commitment_headers, replace=False)
        cls.complete_funds_commitment_assignment(group)

    @classmethod
    def can_recover_group_with_funds_commitment_headers(cls, payment_plan_group: PaymentPlanGroup) -> bool:
        group = payment_plan_group
        return (
            group.status == PaymentPlanGroup.Status.IN_REVIEW
            and group.vision_managed
            and group.vision_status in VISION_RECOVERABLE_STATUSES
            and group.payment_plans.exists()
            and not group.payment_plans.exclude(status=PaymentPlan.Status.IN_REVIEW).exists()
        )
