from django import forms
from django.contrib import admin
from django.db import models

from hope.admin.utils import HOPEModelAdminBase
from hope.models.changelog import Changelog
from hope.apps.changelog.widget import HTMLEditor


class ChangelogAdminForm(forms.ModelForm):
    class Meta:
        model = Changelog
        fields = (
            "description",
            "version",
            "active",
            "date",
        )


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
