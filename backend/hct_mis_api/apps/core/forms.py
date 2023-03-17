from typing import Any, Dict, Optional

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.models import Program


class StorageFileForm(forms.Form):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.fields["business_area"] = forms.ModelChoiceField(queryset=self.get_business_area_queryset())

        self.fields["file"] = forms.FileField(label="Select a file")

    def get_business_area_queryset(self) -> QuerySet[BusinessArea]:
        return BusinessArea.objects.filter(id__in=self.user.user_roles.all().values_list("business_area_id", flat=True))

    def clean(self, *args: Any, **kwargs: Any) -> Optional[Dict[str, Any]]:
        cleaned_data = super().clean()
        limit = settings.MAX_STORAGE_FILE_SIZE * 1024 * 1024
        if self.cleaned_data["file"].size > limit:
            raise ValidationError(f"File too large. Size should not exceed {limit} MiB.")
        return cleaned_data


class ProgramForm(forms.Form):
    name = forms.CharField(max_length=255, label="Target population name")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.business_area_id = kwargs.pop("business_area_id")
        super().__init__(*args, **kwargs)

        self.fields["program"] = forms.ModelChoiceField(queryset=self.get_program_queryset())

    def get_program_queryset(self) -> QuerySet[Program]:
        return Program.objects.filter(Q(business_area_id=self.business_area_id) & Q(status=Program.ACTIVE))


class ClearCacheForm(forms.Form):
    # Report
    resolve_dashboard_years_choices = forms.BooleanField(label="Report: dashboard_years_choices", required=False)
    # Grievance
    resolve_chart_grievances = forms.BooleanField(label="Grievance: chart_grievances", required=False)
    # Program
    resolve_chart_programmes_by_sector = forms.BooleanField(label="Program: chart_programmes_by_sector", required=False)
    resolve_chart_total_transferred_by_month = forms.BooleanField(
        label="Program: chart_total_transferred_by_month", required=False
    )
    # Household
    resolve_section_households_reached = forms.BooleanField(
        label="Household: section_households_reached", required=False
    )
    resolve_section_individuals_reached = forms.BooleanField(
        label="Household: section_individuals_reached", required=False
    )
    resolve_section_child_reached = forms.BooleanField(label="Household: section_child_reached", required=False)
    resolve_chart_individuals_reached_by_age_and_gender = forms.BooleanField(
        label="Household: chart_individuals_reached_by_age_and_gender", required=False
    )
    resolve_chart_individuals_with_disability_reached_by_age = forms.BooleanField(
        label="Household: chart_individuals_with_disability_reached_by_age", required=False
    )
    # Payment
    exchange_rates = forms.BooleanField(label="Payment: exchange rates", required=False)
    resolve_chart_volume_by_delivery_mechanism = forms.BooleanField(
        label="Payment: chart_volume_by_delivery_mechanism", required=False
    )
    resolve_chart_payment_verification = forms.BooleanField(label="Payment: chart_payment_verification", required=False)
    resolve_chart_payment = forms.BooleanField(label="Payment: chart_payment", required=False)
    resolve_section_total_transferred = forms.BooleanField(label="Payment: section_total_transferred", required=False)
    resolve_table_total_cash_transferred_by_administrative_area = forms.BooleanField(
        label="Payment: table_total_cash_transferred_by_administrative_area", required=False
    )
    resolve_chart_total_transferred_cash_by_country = forms.BooleanField(
        label="Payment: chart_total_transferred_cash_by_country", required=False
    )
