from django import forms
from django.contrib import admin
from django.db import models

from hct_mis_api.apps.changelog.models import Changelog
from hct_mis_api.apps.changelog.widget import HTMLEditor
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


class ChangelogAdminForm(forms.ModelForm):
    description = forms.CharField(widget=HTMLEditor)

    class Meta:
        model = Changelog
        fields = "__all__"


class ChangelogAdmin(HOPEModelAdminBase):
    form = ChangelogAdminForm
    list_display = [
        "description",
        "version",
        "active",
        "date",
    ]
    formfield_overrides = {
        models.TextField: {"widget": HTMLEditor(theme="snow")},
    }


admin.site.register(Changelog, ChangelogAdmin)
