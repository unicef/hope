from django import forms

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import XlsxUpdateFile
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class UpdateByXlsxStage1Form(forms.Form):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all())
    registration_data_import = forms.ModelChoiceField(queryset=RegistrationDataImport.objects.all(), required=False)
    file = forms.FileField()


class UpdateByXlsxStage2Form(forms.Form):
    xlsx_update_file = forms.ModelChoiceField(queryset=XlsxUpdateFile.objects.all(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        xlsx_columns = kwargs.pop("xlsx_columns", [])
        super(UpdateByXlsxStage2Form, self).__init__(*args, **kwargs)
        self.fields["xlsx_match_columns"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple, choices=[(xlsx_column, xlsx_column) for xlsx_column in xlsx_columns]
        )
