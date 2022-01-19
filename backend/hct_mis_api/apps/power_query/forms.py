from django import forms

from ..account.models import User
from ..steficon.widget import ContentTypeChoiceField, PythonEditor
from .models import Formatter, Query


class ExportForm(forms.Form):
    formatter = forms.ModelChoiceField(queryset=Formatter.objects)


class FormatterTestForm(forms.Form):
    query = forms.ModelChoiceField(Query.objects)


class QueryForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={"style": "width:80%"}))
    target = ContentTypeChoiceField()
    code = forms.CharField(widget=PythonEditor)
    owner = forms.ModelChoiceField(queryset=User.objects, widget=forms.HiddenInput)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2, "style": "width:80%"}))

    class Meta:
        model = Query
        fields = ("name", "target", "description", "code")
