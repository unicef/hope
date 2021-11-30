from django import forms

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class UpdateByXlsxStage1Form(forms.Form):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all(), required=True)
    registration_data_import = forms.ModelChoiceField(queryset=RegistrationDataImport.objects.all())
    file = forms.FileField()


class UpdateByXlsxStage2Form(forms.Form):
    def __init__(self, xlsx_columns, *args, **kwargs):
        super(UpdateByXlsxStage2Form, self).__init__(*args, **kwargs)
        self.fields["match_columns"] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple, choices=[(xlsx_column, xlsx_column) for xlsx_column in xlsx_columns]
        )
