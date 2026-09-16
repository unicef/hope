from django.contrib import admin

from hope.admin.payment_plan import BasePaymentPlanAdmin
from hope.models import TargetPopulation


@admin.register(TargetPopulation)
class TargetPopulationAdmin(BasePaymentPlanAdmin):
    exclude = (
        "plan_type",
        "follow_up_instruction",
        "use_payment_gateway",
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
    )

    def frontend_url(self, obj: TargetPopulation) -> str:
        return f"/{obj.business_area.slug}/programs/{obj.program.code}/target-population/{obj.id}"
