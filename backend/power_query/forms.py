from django import forms
from django.contrib.auth import get_user_model

from .models import Formatter, Query
from .widget import ContentTypeChoiceField, FormatterEditor


class ExportForm(forms.Form):
    formatter = forms.ModelChoiceField(queryset=Formatter.objects)  # type: ignore # Argument "queryset" to "ModelChoiceField" has incompatible type "BaseManager[Any]"; expected "Union[None, Manager[Model], _QuerySet[Model, Model]]"


class FormatterTestForm(forms.Form):
    query = forms.ModelChoiceField(Query.objects)  # type: ignore # Argument 1 to "ModelChoiceField" has incompatible type "BaseManager[Any]"; expected "Union[None, Manager[Model], _QuerySet[Model, Model]]"


class QueryForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={"style": "width:80%"}))
    target = ContentTypeChoiceField()
    code = forms.CharField(widget=FormatterEditor)
    owner = forms.ModelChoiceField(queryset=get_user_model().objects, widget=forms.HiddenInput)  # type: ignore # Argument "queryset" to "ModelChoiceField" has incompatible type "BaseManager[Any]"; expected "Union[None, Manager[Model], _QuerySet[Model, Model]]"
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2, "style": "width:80%"}))

    class Meta:
        model = Query
        fields = ("name", "target", "description", "code")
