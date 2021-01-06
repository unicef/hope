from django.forms import Form, CharField, ChoiceField, Textarea

from account.models import Role
from core.models import BusinessArea


class LoadUsersForm(Form):
    emails = CharField(widget=Textarea)
    business_area = ChoiceField(choices=[(ba.id, ba.name) for ba in BusinessArea.objects.all()])
    role = ChoiceField(choices=[(role.id, role.name) for role in Role.objects.all()])
