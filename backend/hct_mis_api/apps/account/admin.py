import csv
import logging
import re
from collections import namedtuple
from functools import cached_property
from urllib.parse import unquote

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models, router, transaction
from django.db.models import Q
from django.forms import Form, ModelChoiceField, MultipleChoiceField
from django.forms.models import BaseInlineFormSet, ModelForm
from django.forms.utils import ErrorList
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

import requests
from admin_extra_urls.api import ExtraUrlMixin, button
from adminfilters.filters import (
    ChoicesFieldComboFilter,
    ForeignKeyFieldFilter,
    RelatedFieldComboFilter,
)
from constance import config
from requests import HTTPError

from hct_mis_api.apps.account.forms import KoboLoginForm
from hct_mis_api.apps.account.microsoft_graph import DJANGO_USER_MAP, MicrosoftGraphAPI
from hct_mis_api.apps.account.models import IncompatibleRoles, Role, User, UserRole
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.kobo.api import KoboAPI
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import build_arg_dict_from_dict
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase

logger = logging.getLogger(__name__)


class RoleAdminForm(ModelForm):
    permissions = MultipleChoiceField(
        required=False,
        widget=FilteredSelectMultiple("", False),
        choices=Permissions.choices(),
    )

    class Meta:
        model = UserRole
        fields = "__all__"


class UserRoleAdminForm(ModelForm):
    role = ModelChoiceField(Role.objects.order_by("name"))
    business_area = ModelChoiceField(BusinessArea.objects.filter(is_split=False))

    class Meta:
        model = UserRole
        fields = "__all__"

    def clean(self):
        super().clean()
        if not self.is_valid():
            return
        role = self.cleaned_data["role"]
        incompatible_roles = list(
            IncompatibleRoles.objects.filter(role_one=role).values_list("role_two", flat=True)
        ) + list(IncompatibleRoles.objects.filter(role_two=role).values_list("role_one", flat=True))
        incompatible_userroles = UserRole.objects.filter(
            business_area=self.cleaned_data["business_area"],
            role__id__in=incompatible_roles,
            user=self.cleaned_data["user"],
        )
        if self.instance.id:
            incompatible_userroles = incompatible_userroles.exclude(id=self.instance.id)
        if incompatible_userroles.exists():
            logger.error(
                f"This role is incompatible with {', '.join([userrole.role.name for userrole in incompatible_userroles])}"
            )
            raise ValidationError(
                {
                    "role": _(
                        f"This role is incompatible with {', '.join([userrole.role.name for userrole in incompatible_userroles])}"
                    )
                }
            )


class UserRoleInlineFormSet(BaseInlineFormSet):
    model = UserRole

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
                    IncompatibleRoles.objects.filter(role_one=role).values_list("role_two", flat=True)
                ) + list(IncompatibleRoles.objects.filter(role_two=role).values_list("role_one", flat=True))
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
    model = UserRole
    extra = 0
    formset = UserRoleInlineFormSet


KOBO_ACCESS_EMAIL = """

You have been authorised to access to HOPE/Kobo

Follow this link {kobo_url} and use below credentials:

Username:{email}
Password:{password}

The HOPE team.
"""


class DjAdminManager:
    regex = re.compile('class="errorlist"><li>(.*)(?=<\/li>)')

    class ResponseException(Exception):
        pass

    def __init__(self, kf_host=settings.KOBO_KF_URL, kc_host=settings.KOBO_KC_URL):
        self.admin_path = f"/admin/"
        self.admin_url = f"{kf_host}{self.admin_path}"
        self.login_url = f"{self.admin_url}login/"
        self._logged = False
        self._last_error = None
        self._last_response = False
        self._username = None
        self._password = None
        self.form_errors = []
        if kc_host:
            self.kc = DjAdminManager(kc_host, None)

    def extract_errors(self, res):
        self.form_errors = [msg for msg in self.regex.findall(res.content.decode())]
        return self.form_errors

    def assert_response(self, status: int, location: str = None, custom_error=None):
        if not isinstance(status, (list, tuple)):
            status = [status]
        if self._last_response.status_code not in status:
            msg = custom_error or f"Unexpected code:{self._last_response.status_code} not in {status}"
            self._last_error = self._last_response
            raise self.ResponseException(msg)

        if location and (redir_to := self._last_response.headers.get("location", "N/A")) != location:
            msg = custom_error or f"Unexpected redirect:{redir_to} <> {location}"
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

    def login(self, request=None, username="", password="", twin=None):
        if twin:
            username = twin._username
            password = twin._password
        elif not username and request:
            username = request.POST.get("kobo_username", request.session.get("kobo_username"))
            password = request.POST.get("kobo_password", request.session.get("kobo_password"))
        elif username:
            self._username = username
            self._password = password
        try:
            for client in (self, self.kc):
                try:
                    getattr(client, "_get")(client.login_url)
                    csrftoken = getattr(client, "client").cookies["csrftoken"]
                    getattr(client, "_post")(
                        client.login_url,
                        {
                            "username": username,
                            "password": password,
                            "next": client.admin_url,
                            "csrfmiddlewaretoken": csrftoken,
                        },
                    )
                    getattr(client, "assert_response")(302, client.admin_url)
                except self.ResponseException as e:
                    raise self.ResponseException(f"Unable to login to Kobo at {client.login_url}: {e}")

            if request:
                request.session["kobo_username"] = username
                request.session["kobo_password"] = password
        except Exception as e:
            logger.exception(e)
            raise

    def _get(self, url):
        self._last_response = self.client.get(url, allow_redirects=False)
        return self._last_response

    def _post(self, url, data):
        self._last_response = self.client.post(url, data, allow_redirects=False)
        return self._last_response

    def list_users(self):
        regex = re.compile(
            r"field-username.*<a.*?>(?P<username>.*)</a></t.>" r'.*field-email">(?P<mail>.*?)<',
            re.MULTILINE + re.IGNORECASE,
        )
        page = 2
        last_match = None
        while True:
            url = f"{self.admin_url}auth/user/?p={page}"
            res = self._get(url)
            self.assert_response(200)
            matches = regex.findall(res.content.decode())
            if matches[0] == last_match:
                break
            last_match = matches[0]
            for m in matches:
                yield m

            page += 1

    def delete_user(self, username, pk):
        for client in [self, self.kc]:
            url = f"{client.admin_url}auth/user/{pk}/delete/"
            getattr(client, "_get")(url)
            getattr(client, "assert_response")([200, 404, 302])
            if client._last_response.status_code == 200:
                csrftoken = getattr(client, "client").cookies["csrftoken"]
                getattr(client, "_post")(url, {"csrfmiddlewaretoken": csrftoken})
                getattr(client, "assert_response")(302)

    def create_user(self, username, password):
        self._get(f"{self.admin_url}auth/user/")
        csrftoken = self.client.cookies["csrftoken"]
        self.assert_response(200, None, "Cannot get csrftoken")
        self._post(
            f"{self.admin_url}auth/user/add/",
            data={"username": username, "password1": password, "password2": password, "csrfmiddlewaretoken": csrftoken},
        )
        if self._last_response.status_code == 200:
            self.extract_errors(self._last_response)
            self.assert_response(302, None, f"Cannot create user {username}: {self.form_errors}")

        redir_to = self._last_response.headers["location"]
        m = re.search(r"auth/user/([0-9]*)/(change/|)$", redir_to)
        pk = m.groups()[0]
        return pk


class ImportToKoboForm(forms.Form):
    file = forms.FileField()


@admin.register(User)
class UserAdmin(ExtraUrlMixin, BaseUserAdmin):
    Results = namedtuple("Result", "created,missing,updated,errors")
    list_filter = ("is_staff", "is_superuser", "is_active")
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    readonly_fields = ("ad_uuid",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": (("first_name", "last_name", "email"), "ad_uuid")},
        ),
        (
            _("Custom Fields"),
            {"fields": ("custom_fields",)},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Job Title"), {"fields": ("job_title",)}),
    )
    inlines = (UserRoleInline,)

    def import_kobo_users(self):
        pass

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
            obj: User = self.get_object(request, unquote(object_id))
            kobo_pk = obj.custom_fields.get("kobo_pk", None)
            extra_context = extra_context or {}
            try:
                api = DjAdminManager()
                api.login(request)
                extra_context["kobo_pk"] = kobo_pk
                self.message_user(request, "This action will also delete linked Kobo account", messages.WARNING)
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
    def kobo_login(self, request):
        cookies = {}
        ctx = self.get_common_context(request, logged=False)
        try:
            if request.method == "POST":
                form = KoboLoginForm(request.POST)
                if form.is_valid():
                    api = DjAdminManager()
                    api.login(
                        request,
                        username=form.cleaned_data["kobo_username"],
                        password=form.cleaned_data["kobo_password"],
                    )
                    self.message_user(request, "Successfully logged in", messages.SUCCESS)
                    ctx["logged"] = True
                else:
                    self.message_user(request, "Invalid", messages.ERROR)
            else:
                form = KoboLoginForm(
                    initial={
                        "kobo_username": request.session.get("kobo_username", request.user.email),
                        "kobo_password": request.session.get("kobo_password", ""),
                    }
                )
        except Exception as e:
            logger.exception(e)
            self.message_user(request, str(e), messages.ERROR)
        ctx["form"] = form
        response = TemplateResponse(request, "admin/kobo_login.html", ctx)
        for key, value in cookies.items():
            response.set_cookie(key, value)
        return response

    @button()
    def kobo_import(self, request):
        context = self.get_common_context(request)
        if request.method == "GET":
            form = ImportToKoboForm(initial={})
            context["form"] = form
        else:
            form = ImportToKoboForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                try:
                    csv_file = form.cleaned_data["file"]
                    if csv_file.multiple_chunks():
                        raise Exception("Uploaded file is too big (%.2f MB)" % (csv_file.size(1000 * 1000)))
                    data_set = csv_file.read().decode("utf-8-sig").splitlines()
                    reader = csv.DictReader(data_set, quoting=csv.QUOTE_NONE, delimiter=";")
                    for row in reader:
                        password = get_random_string()
                        email = row["email"].strip()
                        url = f"{settings.KOBO_KF_URL}/authorized_application/users/"
                        username = row["email"].replace("@", "_").replace(".", "_").lower()
                        results = {"errors": [], "created": []}
                        res = requests.post(
                            url,
                            headers={"Authorization": f"Token {config.KOBO_APP_API_TOKEN}"},
                            json={
                                "username": username,
                                "email": email,
                                "password": password,
                                "first_name": row["first_name"],
                                "last_name": row["last_name"],
                            },
                        )
                        if res.status_code == 201:
                            results["created"].append([username, row])
                            send_mail(
                                "Kobo credentials",
                                KOBO_ACCESS_EMAIL.format(email=email, password=password, kobo_url=settings.KOBO_KF_URL),
                                settings.DEFAULT_FROM_EMAIL,
                                [email],
                            )
                        else:
                            results["errors"].append([row, res])
                        context["results"] = results
                except Exception as e:
                    logger.exception(e)
                    context["form"] = form
                    self.message_user(request, f"{e.__class__.__name__}: {str(e)}", messages.ERROR)
            else:
                context["form"] = form

        return TemplateResponse(request, "admin/account/user/kobo_import.html", context)

    # @button(label="Sync users from Kobo")
    # def kobo_users_sync(self, request):
    #     ctx = self.get_common_context(request)
    #     users = []
    #     try:
    #         api = DjAdminManager()
    #         api.login(request)
    #         for entry in api.list_users():
    #             local = User.objects.filter(email=entry[1]).first()
    #             users.append([entry[0], entry[1], local])
    #
    #         ctx["users"] = users
    #
    #     except Exception as e:
    #         self.message_user(request, str(e), messages.ERROR)
    #     return TemplateResponse(request, "admin/kobo_users.html", ctx)
    #

    # @button(label="Bulk upload Kobo Users")
    # def kobo_bulk_create(self, request):
    #     from hct_mis_api.apps.account.forms import KoboImportUsersForm
    #
    #     cookies = {}
    #     ctx = self.get_common_context(request)
    #     api = DjAdminManager()
    #     form = None
    #     try:
    #         if request.method == "POST":
    #             form = KoboImportUsersForm(request.POST)
    #             if form.is_valid():
    #                 emails = set(form.cleaned_data["emails"].split())
    #                 api.login(request)
    #                 results = self.Results([], [], [], [])
    #                 ctx["results"] = results
    #                 for email in emails:
    #                     user, created = User.objects.get_or_create(username=email, is_active=False, email=email)
    #                     password = get_random_string()
    #                     try:
    #                         pk = api.create_user(email, password)
    #                         results.created.append((email, password))
    #                         user.custom_fields["kobo_username"] = email
    #                         user.custom_fields["kobo_pk"] = pk
    #                         user.save()
    #                         send_mail(
    #                             "Kobo credentials",
    #                             KOBO_ACCESS_EMAIL.format(email=email, password=password, kobo_url=settings.KOBO_KF_URL),
    #                             settings.DEFAULT_FROM_EMAIL,
    #                             [email],
    #                         )
    #                     except DjAdminManager.ResponseException as e:
    #                         results.errors.append((email, str(e)))
    #                 if results.errors:
    #                     self.message_user(request, "Some error occurred", messages.ERROR)
    #
    #                 ctx["results"] = results
    #             else:
    #                 self.message_user(request, "Invalid", messages.ERROR)
    #         else:
    #             api.login(request)
    #             form = KoboImportUsersForm(
    #                 initial={
    #                     "username": request.COOKIES.get("kobo_username", request.user.email),
    #                     "password": request.COOKIES.get("kobo_password", ""),
    #                     "emails": "",
    #                 }
    #             )
    #     except Exception as e:
    #         logger.exception(e)
    #         self.message_user(request, str(e), messages.ERROR)
    #     ctx["form"] = form
    #     response = TemplateResponse(request, "admin/kobo_bulk.html", ctx)
    #     for key, value in cookies.items():
    #         response.set_cookie(key, value)
    #     return response
    #

    @button()
    def privileges(self, request, pk):
        ctx = self.get_common_context(request, pk)
        return TemplateResponse(request, "admin/privileges.html", ctx)

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)

    def _sync_ad_data(self, user):
        ms_graph = MicrosoftGraphAPI()
        if user.ad_uuid:
            filters = {"uuid": user.ad_uuid}
        else:
            filters = {"email": user.email}
        user_data = ms_graph.get_user_data(**filters)
        user_args = build_arg_dict_from_dict(user_data, DJANGO_USER_MAP)
        for field, value in user_args.items():
            setattr(user, field, value or "")
        user.save()

    @button(label="Sync")
    def sync_multi(self, request):
        not_found = []
        try:
            for user in User.objects.all():
                try:
                    self._sync_ad_data(user)
                except Http404:
                    not_found.append(str(user))
            if not_found:
                self.message_user(request, f"These users were not found: {', '.join(not_found)}", messages.WARNING)
            else:
                self.message_user(request, "Active Directory data successfully fetched", messages.SUCCESS)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, str(e), messages.ERROR)

    @button(label="Sync")
    def sync_single(self, request, pk):
        try:
            self._sync_ad_data(self.get_object(request, pk))
            self.message_user(request, "Active Directory data successfully fetched", messages.SUCCESS)
        except Exception as e:
            logger.exception(e)
            self.message_user(request, str(e), messages.ERROR)

    @button()
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
                existing = set(User.objects.filter(email__in=emails).values_list("email", flat=True))
                results = self.Results([], [], [], [])
                try:
                    ms_graph = MicrosoftGraphAPI()
                    for email in emails:
                        try:
                            if email in existing:
                                user = User.objects.get(email=email)
                                self._sync_ad_data(user)
                                results.updated.append(user)
                            else:
                                user_data = ms_graph.get_user_data(email=email)
                                user_args = build_arg_dict_from_dict(user_data, DJANGO_USER_MAP)
                                user = User(**user_args)
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
                                basic_role = Role.objects.filter(name="Basic User").first()
                                if global_business_area and basic_role:
                                    users_role_to_bulk_create.append(
                                        UserRole(business_area=global_business_area, user=user, role=basic_role)
                                    )
                                results.created.append(user)

                            users_role_to_bulk_create.append(
                                UserRole(role=role, business_area=business_area, user=user)
                            )
                        except HTTPError as e:
                            if e.response.status_code != 404:
                                raise
                            results.missing.append(email)
                        except Http404:
                            results.missing.append(email)
                    User.objects.bulk_create(users_to_bulk_create)
                    UserRole.objects.bulk_create(users_role_to_bulk_create, ignore_conflicts=True)
                    ctx["results"] = results
                    return TemplateResponse(request, "admin/load_users.html", ctx)
                except Exception as e:
                    logger.exception(e)
                    self.message_user(request, str(e), messages.ERROR)
        else:
            form = LoadUsersForm()
        ctx["form"] = form
        return TemplateResponse(request, "admin/load_users.html", ctx)


@admin.register(Role)
class RoleAdmin(ExtraUrlMixin, HOPEModelAdminBase):
    list_display = ("name",)
    search_fields = ("name",)
    form = RoleAdminForm

    @button()
    def members(self, request, pk):
        url = reverse("admin:account_userrole_changelist")
        return HttpResponseRedirect(f"{url}?role__id__exact={pk}")


@admin.register(UserRole)
class UserRoleAdmin(HOPEModelAdminBase):
    list_display = ("user", "role", "business_area")
    form = UserRoleAdminForm
    raw_id_fields = ("user", "business_area")
    list_filter = (
        ForeignKeyFieldFilter.factory("user|username|istartswith", "Username"),
        ("business_area", RelatedFieldComboFilter),
        ("role", RelatedFieldComboFilter),
    )


class IncompatibleRoleFilter(SimpleListFilter):
    template = "adminfilters/fieldcombobox.html"
    title = "Role"
    parameter_name = "role"

    def lookups(self, request, model_admin):
        types = Role.objects.values_list("id", "name")
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


@admin.register(IncompatibleRoles)
class IncompatibleRolesAdmin(HOPEModelAdminBase):
    list_display = ("role_one", "role_two")
    list_filter = (IncompatibleRoleFilter,)
