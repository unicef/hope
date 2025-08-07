from django import forms

from hope.apps.changelog import models


class ChangelogForm(forms.ModelForm):
    class Meta:
        model = models.Changelog
        fields = [
            "description",
            "version",
            "active",
        ]
