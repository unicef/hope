from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.template.response import TemplateResponse

from account.models import User, UserRole
from admin_extra_urls.extras import action, ExtraUrlMixin, link
from account.models import User, UserRole, Role

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


class LoadUsersForm(forms.Form):
    emails = forms.CharField(widget=forms.Textarea)


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ("username", "email", "first_name")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "business_areas")},),
        (_("Permissions"), {"fields": ( "is_active", "is_staff", "is_superuser",),},),
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
            if form.is_valid():
                emails = form.cleaned_data["emails"].split()
                for email in emails:
                    try:
                        validate_email(email)
                        # TODO: ms graph fetch user and if exists create in HOPE
                    except ValidationError:
                        message = _(f"{email} is not a valid email address.")
                        form.add_error("emails", message)

        else:
            form = LoadUsersForm()
        ctx["form"] = form
        return TemplateResponse(request, "admin/load_users.html", ctx)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user","role", "business_area")
