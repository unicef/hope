from django import forms
from django.core.exceptions import ValidationError

from steficon.interpreters import mapping
from steficon.models import Rule


class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        exclude = ()

    def clean(self):
        code = self.cleaned_data['definition']
        language = self.cleaned_data['language']
        i = mapping[language](code)
        i.validate()
        return self.cleaned_data
