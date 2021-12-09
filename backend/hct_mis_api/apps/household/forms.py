from typing import Optional

from django import forms
from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import XlsxUpdateFile
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class UpdateByXlsxStage1Form(forms.Form):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all())
    registration_data_import = forms.CharField(required=False)
    file = forms.FileField()

    def clean_registration_data_import(self) -> Optional[RegistrationDataImport]:
        data = self.cleaned_data.get("registration_data_import")

        if not data:
            return None

        registration_data_import = self._retrieve_rdi_by_name()

        self._change_rdi_has_correct_business_area(registration_data_import)

        return registration_data_import

    def _change_rdi_has_correct_business_area(self, registration_data_import) -> None:
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

    def __init__(self, *args, **kwargs):
        xlsx_columns = kwargs.pop("xlsx_columns", [])
        super(UpdateByXlsxStage2Form, self).__init__(*args, **kwargs)
        self.fields["xlsx_match_columns"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple, choices=[(xlsx_column, xlsx_column) for xlsx_column in xlsx_columns]
        )
