import csv
import logging
from collections import defaultdict, namedtuple
from typing import TYPE_CHECKING, Any, Sequence, Union

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import ValidationError
from django.db.models import JSONField, QuerySet
from django.db.transaction import atomic
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from jsoneditor.forms import JSONEditor

from hct_mis_api.admin.account_filters import BusinessAreaFilter, HasKoboAccount
from hct_mis_api.admin.account_forms import (
    AddRoleForm,
    HopeUserCreationForm,
    ImportCSVForm,
)
from hct_mis_api.admin.account_mixins import KoboAccessMixin
from hct_mis_api.admin.user_role import RoleAssignmentInline
from hct_mis_api.admin.utils import HopeModelAdminMixin
from hct_mis_api.apps.account import models as account_models
from hct_mis_api.apps.account.models import Partner, User


from django.core.validators import validate_email
from django.forms.forms import Form

from requests import HTTPError

from hct_mis_api.admin.steficon import AutocompleteWidget
from hct_mis_api.apps.account.microsoft_graph import DJANGO_USER_MAP, MicrosoftGraphAPI
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import build_arg_dict_from_dict


if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models.query import _QuerySet

logger = logging.getLogger(__name__)


class LoadUsersForm(forms.Form):
    emails = forms.CharField(widget=forms.Textarea, help_text="Emails must be space separated")
    role = forms.ModelChoiceField(queryset=account_models.Role.objects.all())
    business_area = forms.ModelChoiceField(
        queryset=BusinessArea.objects.all().order_by("name"),
        required=True,
        widget=AutocompleteWidget(BusinessArea, ""),
    )
    partner = forms.ModelChoiceField(
        queryset=account_models.Partner.objects.all().order_by("name"),
        required=True,
        widget=AutocompleteWidget(Partner, ""),
    )
    enable_kobo = forms.BooleanField(required=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean_emails(self) -> dict:
        errors = []
        for e in self.cleaned_data["emails"].split():
            try:
                validate_email(e)
            except ValidationError:
                errors.append(e)
        if errors:
            raise ValidationError("Invalid emails {}".format(", ".join(errors)))
        return self.cleaned_data["emails"]


class ADUSerMixin:
    ad_form_class = LoadUsersForm
    Results = namedtuple("Results", "created,missing,updated,errors")

    def _get_ad_form(self, request: HttpRequest) -> Form:
        if request.method == "POST":
            return self.ad_form_class(request.POST, request=request)
        return self.ad_form_class(request=request)

    def _sync_ad_data(self, user: User) -> None:
        ms_graph = MicrosoftGraphAPI()
        if user.ad_uuid:
            filters = [{"uuid": user.ad_uuid}, {"email": user.email}]
        else:
            filters = [{"email": user.email}]

        for _filter in filters:
            try:
                user_data = ms_graph.get_user_data(**_filter)
                user_args = build_arg_dict_from_dict(user_data, DJANGO_USER_MAP)
                for field, value in user_args.items():
                    setattr(user, field, value or "")
                user.save()
                break
            except Http404:
                pass
        else:
            raise Http404

    @button(label="AD Sync", permission="account.can_sync_with_ad")
    def sync_multi(self, request: HttpRequest) -> None:
        not_found = []
        try:
            for user in self.get_queryset(request):
                try:
                    self._sync_ad_data(user)
                except Http404:
                    not_found.append(str(user))
            if not_found:
                self.message_user(
                    request,
                    f"These users were not found: {', '.join(not_found)}",
                    messages.WARNING,
                )
            else:
                self.message_user(
                    request,
                    "Active Directory data successfully fetched",
                    messages.SUCCESS,
                )
        except Exception as e:
            logger.warning(e)
            self.message_user(request, str(e), messages.ERROR)

    @button(label="Sync", permission="account.can_sync_with_ad")
    def sync_single(self, request: HttpRequest, pk: int) -> None:
        try:
            self._sync_ad_data(self.get_object(request, pk))
            self.message_user(request, "Active Directory data successfully fetched", messages.SUCCESS)
        except Exception as e:
            logger.warning(e)
            self.message_user(request, str(e), messages.ERROR)

    @button(permission="account.can_load_from_ad")
    def load_ad_users(self, request: HttpRequest) -> TemplateResponse:
        ctx = self.get_common_context(
            request,
            None,
            change=True,
            is_popup=False,
            save_as=False,
            has_delete_permission=False,
            has_add_permission=False,
            has_change_permission=True,
        )
        form = self._get_ad_form(request)
        if request.method == "POST":
            if form.is_valid():
                emails = set(form.cleaned_data["emails"].split())
                role = form.cleaned_data["role"]
                business_area = form.cleaned_data["business_area"]
                partner = form.cleaned_data["partner"]
                users_to_bulk_create = []
                users_role_to_bulk_create = []
                existing = set(account_models.User.objects.filter(email__in=emails).values_list("email", flat=True))
                results = self.Results([], [], [], [])
                try:
                    ms_graph = MicrosoftGraphAPI()
                    for email in emails:
                        try:
                            if email in existing:
                                user = account_models.User.objects.get(email=email)
                                self._sync_ad_data(user)
                                results.updated.append(user)
                            else:
                                user_data = ms_graph.get_user_data(email=email)
                                user_args = build_arg_dict_from_dict(user_data, DJANGO_USER_MAP)
                                user = account_models.User(**user_args, partner=partner)
                                if user.first_name is None:
                                    user.first_name = ""
                                if user.last_name is None:
                                    user.last_name = ""
                                job_title = user_data.get("jobTitle")
                                if job_title is not None:
                                    user.job_title = job_title
                                user.set_unusable_password()
                                users_to_bulk_create.append(user)
                                global_business_area = BusinessArea.objects.filter(slug="global").first()
                                basic_role = account_models.Role.objects.filter(name="Basic User").first()
                                if global_business_area and basic_role:
                                    users_role_to_bulk_create.append(
                                        account_models.RoleAssignment(
                                            business_area=global_business_area,
                                            user=user,
                                            role=basic_role,
                                        )
                                    )
                                results.created.append(user)

                            users_role_to_bulk_create.append(
                                account_models.RoleAssignment(role=role, business_area=business_area, user=user)
                            )
                        except HTTPError as e:
                            if e.response.status_code != 404:
                                raise
                            results.missing.append(email)
                        except Http404:
                            results.missing.append(email)
                    account_models.User.objects.bulk_create(users_to_bulk_create)
                    account_models.RoleAssignment.objects.bulk_create(users_role_to_bulk_create, ignore_conflicts=True)
                    ctx["results"] = results
                    return TemplateResponse(request, "admin/load_users.html", ctx)
                except Exception as e:
                    logger.warning(e)
                    self.message_user(request, str(e), messages.ERROR)
        ctx["form"] = form
        return TemplateResponse(request, "admin/load_users.html", ctx)


@admin.register(account_models.User)
class UserAdmin(HopeModelAdminMixin, KoboAccessMixin, BaseUserAdmin, ADUSerMixin):
    Results = namedtuple("Results", "created,missing,updated,errors")
    add_form = HopeUserCreationForm
    add_form_template = "admin/auth/user/add_form.html"
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email"),
            },
        ),
    )
    readonly_fields = ("ad_uuid", "last_modify_date")

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
    base_fieldset = (
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "username",
                    "job_title",
                    "partner",
                )
            },
        ),
    )
    extra_fieldsets = (
        (
            _("Custom Fields"),
            {"classes": ["collapse"], "fields": ("custom_fields", "ad_uuid")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    ("password",),
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
                ),
            },
        ),
    )
    inlines = (RoleAssignmentInline,)
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

    def get_readonly_fields(self, request: HttpRequest, obj: Any | None = ...) -> Sequence[str]:
        if request.user.has_perm("account.restrict_help_desk"):
            return super().get_readonly_fields(request, obj)
        return self.get_fields(request)

    def get_fields(self, request: HttpRequest, obj: Any | None = None) -> list[str]:
        return ["last_name", "first_name", "email", "username", "job_title", "last_login"]

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = None) -> Any:
        fieldsets = self.base_fieldset
        if request.user.is_superuser:
            fieldsets += self.extra_fieldsets  # type: ignore
        return fieldsets

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

    @button(permission="auth.view_permission")
    def privileges(self, request: HttpRequest, pk: "UUID") -> TemplateResponse:
        context = self.get_common_context(request, pk)
        user: account_models.User = context["original"]
        all_perms = user.get_all_permissions()
        context["permissions"] = [p.split(".") for p in sorted(all_perms)]
        ba_perms = defaultdict(list)
        ba_roles = defaultdict(list)
        for role in user.role_assignments.all():
            ba_roles[role.business_area.slug].append(role.role)

        for role in user.role_assignments.values_list("business_area__slug", flat=True).distinct("business_area"):
            ba_perms[role].extend(user.permissions_in_business_area(role))

        context["business_ares_permissions"] = dict(ba_perms)
        context["business_ares_roles"] = dict(ba_roles)
        return TemplateResponse(request, "admin/account/user/privileges.html", context)

    def get_actions(self, request: HttpRequest) -> dict:
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
                                    ur, is_new = u.role_assignments.get_or_create(business_area=ba, role=role)
                                    if is_new:
                                        added += 1
                                        self.log_addition(request, ur, "Role added")
                                except ValidationError as e:
                                    self.message_user(request, str(e), messages.ERROR)
                            elif crud == "REMOVE":
                                to_delete = u.role_assignments.filter(business_area=ba, role=role).first()
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
        ctx = self.get_common_context(request, title="Add Role", selection=queryset)
        ctx["form"] = AddRoleForm()
        return render(request, "admin/account/user/business_area_role.html", context=ctx)

    add_business_area_role.short_description = "Add/Remove Business Area roles"

    @button(label="Import CSV", permission="account.can_upload_to_kobo")
    def import_csv(self, request: HttpRequest) -> TemplateResponse:
        from django.contrib.admin.helpers import AdminForm

        context: dict = self.get_common_context(request, processed=False)
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
                                    ur = u.role_assignments.create(business_area=business_area, role=role)
                                    self.log_addition(request, u, "User imported by CSV")
                                    self.log_addition(request, ur, "User Role added")
                                else:  # check role validity
                                    try:
                                        account_models.IncompatibleRoles.objects.validate_user_role(
                                            u, business_area, role
                                        )
                                        u.role_assignments.get_or_create(business_area=business_area, role=role)
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
                    logger.warning(e)
                    context["form"] = form
                    context["errors"] = [str(e)]
                    self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)
            else:
                self.message_user(request, "Please correct errors below", messages.ERROR)
                context["form"] = form
        fs = form._fieldsets or [(None, {"fields": form.base_fields})]
        context["adminform"] = AdminForm(form, fieldsets=fs, prepopulated_fields={})  # type: ignore # FIXME
        return TemplateResponse(request, "admin/account/user/import_csv.html", context)

    def __init__(self, model: type, admin_site: Any) -> None:
        super().__init__(model, admin_site)

    def formfield_for_foreignkey(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "partner":  # Exclude partners that are parent partners
            kwargs["queryset"] = Partner.objects.exclude(
                id__in=Partner.objects.exclude(parent__isnull=True).values_list("parent", flat=True)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
