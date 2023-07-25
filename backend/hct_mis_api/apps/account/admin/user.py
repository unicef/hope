import csv
import logging
from collections import defaultdict, namedtuple
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Type, Union

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import ValidationError
from django.db.models import JSONField, QuerySet
from django.db.transaction import atomic
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from admin_extra_buttons.decorators import button
from admin_sync.mixin import SyncMixin
from adminfilters.autocomplete import AutoCompleteFilter
from jsoneditor.forms import JSONEditor
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.account import models as account_models
from hct_mis_api.apps.account.admin.ad import ADUSerMixin
from hct_mis_api.apps.account.admin.filters import BusinessAreaFilter, HasKoboAccount
from hct_mis_api.apps.account.admin.forms import (
    AddRoleForm,
    HopeUserCreationForm,
    ImportCSVForm,
)
from hct_mis_api.apps.account.admin.mixins import KoboAccessMixin
from hct_mis_api.apps.account.admin.user_role import UserRoleInline
from hct_mis_api.apps.utils.admin import HopeModelAdminMixin

if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models.query import _QuerySet

logger = logging.getLogger(__name__)


@admin.register(account_models.User)
class UserAdmin(HopeModelAdminMixin, SyncMixin, KoboAccessMixin, LinkedObjectsMixin, BaseUserAdmin, ADUSerMixin):
    Results = namedtuple("Results", "created,missing,updated,errors")
    add_form = HopeUserCreationForm
    add_form_template = "admin/auth/user/add_form.html"
    readonly_fields = ("ad_uuid", "last_modify_date", "doap_hash")

    change_form_template = None
    hijack_success_url = f"/api/{settings.ADMIN_PANEL_URL}/"
    list_filter = (
        ("partner", AutoCompleteFilter),
        BusinessAreaFilter,
        "is_staff",
        HasKoboAccount,
        "is_superuser",
        "is_active",
    )
    list_display = (
        "username",
        "email",
        "partner",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "kobo_user",
    )
    fieldsets = (
        (
            _("Personal info"),
            {
                "fields": (
                    "partner",
                    "username",
                    "password",
                    (
                        "first_name",
                        "last_name",
                    ),
                    ("email", "ad_uuid"),
                )
            },
        ),
        (
            _("Custom Fields"),
            {"classes": ["collapse"], "fields": ("custom_fields", "doap_hash")},
        ),
        (
            _("Permissions"),
            {
                "classes": ["collapse"],
                "fields": (
                    (
                        "is_active",
                        "is_staff",
                        "is_superuser",
                    ),
                    ("groups",),
                ),
            },
        ),
        (
            _("Important dates"),
            {
                "classes": ["collapse"],
                "fields": (
                    "last_login",
                    "date_joined",
                    "last_modify_date",
                    "last_doap_sync",
                ),
            },
        ),
        (_("Job Title"), {"fields": ("job_title",)}),
    )
    inlines = (UserRoleInline,)
    actions = ["create_kobo_user_qs", "add_business_area_role"]
    formfield_overrides = {
        JSONField: {"widget": JSONEditor},
    }

    @property
    def media(self) -> Any:
        return super().media + forms.Media(js=["hijack/hijack.js"])

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "partner",
            )
        )

    def get_fields(self, request: HttpRequest, obj: Optional[Any] = None) -> List[str]:
        return [
            "last_name",
            "first_name",
            "email",
            "partner",
            "job_title",
        ]

    def get_fieldsets(self, request: HttpRequest, obj: Optional[Any] = None) -> Any:
        if request.user.is_superuser:
            return super().get_fieldsets(request, obj)
        return [(None, {"fields": self.get_fields(request, obj)})]

    def kobo_user(self, obj: Any) -> str:
        return obj.custom_fields.get("kobo_username")

    def get_deleted_objects(self, objs: Union[Sequence[Any], "_QuerySet[Any, Any]"], request: HttpRequest) -> Any:
        to_delete, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)
        user = objs[0]
        kobo_pk = user.custom_fields.get("kobo_pk", None)
        kobo_username = user.custom_fields.get("kobo_username", None)
        if kobo_pk:
            to_delete.append(f"Kobo: {kobo_username}")  # type: ignore # this is somehow intentional
        return to_delete, model_count, perms_needed, protected

    @button()
    def privileges(self, request: HttpRequest, pk: "UUID") -> TemplateResponse:
        context = self.get_common_context(request, pk)
        user: account_models.User = context["original"]
        all_perms = user.get_all_permissions()
        context["permissions"] = [p.split(".") for p in sorted(all_perms)]
        ba_perms = defaultdict(list)
        ba_roles = defaultdict(list)
        for role in user.user_roles.all():
            ba_roles[role.business_area.slug].append(role.role)

        for role in user.user_roles.values_list("business_area__slug", flat=True).distinct("business_area"):
            ba_perms[role].extend(user.permissions_in_business_area(role))

        context["business_ares_permissions"] = dict(ba_perms)
        context["business_ares_roles"] = dict(ba_roles)
        return TemplateResponse(request, "admin/account/user/privileges.html", context)

    def get_actions(self, request: HttpRequest) -> Dict:
        actions = super().get_actions(request)
        if not request.user.has_perm("account.can_create_kobo_user"):
            if "create_kobo_user_qs" in actions:
                del actions["create_kobo_user_qs"]
        if not request.user.has_perm("account.add_userrole"):
            if "add_business_area_role" in actions:
                del actions["add_business_area_role"]
        return actions

    def add_business_area_role(self, request: HttpRequest, queryset: QuerySet) -> HttpResponse:
        if "apply" in request.POST:
            form = AddRoleForm(request.POST)
            if form.is_valid():
                ba = form.cleaned_data["business_area"]
                roles = form.cleaned_data["roles"]
                crud = form.cleaned_data["operation"]

                with atomic():
                    users, added, removed = 0, 0, 0
                    for u in queryset.all():
                        users += 1
                        for role in roles:
                            if crud == "ADD":
                                try:
                                    account_models.IncompatibleRoles.objects.validate_user_role(u, ba, role)
                                    ur, is_new = u.user_roles.get_or_create(business_area=ba, role=role)
                                    if is_new:
                                        added += 1
                                        self.log_addition(request, ur, "Role added")
                                except ValidationError as e:
                                    self.message_user(request, str(e), messages.ERROR)
                            elif crud == "REMOVE":
                                to_delete = u.user_roles.filter(business_area=ba, role=role).first()
                                if to_delete:
                                    removed += 1
                                    self.log_deletion(request, to_delete, str(to_delete))
                                    to_delete.delete()
                            else:
                                raise ValueError("Bug found. {} not valid operation for add/rem role")
                    if removed:
                        msg = f"{removed} roles removed from {users} users"
                    elif added:
                        msg = f"{added} roles granted to {users} users"
                    else:
                        msg = f"{users} users processed no actions have been required"

                    self.message_user(request, msg)
            return HttpResponseRedirect(request.get_full_path())
        else:
            ctx = self.get_common_context(request, title="Add Role", selection=queryset)
            ctx["form"] = AddRoleForm()
            return render(request, "admin/account/user/business_area_role.html", context=ctx)

    add_business_area_role.short_description = "Add/Remove Business Area roles"

    @button(label="Import CSV", permission="account.can_upload_to_kobo")
    def import_csv(self, request: HttpRequest) -> TemplateResponse:
        from django.contrib.admin.helpers import AdminForm

        context: Dict = self.get_common_context(request, processed=False)
        if request.method == "GET":
            form = ImportCSVForm(initial={"partner": account_models.Partner.objects.first()})
            context["form"] = form
        else:
            form = ImportCSVForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                try:
                    context["processed"] = True
                    csv_file = form.cleaned_data["file"]
                    enable_kobo = form.cleaned_data["enable_kobo"]
                    partner = form.cleaned_data["partner"]
                    business_area = form.cleaned_data["business_area"]
                    role = form.cleaned_data["role"]

                    if csv_file.multiple_chunks():
                        raise Exception("Uploaded file is too big (%.2f MB)" % (csv_file.size(1000 * 1000)))
                    data_set = csv_file.read().decode("utf-8-sig").splitlines()
                    reader = csv.DictReader(
                        data_set,
                        quotechar=form.cleaned_data["quotechar"],
                        quoting=int(form.cleaned_data["quoting"]),
                        delimiter=form.cleaned_data["delimiter"],
                    )
                    results = []
                    context["results"] = results
                    context["reader"] = reader
                    context["errors"] = []
                    with atomic():
                        try:
                            for row in reader:
                                try:
                                    email = row["email"].strip()
                                except Exception as e:
                                    raise Exception(f"{e.__class__.__name__}: {e} on `{row}`")

                                user_info = {
                                    "email": email,
                                    "is_new": False,
                                    "kobo": False,
                                    "error": "",
                                }
                                if "username" in row:
                                    username = row["username"].strip()
                                else:
                                    username = row["email"].replace("@", "_").replace(".", "_").lower()
                                u, isnew = account_models.User.objects.get_or_create(
                                    email=email,
                                    partner=partner,
                                    defaults={"username": username},
                                )
                                if isnew:
                                    ur = u.user_roles.create(business_area=business_area, role=role)
                                    self.log_addition(request, u, "User imported by CSV")
                                    self.log_addition(request, ur, "User Role added")
                                else:  # check role validity
                                    try:
                                        account_models.IncompatibleRoles.objects.validate_user_role(
                                            u, business_area, role
                                        )
                                        u.user_roles.get_or_create(business_area=business_area, role=role)
                                        self.log_addition(request, ur, "User Role added")
                                    except ValidationError as e:
                                        self.message_user(
                                            request,
                                            f"Error on {u}: {e}",
                                            messages.ERROR,
                                        )

                                if enable_kobo:
                                    self._grant_kobo_accesss_to_user(u, sync=False)

                                context["results"].append(user_info)
                        except Exception:
                            raise
                except Exception as e:
                    logger.exception(e)
                    context["form"] = form
                    context["errors"] = [str(e)]
                    self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)
            else:
                self.message_user(request, "Please correct errors below", messages.ERROR)
                context["form"] = form
        fs = form._fieldsets or [(None, {"fields": form.base_fields})]
        context["adminform"] = AdminForm(form, fieldsets=fs, prepopulated_fields={})  # type: ignore # FIXME
        return TemplateResponse(request, "admin/account/user/import_csv.html", context)

    def __init__(self, model: Type, admin_site: Any) -> None:
        super().__init__(model, admin_site)
