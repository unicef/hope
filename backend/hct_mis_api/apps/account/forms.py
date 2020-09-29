from django import forms

from account.models import Role
from core.models import BusinessArea


class LoadUsersForm(forms.Form):
    emails = forms.CharField(widget=forms.Textarea)
    business_area = forms.ChoiceField(choices=[(ba.id, ba.name) for ba in BusinessArea.objects.all()])
    role = forms.ChoiceField(choices=[(role.id, role.name) for role in Role.objects.all()])