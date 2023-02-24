from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.contrib.postgres.forms import DecimalRangeField
from django.templatetags.static import static

from hct_mis_api.apps.payment.models import (
    AcceptanceProcessThreshold,
    CashPlan,
    PaymentRecord,
)


class ImportPaymentRecordsForm(forms.ModelForm):
    currency = forms.ChoiceField(choices=(("UAH", "Hryvnia"),))
    delivery_type = forms.ChoiceField(choices=PaymentRecord.DELIVERY_TYPE_CHOICE)
    reconciliation_file = forms.FileField()
    start_date = forms.SplitDateTimeField(widget=AdminSplitDateTime)
    end_date = forms.SplitDateTimeField(widget=AdminSplitDateTime)
    dispersion_date = forms.SplitDateTimeField(widget=AdminSplitDateTime)
    delivery_date = forms.SplitDateTimeField(widget=AdminSplitDateTime)
    status_date = forms.SplitDateTimeField(widget=AdminSplitDateTime)

    class Meta:
        model = CashPlan
        exclude = (
            "ca_id",
            "ca_hash_id",
            "id",
            "total_persons_covered",
            "total_entitled_quantity",
            "total_entitled_quantity_revised",
            "total_persons_covered_revised",
            "total_delivered_quantity",
            "total_undelivered_quantity",
            "exchange_rate",
            "session",
        )

    class Media:
        js = (static("admin/js/core.js"),)


class AcceptanceProcessThresholdForm(forms.ModelForm):
    payments_range_usd = DecimalRangeField(
        fields=[
            forms.IntegerField(required=True),
            forms.IntegerField(required=False),
        ],
    )

    class Meta:
        model = AcceptanceProcessThreshold
        fields = [
            "payments_range_usd",
            "approval_number_required",
            "authorization_number_required",
            "finance_release_number_required",
        ]
