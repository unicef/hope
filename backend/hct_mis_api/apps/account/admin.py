from admin_extra_urls.extras import ExtraUrlMixin, link
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms.models import BaseInlineFormSet, ModelForm
from django.forms.utils import ErrorList
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from requests import HTTPError

from account.microsoft_graph import MicrosoftGraphAPI, DJANGO_USER_MAP
from account.models import User, UserRole, Role, IncompatibleRoles
from core.models import BusinessArea
from core.utils import build_arg_dict_from_dict


class UserRoleAdminForm(ModelForm):
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
            raise ValidationError(
                {
                    "role": _(
                        f"This role is incompatible with {', '.join([userrole.role.name for userrole in incompatible_userroles])}"
                    )
                }
            )


class UserRoleInlineFormSet(BaseInlineFormSet):
    model = UserRole

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


@admin.register(User)
class UserAdmin(ExtraUrlMixin, BaseUserAdmin):

    list_display = ("username", "email", "first_name", "last_name", "status")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "email")},
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
    )
    inlines = (UserRoleInline,)

    @link()
    def load_ad_users(self, request):
        from account.forms import LoadUsersForm

        opts = self.model._meta
        ctx = {
            "opts": opts,
            "app_label": "account",
            "change": True,
            "is_popup": False,
            "save_as": False,
            "has_delete_permission": False,
            "has_add_permission": False,
            "has_change_permission": True,
        }
        if request.method == "POST":
            form = LoadUsersForm(request.POST)
            error = False
            if form.is_valid():
                emails = form.cleaned_data["emails"].split()
                role_id = form.cleaned_data["role"]
                role = Role.objects.get(id=role_id)
                business_area_id = form.cleaned_data["business_area"]
                business_area = BusinessArea.objects.get(id=business_area_id)
                users_to_bulk_create = []
                users_role_to_bulk_create = []
                ms_graph = MicrosoftGraphAPI()
                users = User.objects.filter(email__in=emails)
                emails = list(set(emails))
                for user in users:
                    emails.remove(user.email)
                for email in emails:
                    try:
                        validate_email(email)
                        user_data = ms_graph.get_user_data(email)
                        user_args = build_arg_dict_from_dict(user_data, DJANGO_USER_MAP)
                        user = User(**user_args)
                        if user.first_name is None:
                            user.first_name = ""
                        if user.last_name is None:
                            user.last_name = ""
                        user.set_unusable_password()
                        users_to_bulk_create.append(user)
                        users_role_to_bulk_create.append(UserRole(role=role, business_area=business_area, user=user))
                    except ValidationError:
                        error = True
                        message = _(f"{email} is not a valid email address.")
                        form.add_error("emails", message)
                    except HTTPError as e:
                        error = True
                        if e.response.status_code != 404:
                            raise
                        message = _(f"{email} does not exist in the Unicef Active Directory")
                        form.add_error("emails", message)
                    except Http404:
                        error = True
                        message = _(f"{email} does not exist in the Unicef Active Directory")
                        form.add_error("emails", message)

                if not error:
                    User.objects.bulk_create(users_to_bulk_create)
                    UserRole.objects.bulk_create(users_role_to_bulk_create)
                    messages_added_list = [
                        f"<a href='/api/admin/account/user/{user.id}/change/'>{user.email}</a> has been imported from AD"
                        for user in users_to_bulk_create
                    ]
                    messages_already_exist_list = [
                        f"<a href='/api/admin/account/user/{user.id}/change/'>{user.email}</a> already exists in HOPE database"
                        for user in users
                    ]
                    for message in messages_added_list:
                        messages.success(request, mark_safe(message))
                    for message in messages_already_exist_list:
                        messages.warning(request, mark_safe(message))
                    return redirect("/api/admin/account/user/")

        else:
            form = LoadUsersForm()
        ctx["form"] = form
        return TemplateResponse(request, "admin/load_users.html", ctx)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "business_area")
    form = UserRoleAdminForm


@admin.register(IncompatibleRoles)
class IncompatibleRolesAdmin(admin.ModelAdmin):
    pass
