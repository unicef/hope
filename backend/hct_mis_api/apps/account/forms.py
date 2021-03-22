import logging

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms import Form, CharField, Textarea, ModelChoiceField

from hct_mis_api.apps.account.models import Role
from hct_mis_api.apps.core.models import BusinessArea

logger = logging.getLogger(__name__)


class LoadUsersForm(Form):
    emails = CharField(widget=Textarea)
    business_area = ModelChoiceField(queryset=BusinessArea.objects.all())
    role = ModelChoiceField(queryset=Role.objects.all())

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
