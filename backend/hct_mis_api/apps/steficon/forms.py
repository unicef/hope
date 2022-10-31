import csv
import json
import logging

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.forms import HiddenInput, Media, Textarea
from django.utils.translation import gettext_lazy as _

from .config import config
from .interpreters import mapping
from .models import Rule
from .widget import ContentTypeChoiceField, PythonEditor

logger = logging.getLogger(__name__)


def format_code(code):
    try:
        import black

        mode = black.Mode(
            line_length=80,
            string_normalization=True,
        )
        return black.format_file_contents(code, fast=False, mode=mode)
    except ImportError as ex:
        if config.USE_BLACK:
            logger.warning(f"Steficon is configured to use Black, but was unable to import it: {ex}")
        return code


delimiters = ",;|:"
quotes = "'\"`"
escapechars = " \\"


class CSVOptionsForm(forms.Form):
    delimiter = forms.ChoiceField(label=_("Delimiter"), choices=list(zip(delimiters, delimiters)), initial=",")
    quotechar = forms.ChoiceField(label=_("Quotechar"), choices=list(zip(quotes, quotes)), initial="'")
    quoting = forms.ChoiceField(
        label=_("Quoting"),
        choices=(
            (csv.QUOTE_ALL, _("All")),
            (csv.QUOTE_MINIMAL, _("Minimal")),
            (csv.QUOTE_NONE, _("None")),
            (csv.QUOTE_NONNUMERIC, _("Non Numeric")),
        ),
        initial=csv.QUOTE_NONE,
    )

    escapechar = forms.ChoiceField(label=_("Escapechar"), choices=(("", ""), ("\\", "\\")), required=False)


class RuleFileProcessForm(CSVOptionsForm, forms.Form):
    file = forms.FileField(label="", required=True)
    results = forms.CharField(
        label="Results columns",
        required=True,
        help_text="Comma separated list od Result attributes " "to add to the produced CSV. ",
    )
    background = forms.BooleanField(label="Run in background", required=False)

    def clean_results(self):
        try:
            return self.cleaned_data["results"].split(",")
        except Exception as e:
            raise ValidationError(e)


class RuleDownloadCSVFileProcessForm(CSVOptionsForm, forms.Form):
    filename = forms.CharField(label="Output filename")
    data = forms.CharField(widget=Textarea({"hidden": ""}))
    fields = forms.CharField(widget=HiddenInput)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for fname in ["delimiter", "quotechar", "quoting", "escapechar"]:
            # TODO: fields is CharField but used as dict?
            self.fields[fname].widget = HiddenInput()  # type: ignore

    def clean_fields(self):
        try:
            return self.cleaned_data["fields"].split(",")
        except Exception as e:
            raise ValidationError(e)

    def clean_data(self):
        try:
            return json.loads(self.cleaned_data["data"])
        except Exception as e:
            raise ValidationError(e)


class TPModelChoiceField(forms.ModelChoiceField):
    def __init__(
        self,
        *,
        empty_label="---------",
        required=True,
        widget=None,
        label=None,
        initial=None,
        help_text="",
        to_field_name=None,
        limit_choices_to=None,
        **kwargs,
    ):
        from hct_mis_api.apps.targeting.models import TargetPopulation

        queryset = TargetPopulation.objects.all()
        super().__init__(
            queryset,
            empty_label=empty_label,
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            to_field_name=to_field_name,
            limit_choices_to=limit_choices_to,
            **kwargs,
        )

    def label_from_instance(self, obj):
        if obj and obj.business_area:
            return f"{obj.name} ({obj.business_area.name})"
        elif obj.name:
            return f"{obj.name}"
        return str(obj)


class RuleTestForm(forms.Form):
    opt = forms.CharField(required=True, widget=HiddenInput)
    file = forms.FileField(label="", required=False)
    raw_data = forms.CharField(label="", widget=Textarea, required=False)
    content_type = ContentTypeChoiceField(required=False)
    content_type_filters = forms.CharField(label="", widget=Textarea, required=False)
    target_population = TPModelChoiceField(required=False)

    @property
    def media(self):
        media = Media()
        for field in self.fields.values():
            media = media + field.widget.media
        return media

    def clean_raw_data(self):
        original = self.cleaned_data["raw_data"]
        if original:
            try:
                return json.loads(original)
            except Exception as e:
                raise ValidationError(e)

    def clean_file(self):
        original = self.cleaned_data["file"]
        if original:
            try:
                return json.loads(original.read())
            except Exception as e:
                raise ValidationError(e)

    def clean(self):
        selection = self.cleaned_data["opt"]
        if selection == "optFile":
            if not self.cleaned_data.get("file"):
                raise ValidationError({"file": "Please select a file to upload"})
        elif selection == "optData" and not self.cleaned_data.get("raw_data"):
            raise ValidationError({"raw_data": "Please provide sample data"})
        elif selection == "optTargetPopulation":
            if not self.cleaned_data.get("target_population"):
                raise ValidationError({"target_population": "Please select a TargetPopulation"})
        elif selection == "optContentType":
            if not self.cleaned_data.get("content_type"):
                raise ValidationError({"content_type": "Please select a Content Type"})
            ct: ContentType = self.cleaned_data["content_type"]
            model = ct.model_class()
            try:
                filters = json.loads(self.cleaned_data.get("content_type_filters") or "{}")
                model.objects.filter(**filters)
            except Exception as e:
                raise ValidationError({"content_type_filters": str(e)})


class RuleForm(forms.ModelForm):
    definition = forms.CharField(widget=PythonEditor)

    class Meta:
        model = Rule
        exclude = ("updated_by", "created_by")

    def clean(self):
        self._validate_unique = True
        code = self.cleaned_data.get("definition", "")
        language = self.cleaned_data["language"]
        i = mapping[language](code)
        try:
            i.validate()
        except Exception as e:
            raise ValidationError({"definition": str(e)})
        if config.USE_BLACK:
            try:
                self.cleaned_data["definition"] = format_code(code)
            except Exception as e:
                raise ValidationError({"definition": str(e)})
        if self.instance.pk:
            pass
        return self.cleaned_data
