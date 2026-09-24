from django.db import transaction
from rest_framework.exceptions import ValidationError

from hope.apps.payment.flows import PaymentPlanGroupFlow
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.models import FspXlsxTemplatePerDeliveryMechanism, PaymentPlan, PaymentPlanGroup


class PaymentPlanGroupService:
    def __init__(self, payment_plan_group: PaymentPlanGroup) -> None:
        self.payment_plan_group = payment_plan_group

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
        self._validate_shared_configuration(payment_plans)
        self._validate_delivery_templates(payment_plans)

        for payment_plan in payment_plans:
            PaymentPlanService(payment_plan).lock_fsp()

        flow = PaymentPlanGroupFlow(payment_plan_group)
        flow.status_lock()
        payment_plan_group.save(update_fields=("status", "status_date", "updated_at"))

        self.payment_plan_group = payment_plan_group
        return payment_plan_group

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
                "currency", "delivery_mechanism", "financial_service_provider"
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
    def _validate_shared_configuration(payment_plans: list[PaymentPlan]) -> None:
        fsp_ids = {payment_plan.financial_service_provider_id for payment_plan in payment_plans}
        currency_ids = {payment_plan.currency_id for payment_plan in payment_plans}
        if None in fsp_ids or len(fsp_ids) != 1:
            raise ValidationError("Payment Plans in the group must share the same Financial Service Provider.")
        if None in currency_ids or len(currency_ids) != 1:
            raise ValidationError("Payment Plans in the group must share the same Currency.")

    @staticmethod
    def _validate_delivery_templates(payment_plans: list[PaymentPlan]) -> None:
        """Reject up front what the group export would otherwise drop with only a warning."""
        # Delivery mechanisms may differ across the group, the FSP may not, so one query covers every plan.
        mapped_delivery_mechanism_ids = set(
            FspXlsxTemplatePerDeliveryMechanism.objects.filter(
                financial_service_provider_id=payment_plans[0].financial_service_provider_id,
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
