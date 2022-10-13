from django.contrib import admin
from django import forms
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase
from hct_mis_api.apps.changelog.models import Changelog


class ChangelogAdminForm(forms.ModelForm):
    description = forms.TextInput()

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


admin.site.register(Changelog, ChangelogAdmin)
