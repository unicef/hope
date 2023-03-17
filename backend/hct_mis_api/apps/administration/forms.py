from django import forms


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

