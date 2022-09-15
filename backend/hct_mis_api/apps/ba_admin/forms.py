from django import forms

from hct_mis_api.apps.ba_admin.utils import ba_for_user
from hct_mis_api.apps.core.models import BusinessArea


class SelectBusinessAreaForm(forms.Form):
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.none())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["business_area"].queryset = ba_for_user(self.user)
