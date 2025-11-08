from django import forms

from hope.models import Changelog


class ChangelogForm(forms.ModelForm):
    class Meta:
        model = Changelog
        fields = [
            "description",
            "version",
            "active",
        ]
