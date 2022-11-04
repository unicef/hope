from typing import Any, Dict, Tuple

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.db.transaction import atomic
from django.http import HttpResponseRedirect
from django.urls import reverse

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from smart_admin.modeladmin import SmartModelAdmin

from hct_mis_api.api.models import APILogEntry, APIToken
from hct_mis_api.apps.account.models import ChoiceArrayField
from hct_mis_api.apps.core.models import BusinessArea

TOKEN_INFO_EMAIL = """
Dear {friendly_name},

please find below API token infos

Name: {obj}
Key: {obj.key}
Grants: {obj.grants}
Expires: {expire}
Business Areas: {areas}

Regards

The HOPE Team
"""

TOKEN_CREATED_EMAIL = """
Dear {friendly_name},

you have been assigned a new API token.

Name: {obj}
Key: {obj.key}
Grants: {obj.grants}
Expires: {expire}
Business Areas: {areas}

Regards

The HOPE Team
"""

TOKEN_UPDATED_EMAIL = """
Dear {friendly_name},

your assigned API token {obj} has been updated.

Grants: {obj.grants}
Expires: {expire}
Business Areas: {areas}


Regards

The HOPE Team
"""


class APITokenForm(forms.ModelForm):
    class Meta:
        model = APIToken
        exclude = ("key",)

    def __init__(self, *args, instance=None, **kwargs) -> None:
        super().__init__(*args, instance=instance, **kwargs)
        if instance:
            self.fields["valid_for"].queryset = BusinessArea.objects.filter(user_roles__user=instance.user).distinct()

    def clean(self) -> None:
        if self.instance:
            user = self.instance.user
        else:
            user = self.cleaned_data["user"]
        if not BusinessArea.objects.filter(user_roles__user=user).exists():
            raise ValidationError("This user do not have any Business Areas assigned to him")


class NoBusinessAreaAvailable(Exception):
    pass


@admin.register(APIToken)
class APITokenAdmin(SmartModelAdmin):
    list_display = ("__str__", "user", "valid_from", "valid_to")
    list_filter = (
        ("user", AutoCompleteFilter),
        ("valid_for", AutoCompleteFilter),
    )
    filter_horizontal = ("valid_for",)
    autocomplete_fields = ("user",)
    formfield_overrides = {
        ChoiceArrayField: {"widget": forms.CheckboxSelectMultiple},
    }
    form = APITokenForm
    search_fields = ("id",)

    def get_queryset(self, request) -> QuerySet:
        return super().get_queryset(request).select_related("user")

    def get_fields(self, request, obj=None) -> Tuple[str, ...]:
        if obj:
            return super().get_fields(request, obj)
        return "user", "grants", "valid_to"

    def get_readonly_fields(self, request, obj=None) -> Tuple[str, ...]:
        if obj:
            return "user", "valid_from"
        return tuple()

    def _get_email_context(self, request, obj) -> Dict[str, Any]:
        return {
            "obj": obj,
            "friendly_name": obj.user.first_name or obj.user.username,
            "expire": obj.valid_to or "Never",
            "areas": ", ".join(obj.valid_for.values_list("name", flat=True)),
        }

    def _send_token_email(self, request, obj, template) -> None:
        try:
            send_mail(
                f"HOPE API Token {obj} infos",
                template.format(**self._get_email_context(request, obj)),
                None,
                recipient_list=[obj.user.email],
            )
            self.message_user(request, f"Email sent to {obj.user.email}", messages.SUCCESS)
        except OSError:
            self.message_user(request, f"Unable to send notification email to {obj.user.email}", messages.ERROR)

    @button()
    def resend_email(self, request, pk) -> None:
        obj = self.get_object(request, pk)
        self._send_token_email(request, obj, TOKEN_INFO_EMAIL)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None) -> HttpResponseRedirect:
        try:
            return super().changeform_view(request, object_id, form_url, extra_context)
        except NoBusinessAreaAvailable:
            self.message_user(request, "User do not have any Business Areas assigned to him", messages.ERROR)
            return HttpResponseRedirect(reverse(admin_urlname(APIToken._meta, "changelist")))

    def log_addition(self, request, object, message) -> LogEntry:
        return super().log_addition(request, object, message)

    @atomic()
    def save_model(self, request, obj, form, change) -> None:
        obj.save()
        obj.valid_for.set(BusinessArea.objects.filter(user_roles__user=obj.user))
        obj.save()
        if change:
            self._send_token_email(request, obj, TOKEN_UPDATED_EMAIL)
        else:
            self._send_token_email(request, obj, TOKEN_CREATED_EMAIL)


@admin.register(APILogEntry)
class APILogEntryAdmin(SmartModelAdmin):
    list_display = ("timestamp", "method", "url", "token")
    list_filter = (("token", AutoCompleteFilter),)
    date_hierarchy = "timestamp"

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False
