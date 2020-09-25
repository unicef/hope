from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from requests import HTTPError
from django.contrib import messages


from account.microsoft_graph import MicrosoftGraphAPI, DJANGO_USER_MAP
from account.models import User, UserRole
from admin_extra_urls.extras import action, ExtraUrlMixin, link
from account.models import User, UserRole, Role

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import BusinessArea
from core.utils import build_arg_dict, build_arg_dict_from_dict


class LoadUsersForm(forms.Form):
    emails = forms.CharField(widget=forms.Textarea)
    business_area = forms.ChoiceField(choices=[(ba.id, ba.name) for ba in BusinessArea.objects.all()])
    role = forms.ChoiceField(choices=[(role.id, role.name) for role in Role.objects.all()])


@admin.register(User)
class UserAdmin(ExtraUrlMixin, BaseUserAdmin):

    list_display = ("username", "email", "first_name")
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

    @link()
    def load_ad_users(self, request):
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
