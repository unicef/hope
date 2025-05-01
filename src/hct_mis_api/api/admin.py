from typing import TYPE_CHECKING, Any

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.db.transaction import atomic
from django.forms import Form
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from smart_admin.modeladmin import SmartModelAdmin

from hct_mis_api.api.models import APILogEntry, APIToken
from hct_mis_api.apps.account.models import ChoiceArrayField
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.utils.security import is_root

if TYPE_CHECKING:
    from uuid import UUID


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

    def __init__(self, *args: Any, instance: Any | None = None, **kwargs: Any) -> None:
        super().__init__(*args, instance=instance, **kwargs)
        if instance:
            self.fields["valid_for"].queryset = BusinessArea.objects.filter(user_roles__user=instance.user).distinct()

    def clean(self) -> None:
        if self.instance and hasattr(self.instance, "user"):
            user = self.instance.user
        else:
            user = self.cleaned_data["user"]
        if not BusinessArea.objects.filter(user_roles__user=user).exists():
            raise ValidationError("This user does not have any Business Areas assigned to him")


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
    formfield_overrides = {
        ChoiceArrayField: {"widget": forms.CheckboxSelectMultiple},
    }
    form = APITokenForm
    search_fields = ("id",)
    raw_id_fields = ("user",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("user")

    def get_fields(self, request: HttpRequest, obj: Any | None = None) -> tuple[str, ...]:
        if obj:
            return super().get_fields(request, obj)
        return "user", "grants", "valid_to"

    def get_readonly_fields(self, request: HttpRequest, obj: Any | None = None) -> tuple[str, ...]:
        if obj:
            return "user", "valid_from"
        return ()

    def _get_email_context(self, request: HttpRequest, obj: Any) -> dict[str, Any]:
        return {
            "obj": obj,
            "friendly_name": obj.user.first_name or obj.user.username,
            "expire": obj.valid_to or "Never",
            "areas": ", ".join(obj.valid_for.values_list("name", flat=True)),
        }

    def _send_token_email(self, request: HttpRequest, obj: Any, template: str) -> None:
        try:
            user = obj.user
            user.email_user(
                subject=f"HOPE API Token {obj} infos",
                text_body=template.format(**self._get_email_context(request, obj)),
            )
            self.message_user(request, f"Email sent to {obj.user.email}", messages.SUCCESS)
        except OSError:
            self.message_user(request, f"Unable to send notification email to {obj.user.email}", messages.ERROR)

    @button(permission=is_root)
    def resend_email(self, request: HttpRequest, pk: "UUID") -> None:
        obj = self.get_object(request, str(pk))
        self._send_token_email(request, obj, TOKEN_INFO_EMAIL)

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: Any | None = None,
        form_url: str = "",
        extra_context: Any | None = None,
    ) -> HttpResponse | HttpResponse | HttpResponseRedirect:
        try:
            return super().changeform_view(request, object_id, form_url, extra_context)
        except NoBusinessAreaAvailable:
            self.message_user(request, "User do not have any Business Areas assigned to him", messages.ERROR)
            return HttpResponseRedirect(reverse(admin_urlname(APIToken._meta, "changelist")))  # type: ignore # str vs SafeString

    def log_addition(self, request: HttpRequest, object: Any, message: str) -> LogEntry:
        return super().log_addition(request, object, message)

    @atomic()
    def save_model(self, request: HttpRequest, obj: Any, form: Form, change: bool) -> None:
        obj.save()
        obj.valid_for.set(BusinessArea.objects.filter(user_roles__user=obj.user))
        obj.save()
        if change:
            self._send_token_email(request, obj, TOKEN_UPDATED_EMAIL)
        else:
            self._send_token_email(request, obj, TOKEN_CREATED_EMAIL)


@admin.register(APILogEntry)
class APILogEntryAdmin(SmartModelAdmin):
    list_display = ("token", "url", "method", "timestamp")
    list_filter = (("token", AutoCompleteFilter), "method")
    date_hierarchy = "timestamp"
    search_fields = "url"

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return False
