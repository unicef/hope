from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminSplitDateTime

from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.program.models import CashPlan


class ImportPaymentRecordsForm(forms.ModelForm):
    currency = forms.ChoiceField(choices=(("UAH", "Hryvnia"),))
    delivery_type = forms.ChoiceField(choices=PaymentRecord.DELIVERY_TYPE_CHOICE)
    reconciliation_file = forms.FileField()
    start_date = forms.SplitDateTimeField(widget=AdminSplitDateTime)
    end_date = forms.SplitDateTimeField(widget=AdminSplitDateTime)
    dispersion_date = forms.SplitDateTimeField(widget=AdminSplitDateTime)
    status_date = forms.SplitDateTimeField(widget=AdminSplitDateTime)

    class Meta:
        model = CashPlan
        exclude = (
            "business_area",
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
        )
