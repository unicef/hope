from django import forms

from hct_mis_api.apps.changelog import models


class ChangelogForm(forms.ModelForm):
    class Meta:
        model = models.Changelog
        fields = [
            "description",
            "version",
            "active",
        ]
