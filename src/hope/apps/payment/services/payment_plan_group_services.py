from django.db import transaction
from rest_framework.exceptions import ValidationError

from hope.apps.payment.flows import PaymentPlanGroupFlow
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.models import (
    Currency,
    DeliveryMechanism,
    FinancialServiceProvider,
    FspXlsxTemplatePerDeliveryMechanism,
    PaymentPlan,
    PaymentPlanGroup,
)


class PaymentPlanGroupService:
    def __init__(self, payment_plan_group: PaymentPlanGroup) -> None:
        self.payment_plan_group = payment_plan_group

    def assign_financial_service_provider(self, financial_service_provider: FinancialServiceProvider | None) -> None:
        """Set the group's FSP, copy it onto its Target Populations and rebuild them; the caller saves the group.

        Payments carry the FSP and the wallet validity from the build, so a change is only possible while
        every Target Population can still be rebuilt, i.e. is TP_OPEN.
        """
        if financial_service_provider == self.payment_plan_group.financial_service_provider:
            return
        payment_plans = list(self.payment_plan_group.payment_plans.all())
        if any(payment_plan.status != PaymentPlan.Status.TP_OPEN for payment_plan in payment_plans):
            raise ValidationError(
                "Financial Service Provider can be changed only while every Target Population in the group is Open."
            )
        self.payment_plan_group.financial_service_provider = financial_service_provider
        self.payment_plan_group.payment_plans.update(financial_service_provider=financial_service_provider)
        for payment_plan in payment_plans:
            payment_plan.financial_service_provider = financial_service_provider
            transaction.on_commit(
                lambda payment_plan=payment_plan: PaymentPlanService.rebuild_payment_plan_population(
                    True, False, False, payment_plan
                )
            )

    def assign_currency(self, currency: Currency | None) -> None:
        """Set the group's currency; the caller saves the group. Payment Plans copy it when they are opened."""
        if currency == self.payment_plan_group.currency:
            return
        if self.payment_plan_group.payment_plans.exclude(status__in=PaymentPlan.PRE_PAYMENT_PLAN_STATUSES).exists():
            raise ValidationError("Currency can be changed only before any Payment Plan in the group is opened.")
        if currency is not None:
            self._validate_currency_against_delivery_mechanisms(currency)
        self.payment_plan_group.currency = currency

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
        # lock_fsp() / unlock_fsp() read both objects per plan
        return list(
            payment_plan_group.payment_plans.select_related(
                "delivery_mechanism", "financial_service_provider"
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
