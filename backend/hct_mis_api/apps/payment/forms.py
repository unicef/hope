from typing import Any, Dict, Optional

from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.contrib.postgres.forms import DecimalRangeField
from django.templatetags.static import static

from hct_mis_api.apps.payment.models import (
    AcceptanceProcessThreshold,
    CashPlan,
    DeliveryMechanismPerPaymentPlan,
    GenericPayment,
    PaymentRecord,
)
from hct_mis_api.apps.utils.phone import is_valid_phone_number


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


class DeliveryMechanismPerPaymentPlanForm(forms.ModelForm):
    class Meta:
        model = DeliveryMechanismPerPaymentPlan
        fields = "__all__"

    def clean(self) -> Optional[Dict[str, Any]]:
        cleaned_data = self.cleaned_data

        if cleaned_data["delivery_mechanism"] == GenericPayment.DELIVERY_TYPE_DEPOSIT_TO_CARD:
            if cleaned_data["card_number"] is None:
                self.add_error("card_number", "This field is required.")
            else:
                # if someone changes delivery mechanism type, clear other special fields
                cleaned_data["phone_no"] = None
                cleaned_data["bank_name"] = None
                cleaned_data["bank_account_number"] = None
        elif cleaned_data["delivery_mechanism"] == GenericPayment.DELIVERY_TYPE_MOBILE_MONEY:
            if cleaned_data.get("phone_no") is None or not is_valid_phone_number(cleaned_data.get("phone_no")):
                self.add_error("phone_no", "Phone number is empty or not valid.")
            else:
                cleaned_data["card_number"] = None
                cleaned_data["bank_name"] = None
                cleaned_data["bank_account_number"] = None
        elif cleaned_data["delivery_mechanism"] == GenericPayment.DELIVERY_TYPE_TRANSFER_TO_ACCOUNT:
            if cleaned_data["bank_name"] is None:
                self.add_error("bank_name", "This field is required.")
            if cleaned_data["bank_account_number"] is None:
                self.add_error("bank_account_number", "This field is required.")
            else:
                cleaned_data["card_number"] = None
                cleaned_data["phone_no"] = None
        else:
            # clean all special fields
            cleaned_data["card_number"] = None
            cleaned_data["phone_no"] = None
            cleaned_data["bank_name"] = None
            cleaned_data["bank_account_number"] = None

        return cleaned_data
