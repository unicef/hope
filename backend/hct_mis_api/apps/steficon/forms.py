import logging

from django import forms
from django.core.exceptions import ValidationError

from hct_mis_api.apps.steficon.interpreters import mapping
from hct_mis_api.apps.steficon.models import Rule
from hct_mis_api.apps.steficon.widget import CodeWidget
from hct_mis_api.apps.steficon.config import config

logger = logging.getLogger(__name__)
try:
    import black

    mode = black.Mode(
        line_length=80,
        string_normalization=True,
    )

    def format_code(code):
        return black.format_file_contents(code, fast=False, mode=mode)


except ImportError as e:
    if config.USE_BLACK:
        logger.warning(f"Steficon is configured to use Black, but was unable to import it: {e}")

    def format_code(code):
        return code


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
        if config.USE_BLACK:
            try:
                self.cleaned_data["definition"] = format_code(code)
            except Exception as e:
                logger.exception(e)
                raise ValidationError({"definition": str(e)})
        return self.cleaned_data
