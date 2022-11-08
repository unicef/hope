import csv
import logging
from typing import Dict

from django import forms  # Form, CharField, Textarea, ModelChoiceField, PasswordInput
from django.contrib.admin import widgets
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext as _

from adminactions.api import delimiters, quotes

from hct_mis_api.apps.account.models import Partner, Role
from hct_mis_api.apps.core.models import BusinessArea

logger = logging.getLogger(__name__)


class KoboLoginForm(forms.Form):
    kobo_username = forms.CharField()
    kobo_password = forms.CharField(widget=forms.PasswordInput)


class KoboImportUsersForm(forms.Form):
    emails = forms.CharField(required=False, widget=forms.Textarea)

    def clean_emails(self) -> Dict:
        errors = []
        for e in self.cleaned_data["emails"].split():
            try:
                validate_email(e)
            except ValidationError:
                errors.append(e)
        if errors:
            logger.error("Invalid emails {}".format(", ".join(errors)))
            raise ValidationError("Invalid emails {}".format(", ".join(errors)))
        return self.cleaned_data["emails"]


class ImportCSVForm(forms.Form):
    file = forms.FileField()
    delimiter = forms.ChoiceField(label=_("Delimiter"), choices=list(zip(delimiters, delimiters)), initial=",")
    quotechar = forms.ChoiceField(label=_("Quotechar"), choices=list(zip(quotes, quotes)), initial="'")
    quoting = forms.ChoiceField(
        label=_("Quoting"),
        choices=(
            (csv.QUOTE_ALL, _("All")),
            (csv.QUOTE_MINIMAL, _("Minimal")),
            (csv.QUOTE_NONE, _("None")),
            (csv.QUOTE_NONNUMERIC, _("Non Numeric")),
        ),
        initial=csv.QUOTE_ALL,
    )

    escapechar = forms.ChoiceField(label=_("Escapechar"), choices=(("", ""), ("\\", "\\")), required=False)

    enable_kobo = forms.BooleanField(required=False)
    partner = forms.ModelChoiceField(queryset=Partner.objects.all())
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all())
    role = forms.ModelChoiceField(queryset=Role.objects.all())

    _fieldsets = (
        (_("File"), {"fields": ("file",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    (
                        "enable_kobo",
                        "partner",
                        "business_area",
                        "role",
                    ),
                )
            },
        ),
        (
            _("Options"),
            {"classes": ["collapse"], "fields": (("delimiter", "quotechar", "quoting", "escapechar"),)},
        ),
    )
    # row_attrs = {'one': {'style': 'display: none'}}


class LoadUsersForm(forms.Form):
    emails = forms.CharField(widget=forms.Textarea)
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all())
    role = forms.ModelChoiceField(queryset=Role.objects.all())
    enable_kobo = forms.BooleanField(required=False)

    def clean_emails(self) -> Dict:
        errors = []
        for e in self.cleaned_data["emails"].split():
            try:
                validate_email(e)
            except ValidationError:
                errors.append(e)
        if errors:
            logger.error("Invalid emails {}".format(", ".join(errors)))
            raise ValidationError("Invalid emails {}".format(", ".join(errors)))
        return self.cleaned_data["emails"]


class AddRoleForm(forms.Form):
    operation = forms.ChoiceField(choices=(("ADD", "Add"), ("REMOVE", "Remove")))
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all())
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=widgets.FilteredSelectMultiple("Roles", False),
    )
