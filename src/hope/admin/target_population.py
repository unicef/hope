from typing import Any

from django.contrib import admin
from django.db.models.fields import Field
from django.forms import TypedChoiceField
from django.http import HttpRequest

from hope.admin.payment_plan import BasePaymentPlanAdmin
from hope.models import PaymentPlan, TargetPopulation

# Fields that only make sense once a plan is a payment plan. `exclude` only drops
# form fields, so they also have to be removed from `readonly_fields` - otherwise
# Django appends them back to the form after the form fields are resolved.
HIDDEN_FIELDS = (
    "follow_up_instruction",
    "use_payment_gateway",
    "background_action_status",
    "dispersion_start_date",
    "dispersion_end_date",
    "total_entitled_quantity",
    "total_entitled_quantity_usd",
    "total_entitled_quantity_revised",
    "total_entitled_quantity_revised_usd",
    "total_delivered_quantity",
    "total_delivered_quantity_usd",
    "total_undelivered_quantity",
    "total_undelivered_quantity_usd",
    "is_cash_assist",
    "imported_file",
    "export_file_entitlement",
    "reconciliation_import_file",
)


@admin.register(TargetPopulation)
class TargetPopulationAdmin(BasePaymentPlanAdmin):
    readonly_fields = tuple(field for field in BasePaymentPlanAdmin.readonly_fields if field not in HIDDEN_FIELDS)
    exclude = HIDDEN_FIELDS + ("plan_type",)

    def formfield_for_choice_field(
        self, db_field: Field, request: HttpRequest, **kwargs: Any
    ) -> TypedChoiceField | None:
        if db_field.name == "status":
            kwargs["choices"] = [(status.value, status.label) for status in PaymentPlan.PRE_PAYMENT_PLAN_STATUSES]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def frontend_url(self, obj: PaymentPlan) -> str:
        return f"/{obj.business_area.slug}/programs/{obj.program.code}/target-population/{obj.id}"
