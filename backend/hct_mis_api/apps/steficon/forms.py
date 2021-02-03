from django import forms
from hct_mis_api.apps.steficon.interpreters import mapping
from hct_mis_api.apps.steficon.models import Rule
from steficon.widget import CodeWidget


class RuleForm(forms.ModelForm):
    definition = forms.CharField(widget=CodeWidget)

    class Meta:
        model = Rule
        exclude = ('updated_by',)

    def clean(self):
        code = self.cleaned_data['definition']
        language = self.cleaned_data['language']
        i = mapping[language](code)
        i.validate()
        return self.cleaned_data
