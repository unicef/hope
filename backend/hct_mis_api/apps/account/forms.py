import logging

from django import forms  # Form, CharField, Textarea, ModelChoiceField, PasswordInput
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from hct_mis_api.apps.account.models import Role
from hct_mis_api.apps.core.models import BusinessArea

logger = logging.getLogger(__name__)


class KoboLoginForm(forms.Form):
    kobo_username = forms.CharField()
    kobo_password = forms.CharField(widget=forms.PasswordInput)


class KoboImportUsersForm(forms.Form):
    emails = forms.CharField(required=False, widget=forms.Textarea)

    def clean_emails(self):
        errors = []
        for e in self.cleaned_data["emails"].split():
            try:
                validate_email(e)
            except ValidationError:
                errors.append(e)
        if errors:
            logger.error("Invalid emails %s" % ", ".join(errors))
            raise ValidationError("Invalid emails %s" % ", ".join(errors))
        return self.cleaned_data["emails"]


class LoadUsersForm(forms.Form):
    emails = forms.CharField(widget=forms.Textarea)
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all())
    role = forms.ModelChoiceField(queryset=Role.objects.all())

    def clean_emails(self):
        errors = []
        for e in self.cleaned_data["emails"].split():
            try:
                validate_email(e)
            except ValidationError:
                errors.append(e)
        if errors:
            logger.error("Invalid emails %s" % ", ".join(errors))
            raise ValidationError("Invalid emails %s" % ", ".join(errors))
        return self.cleaned_data["emails"]
