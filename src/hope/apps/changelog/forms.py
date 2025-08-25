from django import forms

from models import changelog


class ChangelogForm(forms.ModelForm):
    class Meta:
        model = models.Changelog
        fields = [
            "description",
            "version",
            "active",
        ]
