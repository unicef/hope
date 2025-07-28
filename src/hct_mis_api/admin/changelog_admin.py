from django import forms
from django.contrib import admin
from django.db import models

from hct_mis_api.apps.changelog.models import Changelog
from hct_mis_api.apps.changelog.widget import HTMLEditor
from hct_mis_api.admin.utils_admin import HOPEModelAdminBase


class ChangelogAdminForm(forms.ModelForm):
    class Meta:
        model = Changelog
        fields = "__all__"


class ChangelogAdmin(HOPEModelAdminBase):
    form = ChangelogAdminForm
    list_display = [
        "version",
        "active",
        "date",
    ]
    list_filter = ["active"]
    date_hierarchy = "date"
    formfield_overrides = {
        models.TextField: {"widget": HTMLEditor},
    }


admin.site.register(Changelog, ChangelogAdmin)
