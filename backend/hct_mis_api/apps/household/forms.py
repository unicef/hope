import re
from typing import Any, Dict, List, Optional

from django import forms
from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from django.utils.translation import gettext_lazy as _

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import Household, XlsxUpdateFile
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.targeting.models import TargetingCriteria, TargetPopulation


def get_households_from_text(ba: BusinessArea, text: Any, target_field: Any) -> Optional[List]:
    """
    Given a text and a BA, find all the Households ID in the text and return the valid IDs in that business area
    """
    if target_field == "unicef_id":
        return Household.objects.filter(
            withdrawn=False, business_area=ba, unicef_id__in=re.findall(r"HH-\d{2}-\d{4}.\d{4}", text)
        )
    elif target_field == "unique_id":
        return Household.objects.filter(
            withdrawn=False,
            business_area=ba,
            id__in=re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", text),
        )
    return []


class UpdateByXlsxStage1Form(forms.Form):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all())
    registration_data_import = forms.ModelChoiceField(queryset=RegistrationDataImport.objects.all())
    file = forms.FileField()

    def clean_registration_data_import(self) -> Optional[RegistrationDataImport]:
        data = self.cleaned_data.get("registration_data_import")

        if not data:
            return None

        registration_data_import = self._retrieve_rdi_by_name()

        self._check_rdi_has_correct_business_area(registration_data_import)

        return registration_data_import

    def _check_rdi_has_correct_business_area(self, registration_data_import: RegistrationDataImport) -> None:
        business_area = self.cleaned_data.get("business_area")
        if registration_data_import.business_area != business_area:
            raise ValidationError("Rdi should belong to selected business area")

    def _retrieve_rdi_by_name(self) -> RegistrationDataImport:
        data = self.cleaned_data.get("registration_data_import")
        registration_data_import = RegistrationDataImport.objects.filter(name=data).first()
        if not registration_data_import:
            raise ValidationError(f"Rdi with the name {data} doesn't exist")
        return registration_data_import


class UpdateByXlsxStage2Form(forms.Form):
    xlsx_update_file = forms.ModelChoiceField(queryset=XlsxUpdateFile.objects.all(), widget=forms.HiddenInput())

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.xlsx_columns = kwargs.pop("xlsx_columns", [])
        super().__init__(*args, **kwargs)
        self.fields["xlsx_match_columns"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            choices=[(xlsx_column, xlsx_column) for xlsx_column in self.xlsx_columns],
        )

    def clean_xlsx_match_columns(self) -> Dict:
        data = self.cleaned_data["xlsx_match_columns"]
        required_columns = {"individual__unicef_id", "household__unicef_id"}
        all_columns = set(self.xlsx_columns)
        required_columns_in_this_form = all_columns & required_columns
        columns_not_found = required_columns_in_this_form - set(data)
        if not len(columns_not_found):
            return data
        raise ValidationError("Unicef Id columns have to be selected")


class UpdateIndividualsIBANFromXlsxForm(forms.Form):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all())
    file = forms.FileField()


class WithdrawForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    reason = forms.CharField(label="Log message", max_length=100, required=False)
    tag = forms.SlugField(
        max_length=100,
        required=False,
        help_text="HH will have a user_field with this name with value 'True'",
    )


class RestoreForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    reason = forms.CharField(label="Log message", max_length=100, required=False)
    reopen_tickets = forms.BooleanField(required=False, help_text="Restore all previously closed tickets")


class MassWithdrawForm(WithdrawForm):
    pass


class AddToTargetPopulationForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    action = forms.CharField(widget=forms.HiddenInput)
    target_population = forms.ModelChoiceField(
        queryset=TargetPopulation.objects.filter(status=TargetPopulation.STATUS_OPEN)
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        read_only = kwargs.pop("read_only", False)
        super().__init__(*args, **kwargs)
        if read_only:
            self.fields["target_population"].widget = HiddenInput()


class CreateTargetPopulationForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    action = forms.CharField(widget=forms.HiddenInput)
    name = forms.CharField()
    program = forms.ModelChoiceField(queryset=Program.objects.filter(status=Program.ACTIVE))

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        read_only = kwargs.pop("read_only", False)
        super().__init__(*args, **kwargs)
        if "initial" in kwargs:
            first = Household.objects.get(pk=kwargs["initial"]["_selected_action"][0])
            self.fields["program"].queryset = Program.objects.filter(
                status=Program.ACTIVE, business_area=first.business_area
            )

        if read_only:
            self.fields["program"].widget = HiddenInput()
            self.fields["name"].widget = HiddenInput()


class CreateTargetPopulationTextForm(forms.Form):
    name = forms.CharField()
    business_area = forms.ModelChoiceField(
        queryset=BusinessArea.objects.all(), help_text=_("Chose the correct business area")
    )
    target_field = forms.ChoiceField(choices=(("unique_id", _("UUID")), ("unicef_id", _("Unicef ID"))))
    action = forms.CharField(widget=forms.HiddenInput)
    criteria = forms.CharField(widget=forms.Textarea)
    targeting_criteria = forms.ModelChoiceField(widget=forms.HiddenInput, queryset=TargetingCriteria.objects.all())

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        read_only = kwargs.pop("read_only", False)
        super().__init__(*args, **kwargs)
        if "initial" in kwargs:
            self.fields["business_area"].queryset = BusinessArea.objects.all()

        if read_only:
            self.fields["business_area"].widget = HiddenInput()
            self.fields["name"].widget = HiddenInput()
            self.fields["criteria"].widget = HiddenInput()
            self.fields["targeting_criteria"].widget = HiddenInput()
            self.fields["target_field"].widget = HiddenInput()

    def clean_criteria(self) -> Optional[List]:
        try:
            return get_households_from_text(
                self.cleaned_data["business_area"], self.cleaned_data["criteria"], self.cleaned_data["target_field"]
            )
        except Exception as e:
            raise ValidationError(str(e))
