import csv
import logging

from adminactions.api import delimiters, quotes
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _

from models import account as account_models
from models.account import Partner, Role
from hope.apps.account.permissions import Permissions
from models.core import BusinessArea

logger = logging.getLogger(__name__)


class RoleAdminForm(forms.ModelForm):
    permissions = forms.MultipleChoiceField(
        required=False,
        widget=FilteredSelectMultiple("", False),
        choices=Permissions.choices(),
    )

    class Meta:
        model = account_models.Role
        fields = (
            "name",
            "subsystem",
            "permissions",
            "is_visible_on_ui",
            "is_available_for_partner",
        )


class RoleAssignmentAdminForm(forms.ModelForm):
    role = forms.ModelChoiceField(account_models.Role.objects.order_by("name"))
    business_area = forms.ModelChoiceField(BusinessArea.objects.filter(is_split=False))

    class Meta:
        model = account_models.RoleAssignment
        fields = (
            "business_area",
            "user",
            "partner",
            "role",
            "program",
            "expiry_date",
            "group",
        )

    def clean(self) -> None:
        super().clean()
        if not self.is_valid():
            return
        role = self.cleaned_data["role"]
        user = self.cleaned_data["user"]
        business_area = self.cleaned_data["business_area"]

        account_models.IncompatibleRoles.objects.validate_user_role(user, business_area, role)


class RoleAssignmentInlineFormSet(forms.BaseInlineFormSet):
    model = account_models.RoleAssignment

    def add_fields(self, form: "forms.Form", index: int | None) -> None:
        super().add_fields(form, index)
        form.fields["role"].required = True

    def clean(self) -> None:
        super().clean()
        if not self.is_valid():
            return
        for form in self.forms:
            if not form.is_valid():
                return
            if form.cleaned_data and not form.cleaned_data.get("DELETE"):
                business_area = form.cleaned_data["business_area"]
                role = form.cleaned_data["role"]
                incompatible_roles = list(
                    account_models.IncompatibleRoles.objects.filter(role_one=role).values_list("role_two", flat=True)
                ) + list(
                    account_models.IncompatibleRoles.objects.filter(role_two=role).values_list("role_one", flat=True)
                )
                error_forms = [
                    form_two.cleaned_data["role"].name
                    for form_two in self.forms
                    if form_two.cleaned_data
                    and not form_two.cleaned_data.get("DELETE")
                    and form_two.cleaned_data["business_area"] == business_area
                    and form_two.cleaned_data["role"].id in incompatible_roles
                ]
                if error_forms:
                    if "role" not in form._errors:
                        form._errors["role"] = ErrorList()
                    form._errors["role"].append(_(f"{role.name} is incompatible with {', '.join(error_forms)}."))


class HopeUserCreationForm(UserCreationForm):
    class Meta:
        model = account_models.User
        fields = ()
        field_classes = {"username": UsernameField, "email": forms.EmailField}


class AddRoleForm(forms.Form):
    operation = forms.ChoiceField(choices=(("ADD", "Add"), ("REMOVE", "Remove")))
    business_area = forms.ModelChoiceField(queryset=BusinessArea.objects.all())
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=FilteredSelectMultiple("Roles", False),
    )


class KoboLoginForm(forms.Form):
    kobo_username = forms.CharField()
    kobo_password = forms.CharField(widget=forms.PasswordInput)


class KoboImportUsersForm(forms.Form):
    emails = forms.CharField(required=False, widget=forms.Textarea)

    def clean_emails(self) -> dict:
        errors = []
        for e in self.cleaned_data["emails"].split():
            try:
                validate_email(e)
            except ValidationError:
                errors.append(e)
        if errors:
            logger.warning("Invalid emails {}".format(", ".join(errors)))
            raise ValidationError("Invalid emails {}".format(", ".join(errors)))
        return self.cleaned_data["emails"]


class ImportCSVForm(forms.Form):
    file = forms.FileField()
    delimiter = forms.ChoiceField(
        label=_("Delimiter"),
        choices=list(zip(delimiters, delimiters, strict=True)),
        initial=",",
    )
    quotechar = forms.ChoiceField(
        label=_("Quotechar"),
        choices=list(zip(quotes, quotes, strict=True)),
        initial="'",
    )
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
            {
                "classes": ["collapse"],
                "fields": (("delimiter", "quotechar", "quoting", "escapechar"),),
            },
        ),
    )
