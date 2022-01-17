from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from ..account.models import User
from .models import Formatter, Query
from .widget import CodeWidget


class ExportForm(forms.Form):
    formatter = forms.ModelChoiceField(queryset=Formatter.objects)


class ContentTypeChoiceField(forms.ModelChoiceField):
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
        queryset = ContentType.objects.order_by("model", "app_label")
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
        return f"{obj.name.title()} ({obj.app_label})"


class QueryForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={"style": "width:80%"}))
    target = ContentTypeChoiceField()
    code = forms.CharField(widget=CodeWidget)
    owner = forms.ModelChoiceField(queryset=User.objects, widget=forms.HiddenInput)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2, "style": "width:80%"}))

    class Meta:
        model = Query
        fields = ("name", "target", "description", "code")
