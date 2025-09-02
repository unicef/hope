import csv
import json
import logging
from typing import TYPE_CHECKING, Any, Union

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import HiddenInput, Media, Textarea
from django.utils.translation import gettext_lazy as _

from hope.apps.steficon.config import config
from hope.apps.steficon.interpreters import Interpreter, mapping
from hope.apps.steficon.widget import ContentTypeChoiceField, PythonFormatterEditor
from hope.models.payment_plan import PaymentPlan
from hope.models.rule import Rule, RuleCommit

if TYPE_CHECKING:
    from django.contrib.contenttypes.models import ContentType

    if TYPE_CHECKING:
        from django.db.models.fields import _ChoicesCallable

logger = logging.getLogger(__name__)


def format_code(code: str) -> str:
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
    delimiter = forms.ChoiceField(
        label=_("Delimiter"),
        choices=list(zip(delimiters, delimiters, strict=True)),
        initial=",",
    )
    quotechar = forms.ChoiceField(
        label=_("Quotechar"),
        choices=list(zip(quotes, quotes, strict=True)),
        initial="'",
    )
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
        help_text="Comma separated list od Result attributes to add to the produced CSV. ",
    )
    background = forms.BooleanField(label="Run in background", required=False)

    def clean_results(self) -> dict:
        try:
            return self.cleaned_data["results"].split(",")
        except Exception as e:
            raise ValidationError(str(e))


class RuleDownloadCSVFileProcessForm(CSVOptionsForm, forms.Form):
    filename = forms.CharField(label="Output filename")
    data = forms.CharField(widget=Textarea({"hidden": ""}))  # type: ignore # FIXME: 'data' is an internal field
    fields = forms.CharField(widget=HiddenInput)  # type: ignore # FIXME: 'fields' is an internal field

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for fname in ["delimiter", "quotechar", "quoting", "escapechar"]:
            self.fields[fname].widget = HiddenInput()  # type: ignore # FIXME

    def clean_fields(self) -> list | None:
        try:
            return self.cleaned_data["fields"].split(",")
        except Exception as e:
            raise ValidationError(str(e))

    def clean_data(self) -> dict | None:
        try:
            return json.loads(self.cleaned_data["data"])
        except Exception as e:
            raise ValidationError(str(e))


class TPModelChoiceField(forms.ModelChoiceField):
    def __init__(
        self,
        *,
        empty_label: str = "---------",
        required: bool = True,
        widget: Any | None = None,
        label: Any | None = None,
        initial: Any | None = None,
        help_text: str = "",
        to_field_name: str | None = None,
        limit_choices_to: Union[Q | dict[str, Any], "_ChoicesCallable", None] = None,
        **kwargs: Any,
    ) -> None:
        queryset = PaymentPlan.objects.all()
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

    def label_from_instance(self, obj: Any) -> str:
        if obj and obj.business_area:
            return f"{obj.name} ({obj.business_area.name})"
        if obj.name:
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
    def media(self) -> Media:
        media = Media()
        for field in self.fields.values():
            media = media + field.widget.media
        return media

    def clean_raw_data(self) -> dict | None:
        original = self.cleaned_data["raw_data"]
        if original:
            try:
                return json.loads(original)
            except Exception as e:
                raise ValidationError(str(e))
        return None

    def clean_file(self) -> dict | None:
        original = self.cleaned_data["file"]
        if original:
            try:
                return json.loads(original.read())
            except Exception as e:
                raise ValidationError(str(e))
        return None

    def clean(self) -> None:
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
    definition = forms.CharField(widget=PythonFormatterEditor)

    class Meta:
        model = Rule
        fields = (
            "name",
            "definition",
            "description",
            "enabled",
            "deprecated",
            "language",
            "security",
            "type",
            "flags",
            "allowed_business_areas",
        )

    def clean(self) -> dict | None:
        if len(self.cleaned_data) == 1 and "allowed_business_areas" in self.cleaned_data:
            # added that just for update 'allowed_business_areas'
            return self.cleaned_data
        self._validate_unique = True
        code = self.cleaned_data.get("definition", "")
        language = self.cleaned_data["language"]
        interpreter: type[Interpreter] = mapping[language]
        i: Interpreter = interpreter(code)
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


class RuleCommitAdminForm(forms.ModelForm):
    definition = forms.CharField(widget=PythonFormatterEditor)

    class Meta:
        model = RuleCommit
        fields = (
            "rule",
            "definition",
            "is_release",
            "enabled",
            "deprecated",
            "language",
            "affected_fields",
        )
