from django.contrib import admin

from account.models import User, UserRole

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext, gettext_lazy as _


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ("username", "email", "first_name")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "email", "business_areas")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "roles",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("name", "business_area")
