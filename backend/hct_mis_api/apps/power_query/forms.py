from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from .models import Query, Formatter
from .widget import CodeWidget
from ..account.models import User


class ExportForm(forms.Form):
    formatter = forms.ModelChoiceField(queryset=Formatter.objects)


class QueryForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'style': "width:80%"}))
    target = forms.ModelChoiceField(ContentType.objects.order_by('app_label', 'model'))
    code = forms.CharField(widget=CodeWidget)
    owner = forms.ModelChoiceField(queryset=User.objects,
                                   widget=forms.HiddenInput)
    description = forms.CharField(required=False,
                                  widget=forms.Textarea(attrs={'rows': 2, 'style': "width:80%"}))

    class Meta:
        model = Query
        fields = ("name", "target", "description", "code")

    def clean(self):
        pass

    def clean_order_by(self):
        try:
            selection = self.cleaned_data.get('order_by')
            if selection:
                field_names = self.cleaned_data.get('order_by', '') or "".split(',')
                return ','.join(field_names)
            else:
                return ""
        except Exception as e:
            raise ValidationError(e)
