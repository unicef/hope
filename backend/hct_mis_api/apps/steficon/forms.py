from django import forms
from django.core.exceptions import ValidationError

from hct_mis_api.apps.steficon.interpreters import mapping
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.steficon.widget import CodeWidget
import black

mode = black.Mode(
    line_length=80,
    string_normalization=True,
)


class RuleForm(forms.ModelForm):
    definition = forms.CharField(widget=CodeWidget)

    class Meta:
        model = Rule
        exclude = ("updated_by", "created_by")

    def clean(self):
        self._validate_unique = True
        code = self.cleaned_data["definition"]
        language = self.cleaned_data["language"]
        i = mapping[language](code)
        i.validate()
        try:
            code = black.format_file_contents(code, fast=False, mode=mode)
            self.cleaned_data["definition"] = code
        except Exception as e:
            raise ValidationError({"definition": str(e)})
        return self.cleaned_data
