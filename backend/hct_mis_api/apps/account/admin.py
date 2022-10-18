import csv
import logging
import re
from collections import defaultdict, namedtuple
from functools import cached_property
from urllib.parse import unquote

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.utils import construct_change_message
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as _GroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import router, transaction
from django.db.models import JSONField, Q
from django.db.transaction import atomic
from django.forms import EmailField, ModelChoiceField, MultipleChoiceField
from django.forms.models import BaseInlineFormSet, ModelForm
from django.forms.utils import ErrorList
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

import requests
from admin_extra_buttons.api import button
from admin_sync.mixin import GetManyFromRemoteMixin, SyncMixin
from adminactions.export import ForeignKeysCollector
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import AllValuesComboFilter
from constance import config
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ManyToManyWidget
from jsoneditor.forms import JSONEditor
from requests import HTTPError
from smart_admin.decorators import smart_register
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.account import models as account_models
from hct_mis_api.apps.account.forms import AddRoleForm, ImportCSVForm
from hct_mis_api.apps.account.microsoft_graph import DJANGO_USER_MAP, MicrosoftGraphAPI
from hct_mis_api.apps.account.models import IncompatibleRoles, Partner, Role, User
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import build_arg_dict_from_dict
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase, HopeModelAdminMixin

logger = logging.getLogger(__name__)


class RoleAdminForm(ModelForm):
    permissions = MultipleChoiceField(
        required=False,
        widget=FilteredSelectMultiple("", False),
        choices=Permissions.choices(),
    )

    class Meta:
        model = account_models.UserRole
        fields = "__all__"


class UserRoleAdminForm(ModelForm):
    role = ModelChoiceField(account_models.Role.objects.order_by("name"))
    business_area = ModelChoiceField(BusinessArea.objects.filter(is_split=False))

    class Meta:
        model = account_models.UserRole
        fields = "__all__"

    def clean(self):
        super().clean()
        if not self.is_valid():
            return
        role = self.cleaned_data["role"]
        user = self.cleaned_data["user"]
        business_area = self.cleaned_data["business_area"]

        account_models.IncompatibleRoles.objects.validate_user_role(user, business_area, role)


class UserRoleInlineFormSet(BaseInlineFormSet):
    model = account_models.UserRole

    def add_fields(self, form, index):
        super().add_fields(form, index)
        form.fields["business_area"].choices = [
            (str(x.id), str(x)) for x in BusinessArea.objects.filter(is_split=False)
        ]

    def clean(self):
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


class UserRoleInline(admin.TabularInline):
    model = account_models.UserRole
    extra = 0
    formset = UserRoleInlineFormSet


KOBO_ACCESS_EMAIL = """

You have been authorised to access to HOPE/Kobo

Follow this link {kobo_url} and use below credentials:

Username:{email}
Password:{password}

The HOPE team.
"""


def get_valid_kobo_username(user: User):
    return user.username.replace("@", "_at_").replace(".", "_").replace("+", "_").lower()


class DjAdminManager:
    regex = re.compile(r'class="errorlist"><li>(.*)(?=<\/li>)')

    class ResponseException(Exception):
        pass

    def __init__(self, kf_host=settings.KOBO_KF_URL, kc_host=settings.KOBO_KC_URL):
        self.admin_path = "/admin/"
        self.admin_url = f"{kf_host}{self.admin_path}"
        self.login_url = f"{self.admin_url}login/"

        self.admin_url_kc = f"{kc_host}{self.admin_path}"
        self.login_url_kc = f"{self.admin_url_kc}login/"
        self._logged = False
        self._last_error = None
        self._last_response = False
        self._username = None
        self._password = None
        self.form_errors = []

    def extract_errors(self, res):
        self.form_errors = [msg for msg in self.regex.findall(res.content.decode())]
        return self.form_errors

    def assert_response(self, status: [int], location: str = None, custom_error=""):
        if not isinstance(status, (list, tuple)):
            status = [status]
        if self._last_response.status_code not in status:
            msg = f"Unexpected code:{self._last_response.status_code} not in {status}: {custom_error}"
            self._last_error = self._last_response
            raise self.ResponseException(msg)

        if location and (redir_to := self._last_response.headers.get("location", "N/A")) != location:
            msg = f"Unexpected redirect:{redir_to} <> {location}: {custom_error}"
            self._last_error = self._last_response
            raise self.ResponseException(msg)

    @cached_property
    def client(self):
        client = requests.Session()
        client.headers["Referer"] = self.admin_url
        client.headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.77 Safari/537.36"
        )
        return client

    def logout(self, request):
        self._username = request.session["kobo_username"] = None
        self._password = request.session["kobo_password"] = None

    def login(self, request=None, twin=None):
        try:
            username, password = config.KOBO_ADMIN_CREDENTIALS.split(":")
        except ValueError:
            raise ValueError("Invalid KOBO_ADMIN_CREDENTIALS")
        try:
            try:
                self._get(self.login_url)
                csrftoken = self.get_csrfmiddlewaretoken()
                self._post(
                    self.login_url,
                    {
                        "username": username,
                        "password": password,
                        "next": self.admin_url,
                        "csrfmiddlewaretoken": csrftoken,
                    },
                )
                self.assert_response(302, self.admin_url)
            except Exception as e:
                raise self.ResponseException(
                    f"Unable to login to Kobo at "
                    f"{self.login_url}: {e.__class__.__name__} {e}. "
                    f"Check KOBO_ADMIN_CREDENTIALS value"
                )

        except Exception as e:
            logger.exception(e)
            raise

    def _get(self, url):
        self._last_response = self.client.get(url, allow_redirects=False)
        self.client.headers["Referer"] = url
        return self._last_response

    def _post(self, url, data):
        self._last_response = self.client.post(url, data, allow_redirects=False)
        return self._last_response

    def list_users(self, q=""):
        regex = re.compile(
            r'action-checkbox.*value="(?P<id>\d+)".*</td>.*field-username.*<a.*?>(?P<username>.*)</a></t.>.*field-email">(?P<mail>.*?)<',
            re.MULTILINE + re.IGNORECASE,
        )
        page = 1
        last_match = None
        while True:
            url = f"{self.admin_url}auth/user/?q={q}&p={page}"
            res = self._get(url)
            self.assert_response(200)
            matches = regex.findall(res.content.decode())
            if matches[0] == last_match:
                break
            last_match = matches[0]
            yield from matches

            page += 1

    def get_csrfmiddlewaretoken(self):
        regex = re.compile("""csrfmiddlewaretoken["'] +value=["'](.*)["']""")
        try:
            m = regex.search(self._last_response.content.decode("utf8"))
            return m.groups()[0]
        except Exception:
            raise ValueError("Unable to get CSRF token from Kobo")

    def delete_user(self, username, pk):
        self.login()
        for url in (f"{self.admin_url_kc}auth/user/{pk}/delete/", f"{self.admin_url}auth/user/{pk}/delete/"):
            self._get(url)
            self.assert_response([200, 404, 302], custom_error=url)
            if self._last_response.status_code == 302 and "/login/" in self._last_response.headers["Location"]:
                raise Exception(f"Cannot access to {url}")

            if self._last_response.status_code == 200:
                # csrftoken = self.client.cookies.get_dict()['csrftoken']
                csrftoken = self.get_csrfmiddlewaretoken()
                self._post(url, {"csrfmiddlewaretoken": csrftoken, "post": "yes"})
                self.assert_response(302, custom_error=f"{url} - {csrftoken}")


class HasKoboAccount(SimpleListFilter):
    parameter_name = "kobo_account"
    title = "Has Kobo Access"

    def lookups(self, request, model_admin):
        return (1, "Yes"), (0, "No")

    def queryset(self, request, queryset):
        if self.value() == "0":
            return queryset.filter(Q(custom_fields__kobo_pk__isnull=True) | Q(custom_fields__kobo_pk=None))
        elif self.value() == "1":
            return queryset.filter(custom_fields__kobo_pk__isnull=False).exclude(custom_fields__kobo_pk=None)
        return queryset


class BusinessAreaFilter(SimpleListFilter):
    parameter_name = "ba"
    title = "Business Area"
    template = "adminfilters/combobox.html"

    def lookups(self, request, model_admin):
        return BusinessArea.objects.filter(user_roles__isnull=False).values_list("id", "name").distinct()

    def queryset(self, request, queryset):
        return queryset.filter(user_roles__business_area=self.value()).distinct() if self.value() else queryset


@admin.register(account_models.Partner)
class PartnerAdmin(HopeModelAdminMixin, admin.ModelAdmin):
    list_filter = ("is_un",)
    search_fields = ("name",)


class HopeUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ()
        field_classes = {"username": UsernameField, "email": EmailField}


@admin.register(account_models.User)
class UserAdmin(HopeModelAdminMixin, SyncMixin, LinkedObjectsMixin, BaseUserAdmin):
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
    def media(self):
        return super().media + forms.Media(js=["hijack/hijack.js"])

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "partner",
            )
        )

    def get_fields(self, request, obj=None):
        return [
            "last_name",
            "first_name",
            "email",
            "partner",
            "job_title",
        ]

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_fieldsets(request, obj)
        return [(None, {"fields": self.get_fields(request, obj)})]

    def kobo_user(self, obj):
        return obj.custom_fields.get("kobo_username")

    def get_deleted_objects(self, objs, request):
        to_delete, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)
        user = objs[0]
        kobo_pk = user.custom_fields.get("kobo_pk", None)
        kobo_username = user.custom_fields.get("kobo_username", None)
        if kobo_pk:
            to_delete.append(f"Kobo: {kobo_username}")
        return to_delete, model_count, perms_needed, protected

    def delete_view(self, request, object_id, extra_context=None):
        if request.POST:  # The user has confirmed the deletion.
            with transaction.atomic(using=router.db_for_write(self.model)):
                res = self._delete_view(request, object_id, extra_context)
        else:
            obj: account_models.User = self.get_object(request, unquote(object_id))
            kobo_pk = obj.custom_fields.get("kobo_pk", None)
            extra_context = extra_context or {}
            try:
                api = DjAdminManager()
                api.login(request)
                extra_context["kobo_pk"] = kobo_pk
                self.message_user(
                    request,
                    "This action will also delete linked Kobo account",
                    messages.WARNING,
                )
            except Exception as e:
                extra_context["kobo_failed"] = True
                self.message_user(request, str(e), messages.ERROR)
            res = super().delete_view(request, object_id, extra_context)

        return res

    def delete_model(self, request, obj):
        try:
            if "kobo_username" in obj.custom_fields:
                api = DjAdminManager()
                api.login(request)
                api.delete_user(obj.custom_fields["kobo_username"], obj.custom_fields["kobo_pk"])
            super().delete_model(request, obj)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, str(e), messages.ERROR)
            raise

    @button()
    def privileges(self, request, pk):
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

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.has_perm("account.can_create_kobo_user"):
            if "create_kobo_user_qs" in actions:
                del actions["create_kobo_user_qs"]
        if not request.user.has_perm("account.add_userrole"):
            if "add_business_area_role" in actions:
                del actions["add_business_area_role"]
        return actions

    def add_business_area_role(self, request, queryset):
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
                                    IncompatibleRoles.objects.validate_user_role(u, ba, role)
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

    def _grant_kobo_accesss_to_user(self, user, notify=True, sync=True):
        password = get_random_string(length=12)
        url = f"{settings.KOBO_KF_URL}/authorized_application/users/"
        username = get_valid_kobo_username(user)
        res = requests.post(
            url,
            headers={"Authorization": f"Token {config.KOBO_APP_API_TOKEN}"},
            json={
                "username": username,
                "email": user.email,
                "password": password,
                "last_name": user.last_name,
                "first_name": user.first_name,
            },
        )
        if res.status_code != 201:
            raise Exception(res.content)
        if res.status_code == 400:
            raise Exception(res.content)

        if sync:
            api = DjAdminManager()
            api.login()
            for entry in api.list_users(q=username):
                if entry[1] == username and entry[2] == user.email:
                    user.custom_fields["kobo_pk"] = entry[0]
                    user.custom_fields["kobo_username"] = entry[1]
                    user.save()
        if res.status_code == 201 and notify:
            send_mail(
                "Kobo credentials",
                KOBO_ACCESS_EMAIL.format(email=user.email, password=password, kobo_url=settings.KOBO_KF_URL),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
        user.custom_fields["kobo_username"] = user.username
        user.save()

    def create_kobo_user_qs(self, request, queryset):
        for user in queryset.all():
            try:
                self._grant_kobo_accesss_to_user(request, user)
            except Exception as e:
                logger.exception(e)
                self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)
        self.message_user(
            request,
            f"User successfully `{user.username}` created on Kobo",
            messages.SUCCESS,
        )

    @button(
        permission="account.can_create_kobo_user",
        enabled=lambda b: not b.original.custom_fields.get("kobo_username"),
    )
    def create_kobo_user(self, request, pk):
        try:
            self._grant_kobo_accesss_to_user(self.get_queryset(request).get(pk=pk))
            self.message_user(request, f"Granted access to {settings.KOBO_KF_URL}", messages.SUCCESS)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)

    @button(
        permission="account.can_create_kobo_user",
        enabled=lambda b: not b.custom_fields.get("kobo_username"),
    )
    def remove_kobo_access(self, request, pk):
        try:
            obj = self.get_object(request, pk)
            api = DjAdminManager()
            api.delete_user(obj.custom_fields["kobo_username"], obj.custom_fields["kobo_pk"])
            obj.custom_fields["kobo_username"] = None
            obj.custom_fields["kobo_pk"] = None
            obj.save()
            self.message_user(
                request,
                f"Kobo Access removed from {settings.KOBO_KF_URL}",
                messages.WARNING,
            )
        except Exception as e:
            logger.exception(e)
            self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)

    @button(label="Import CSV", permission="account.can_upload_to_kobo")
    def import_csv(self, request):
        from django.contrib.admin.helpers import AdminForm

        context = self.get_common_context(request, processed=False)
        if request.method == "GET":
            form = ImportCSVForm(initial={"partner": Partner.objects.first()})
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
                                        IncompatibleRoles.objects.validate_user_role(u, business_area, role)
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
        context["adminform"] = AdminForm(form, fieldsets=fs, prepopulated_fields={})
        return TemplateResponse(request, "admin/account/user/import_csv.html", context)

    @button(label="Sync users from Kobo", permission="account.can_import_from_kobo")
    def kobo_users_sync(self, request):
        ctx = self.get_common_context(request)
        users = []
        if request.method == "POST":
            selected = request.POST.getlist("kobo_id")
            api = DjAdminManager()
            api.login(request)
            results = []
            for entry in api.list_users():
                if entry[0] in selected:
                    local, created = account_models.User.objects.get_or_create(
                        email=entry[2],
                        defaults={
                            "username": entry[1],
                            "custom_fields": {
                                "kobo_pk": entry[0],
                                "kobo_username": entry[1],
                            },
                        },
                    )
                    local.custom_fields["kobo_pk"] = entry[0]
                    local.custom_fields["kobo_username"] = entry[1]
                    local.save()
                    results.append([local, created])
            ctx["results"] = results
        else:
            try:
                api = DjAdminManager()
                api.login(request)
                for entry in api.list_users():
                    local = account_models.User.objects.filter(email=entry[2]).first()
                    if entry[1] not in ["__sys__", "superuser"]:
                        users.append([entry[0], entry[1], entry[2], local])
                ctx["users"] = users

            except Exception as e:
                logger.exception(e)
                self.message_user(request, str(e), messages.ERROR)
        return TemplateResponse(request, "admin/kobo_users.html", ctx)

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)

    def _sync_ad_data(self, user):
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
    def sync_multi(self, request):
        not_found = []
        try:
            for user in account_models.User.objects.all():
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
            logger.exception(e)
            self.message_user(request, str(e), messages.ERROR)

    @button(label="Sync", permission="account.can_sync_with_ad")
    def sync_single(self, request, pk):
        try:
            self._sync_ad_data(self.get_object(request, pk))
            self.message_user(request, "Active Directory data successfully fetched", messages.SUCCESS)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, str(e), messages.ERROR)

    @button(permission="account.can_load_from_ad")
    def load_ad_users(self, request):
        from hct_mis_api.apps.account.forms import LoadUsersForm

        ctx = self.get_common_context(
            request,
            None,
            **{
                "change": True,
                "is_popup": False,
                "save_as": False,
                "has_delete_permission": False,
                "has_add_permission": False,
                "has_change_permission": True,
            },
        )
        if request.method == "POST":
            form = LoadUsersForm(request.POST)
            if form.is_valid():
                emails = set(form.cleaned_data["emails"].split())
                role = form.cleaned_data["role"]
                business_area = form.cleaned_data["business_area"]
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
                                user = account_models.User(**user_args)
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
                                        account_models.UserRole(
                                            business_area=global_business_area,
                                            user=user,
                                            role=basic_role,
                                        )
                                    )
                                results.created.append(user)

                            users_role_to_bulk_create.append(
                                account_models.UserRole(role=role, business_area=business_area, user=user)
                            )
                        except HTTPError as e:
                            if e.response.status_code != 404:
                                raise
                            results.missing.append(email)
                        except Http404:
                            results.missing.append(email)
                    account_models.User.objects.bulk_create(users_to_bulk_create)
                    account_models.UserRole.objects.bulk_create(users_role_to_bulk_create, ignore_conflicts=True)
                    ctx["results"] = results
                    return TemplateResponse(request, "admin/load_users.html", ctx)
                except Exception as e:
                    logger.exception(e)
                    self.message_user(request, str(e), messages.ERROR)
        else:
            form = LoadUsersForm()
        ctx["form"] = form
        return TemplateResponse(request, "admin/load_users.html", ctx)


class PermissionFilter(SimpleListFilter):
    title = "Permission Name"
    parameter_name = "perm"
    template = "adminfilters/combobox.html"

    def lookups(self, request, model_admin):
        return Permissions.choices()

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(permissions__contains=[self.value()])


class RoleResource(resources.ModelResource):
    class Meta:
        model = account_models.Role
        fields = ("name", "subsystem", "permissions")
        import_id_fields = ("name", "subsystem")


@admin.register(account_models.Role)
class RoleAdmin(ImportExportModelAdmin, SyncMixin, HOPEModelAdminBase):
    list_display = ("name", "subsystem")
    search_fields = ("name",)
    form = RoleAdminForm
    list_filter = (PermissionFilter, "subsystem")
    resource_class = RoleResource
    change_list_template = "admin/account/role/change_list.html"

    @button()
    def members(self, request, pk):
        url = reverse("admin:account_userrole_changelist")
        return HttpResponseRedirect(f"{url}?role__id__exact={pk}")

    @button()
    def matrix(self, request):
        ctx = self.get_common_context(request, action="Matrix")
        matrix1 = {}
        matrix2 = {}
        perms = sorted(str(x.value) for x in Permissions)
        roles = account_models.Role.objects.order_by("name").filter(subsystem="HOPE")
        for perm in perms:
            granted_to_roles = []
            for role in roles:
                if role.permissions and perm in role.permissions:
                    granted_to_roles.append("X")
                else:
                    granted_to_roles.append("")
            matrix1[perm] = granted_to_roles

        for role in roles:
            values = []
            for perm in perms:
                if role.permissions and perm in role.permissions:
                    values.append("X")
                else:
                    values.append("")
            matrix2[role.name] = values

        ctx["permissions"] = perms
        ctx["roles"] = roles.values_list("name", flat=True)
        ctx["matrix1"] = matrix1
        ctx["matrix2"] = matrix2
        return TemplateResponse(request, "admin/account/role/matrix.html", ctx)

    def _perms(self, request, object_id) -> set:
        return set(self.get_object(request, object_id).permissions or [])

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if object_id:
            self.existing_perms = self._perms(request, object_id)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def construct_change_message(self, request, form, formsets, add=False):
        change_message = construct_change_message(form, formsets, add)
        if not add and "permissions" in form.changed_data:
            new_perms = self._perms(request, form.instance.id)
            change_message[0]["changed"]["permissions"] = {
                "added": sorted(new_perms.difference(self.existing_perms)),
                "removed": sorted(self.existing_perms.difference(new_perms)),
            }
        return change_message


@admin.register(account_models.UserRole)
class UserRoleAdmin(GetManyFromRemoteMixin, HOPEModelAdminBase):
    list_display = ("user", "role", "business_area")
    form = UserRoleAdminForm
    autocomplete_fields = ("role",)
    raw_id_fields = ("user", "business_area", "role")
    search_fields = ("user__username__istartswith",)
    list_filter = (
        ("business_area", AutoCompleteFilter),
        ("role", AutoCompleteFilter),
        ("role__subsystem", AllValuesComboFilter),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "business_area",
                "user",
                "role",
            )
        )

    def check_sync_permission(self, request, obj=None):
        return request.user.is_staff

    def check_publish_permission(self, request, obj=None):
        return False

    def _get_data(self, record) -> str:
        roles = Role.objects.all()
        collector = ForeignKeysCollector(None)
        objs = []
        for qs in [roles]:
            objs.extend(qs)
        objs.extend(account_models.UserRole.objects.filter(pk=record.pk))
        collector.collect(objs)
        serializer = self.get_serializer("json")
        return serializer.serialize(
            collector.data, use_natural_foreign_keys=True, use_natural_primary_keys=True, indent=3
        )


class IncompatibleRoleFilter(SimpleListFilter):
    template = "adminfilters/combobox.html"
    title = "Role"
    parameter_name = "role"

    def lookups(self, request, model_admin):
        types = account_models.Role.objects.values_list("id", "name")
        return list(types.order_by("name").distinct())

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        try:
            return queryset.filter(
                Q(role_one=self.value()) | Q(role_two=self.value()),
            )
        except (ValueError, ValidationError) as e:
            logger.exception(e)
            raise IncorrectLookupParameters(e)


@admin.register(account_models.IncompatibleRoles)
class IncompatibleRolesAdmin(HOPEModelAdminBase):
    list_display = ("role_one", "role_two")
    list_filter = (IncompatibleRoleFilter,)


class GroupResource(resources.ModelResource):
    permissions = fields.Field(widget=ManyToManyWidget(Permission, field="codename"), attribute="permissions")

    class Meta:
        model = Group
        fields = ("name", "permissions")
        import_id_fields = ("name",)


@smart_register(Group)
class GroupAdmin(ImportExportModelAdmin, SyncMixin, HopeModelAdminMixin, _GroupAdmin):
    resource_class = GroupResource
    change_list_template = "admin/account/group/change_list.html"

    @button(permission=lambda request, group: request.user.is_superuser)
    def import_fixture(self, request):
        from adminactions.helpers import import_fixture as _import_fixture

        return _import_fixture(self, request)

    def _perms(self, request, object_id) -> set:
        return set(self.get_object(request, object_id).permissions.values_list("codename", flat=True))

    @button()
    def users(self, request, pk):
        User = get_user_model()
        context = self.get_common_context(request, pk, aeu_groups=["1"])
        group = context["original"]
        users = User.objects.filter(groups=group).distinct()
        context["title"] = _('Users in group "{}"').format(group.name)
        context["user_opts"] = User._meta
        context["data"] = users
        return render(request, "admin/account/group/members.html", context)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if object_id:
            self.existing_perms = self._perms(request, object_id)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def construct_change_message(self, request, form, formsets, add=False):
        change_message = construct_change_message(form, formsets, add)
        if not add and "permissions" in form.changed_data:
            new_perms = self._perms(request, form.instance.id)
            change_message[0]["changed"]["permissions"] = {
                "added": sorted(new_perms.difference(self.existing_perms)),
                "removed": sorted(self.existing_perms.difference(new_perms)),
            }
        return change_message


@admin.register(account_models.UserGroup)
class UserGroupAdmin(GetManyFromRemoteMixin, HOPEModelAdminBase):
    list_display = ("user", "group", "business_area")
    autocomplete_fields = ("group",)
    raw_id_fields = ("user", "business_area", "group")
    search_fields = ("user__username__istartswith",)
    list_filter = (
        ("business_area", AutoCompleteFilter),
        ("group", AutoCompleteFilter),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "business_area",
                "user",
                "group",
            )
        )

    def check_sync_permission(self, request, obj=None):
        return request.user.is_staff

    def check_publish_permission(self, request, obj=None):
        return False

    def _get_data(self, record) -> str:
        groups = Group.objects.all()
        collector = ForeignKeysCollector(None)
        objs = []
        for qs in [groups]:
            objs.extend(qs)
        objs.extend(account_models.UserGroup.objects.filter(pk=record.pk))
        collector.collect(objs)
        serializer = self.get_serializer("json")
        return serializer.serialize(
            collector.data, use_natural_foreign_keys=True, use_natural_primary_keys=True, indent=3
        )
