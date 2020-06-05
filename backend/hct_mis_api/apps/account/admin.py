from django.contrib import admin

from account.models import User

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ("username", "email", "first_name")
