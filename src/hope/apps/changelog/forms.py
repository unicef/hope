from django import forms

from hope.models.changelog import Changelog


class ChangelogForm(forms.ModelForm):
    class Meta:
        model = Changelog
        fields = [
            "description",
            "version",
            "active",
        ]
