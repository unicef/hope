from django import forms

from hct_mis_api.apps.program.models import CashPlan


class CashPlanForm(forms.ModelForm):
    class Meta:
        model = CashPlan
        fields = (
            "status",
            "status_date",
            "name",
            "distribution_level",
            "start_date",
            "end_date",
            "dispersion_date",
            "coverage_duration",
            "coverage_unit",
            "comments",
            "program",
            "delivery_type",
            "assistance_measurement",
            "assistance_through",
            "service_provider",
            "vision_id",
            "funds_commitment",
            "down_payment",
            "validation_alerts_count",
        )
