from operator import itemgetter

from django import forms
from django.contrib import admin, messages
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils import timezone
from django.utils.safestring import mark_safe

from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin, _confirm_action
from adminfilters.filters import TextFieldFilter

from hct_mis_api.apps.core.currencies import CURRENCY_CHOICES
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.erp_datahub.models import DownPayment, FundsCommitment
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


class NumberValidator(RegexValidator):
    regex = r"[0-9]{10,}"


class FundsCommitmentAddForm(forms.ModelForm):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects, to_field_name="code")
    currency_code = forms.ChoiceField(choices=sorted(CURRENCY_CHOICES[1:], key=itemgetter(1)))
    funds_commitment_number = forms.CharField(required=True)
    vendor_id = forms.CharField(validators=[NumberValidator, MinLengthValidator(10)])
    gl_account = forms.CharField(validators=[NumberValidator, MinLengthValidator(10)])
    new_business_area_code = forms.ModelChoiceField(
        queryset=BusinessArea.objects.filter(is_split=False), to_field_name="code"
    )

    class Meta:
        model = FundsCommitment
        exclude = ("update_date", "updated_by", "mis_sync_flag", "mis_sync_date", "ca_sync_date", "ca_sync_flag")

    def clean_business_area(self):
        return self.cleaned_data["business_area"].code

    def clean_new_business_area_code(self):
        return self.cleaned_data["business_area"].code


class DownPaymentAddForm(forms.ModelForm):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects, to_field_name="code")
    new_business_area_code = forms.ModelChoiceField(
        queryset=BusinessArea.objects.filter(is_split=False), to_field_name="code"
    )

    class Meta:
        model = DownPayment
        exclude = ("update_date", "updated_by", "mis_sync_flag", "mis_sync_date", "ca_sync_date", "ca_sync_flag")

    def clean_business_area(self):
        return self.cleaned_data["business_area"].code

    def clean_new_business_area_code(self):
        return self.cleaned_data["business_area"].code


@admin.register(FundsCommitment)
class FundsCommitmentAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_display = ("rec_serial_number", "business_area", "funds_commitment_number", "posting_date")
    list_filter = (
        "mis_sync_date",
        "ca_sync_date",
        TextFieldFilter.factory("business_area"),
    )
    date_hierarchy = "create_date"
    add_form = FundsCommitmentAddForm

    @button()
    def execute_exchange_rate_sync(self, request):
        if request.method == "POST":
            from hct_mis_api.apps.erp_datahub.tasks.pull_from_erp_datahub import PullFromErpDatahubTask

            task = PullFromErpDatahubTask()
            task.execute()
            self.message_user(request, "Exchange rate synced", messages.SUCCESS)
        else:
            return _confirm_action(
                self,
                request,
                self.execute_exchange_rate_sync,
                mark_safe(
                    """<h1>DO NOT CONTINUE IF YOU ARE NOT SURE WHAT YOU ARE DOING</h1>                
                        <h3>Import will only be simulated</h3> 
                        """
                ),
                "Successfully executed",
                template="admin_extra_urls/confirm.html",
            )

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial["created_by"] = request.user.email
        initial["updated_by"] = request.user.email
        initial["posting_date"] = timezone.now()
        initial["status_date"] = timezone.now()
        return initial

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not change:
            return FundsCommitmentAddForm
        return super().get_form(request, obj, change, **kwargs)


@admin.register(DownPayment)
class DownPaymentAdmin(HOPEModelAdminBase):
    list_filter = (
        "mis_sync_date",
        "ca_sync_date",
        TextFieldFilter.factory("business_area"),
    )
    add_form = DownPaymentAddForm
    date_hierarchy = "create_date"
