from typing import Any, Dict, Optional

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet

from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.models import Program


class StorageFileForm(forms.Form):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.fields["business_area"] = forms.ModelChoiceField(queryset=self.get_business_area_queryset())

        self.fields["file"] = forms.FileField(label="Select a file")

    def get_business_area_queryset(self) -> QuerySet[BusinessArea]:
        return BusinessArea.objects.filter(id__in=self.user.user_roles.all().values_list("business_area_id", flat=True))

    def clean(self, *args: Any, **kwargs: Any) -> Optional[Dict[str, Any]]:
        cleaned_data = super().clean()
        limit = settings.MAX_STORAGE_FILE_SIZE * 1024 * 1024
        if self.cleaned_data["file"].size > limit:
            raise ValidationError(f"File too large. Size should not exceed {limit} MiB.")
        return cleaned_data


class ProgramForm(forms.Form):
    name = forms.CharField(max_length=255, label="RDI name")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.business_area_id = kwargs.pop("business_area_id")
        super().__init__(*args, **kwargs)

        self.fields["program"] = forms.ModelChoiceField(queryset=self.get_program_queryset())

    def get_program_queryset(self) -> QuerySet[Program]:
        return Program.objects.filter(Q(business_area_id=self.business_area_id) & Q(status=Program.ACTIVE))


class DataCollectingTypeForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["type"].required = True

    class Meta:
        model = DataCollectingType
        fields = "__all__"

    def clean(self) -> None:
        household_filters_available = self.cleaned_data["household_filters_available"]

        if self.cleaned_data.get("type") == DataCollectingType.Type.SOCIAL and household_filters_available is True:
            msg = "Household filters cannot be applied for data collecting type with social type"
            self.add_error("type", forms.ValidationError(msg))
