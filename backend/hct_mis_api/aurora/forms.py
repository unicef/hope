from typing import Any, Dict, Optional

from django import forms
from django.core.exceptions import ValidationError

from hct_mis_api.aurora.models import Registration


class ProjectForm(forms.ModelForm):
    pass


class FetchForm(forms.Form):
    registration = forms.ModelChoiceField(required=False, queryset=Registration.objects.all().order_by("name"))
    from_id = forms.IntegerField(required=False)
    after_date = forms.DateField(required=False)
    overwrite = forms.BooleanField(required=False)

    def clean(self) -> Optional[Dict[str, Any]]:
        if not (self.cleaned_data.get("from_id") or self.cleaned_data.get("after_date")):
            raise ValidationError("Set 'id' or 'data' ")
        return self.cleaned_data
