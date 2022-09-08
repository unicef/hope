from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.models import BusinessArea


class StorageFileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.fields["business_area"] = forms.ModelChoiceField(
            queryset=self.get_business_area_queryset()
        )

        self.fields["file"] = forms.FileField(label="Select a file")

    def get_business_area_queryset(self):
        return BusinessArea.objects.filter(
            id__in=self.user.user_roles.all().values_list("business_area_id", flat=True)
        )

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean()
        limit = settings.MAX_STORAGE_FILE_SIZE * 1024 * 1024
        if self.cleaned_data["file"].size > limit:
            raise ValidationError(f"File too large. Size should not exceed {limit} MiB.")
        return cleaned_data
