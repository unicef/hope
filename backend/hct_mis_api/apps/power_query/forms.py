from django import forms

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.power_query.models import Formatter, Query
from hct_mis_api.apps.steficon.widget import ContentTypeChoiceField, PythonEditor


class ExportForm(forms.Form):
    formatter = forms.ModelChoiceField(queryset=Formatter.objects)  # type: ignore # Argument "queryset" to "ModelChoiceField" has incompatible type "BaseManager[Any]"; expected "Union[None, Manager[Model], _QuerySet[Model, Model]]"


class FormatterTestForm(forms.Form):
    query = forms.ModelChoiceField(Query.objects)  # type: ignore # Argument 1 to "ModelChoiceField" has incompatible type "BaseManager[Any]"; expected "Union[None, Manager[Model], _QuerySet[Model, Model]]"


class QueryForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={"style": "width:80%"}))
    target = ContentTypeChoiceField()
    code = forms.CharField(widget=PythonEditor)
    owner = forms.ModelChoiceField(queryset=User.objects, widget=forms.HiddenInput)  # type: ignore # Argument "queryset" to "ModelChoiceField" has incompatible type "BaseManager[Any]"; expected "Union[None, Manager[Model], _QuerySet[Model, Model]]"
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2, "style": "width:80%"}))

    class Meta:
        model = Query
        fields = ("name", "target", "description", "code")
