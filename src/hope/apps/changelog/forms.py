from django import forms


class ChangelogForm(forms.ModelForm):
    class Meta:
        model = models.Changelog
        fields = [
            "description",
            "version",
            "active",
        ]
