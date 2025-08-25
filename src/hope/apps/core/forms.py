from typing import Any

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet

from models.core import BusinessArea, DataCollectingType
from models.program import Program


class StorageFileForm(forms.Form):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.fields["business_area"] = forms.ModelChoiceField(queryset=self.get_business_area_queryset())

        self.fields["file"] = forms.FileField(label="Select a file")

    def get_business_area_queryset(self) -> QuerySet[BusinessArea]:
        return BusinessArea.objects.filter(role_assignments__user=self.user)

    def clean(self, *args: Any, **kwargs: Any) -> dict[str, Any] | None:
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
        fields = (
            "code",
            "label",
            "type",
            "description",
            "active",
            "deprecated",
            "individual_filters_available",
            "household_filters_available",
            "recalculate_composition",
            "weight",
            "compatible_types",
            "limit_to",
        )

    def clean(self) -> None:
        household_filters_available = self.cleaned_data["household_filters_available"]
        dct = self.cleaned_data.get("type")

        # validate household filters for SOCIAL type
        if dct == DataCollectingType.Type.SOCIAL and household_filters_available is True:
            msg = "Household filters cannot be applied for data collecting type with social type"
            self.add_error("type", forms.ValidationError(msg))

        # validate compatible types against DCT's type
        compatible_dcts = self.cleaned_data.get("compatible_types")
        incompatible_dcts = compatible_dcts.exclude(Q(id=self.instance.id) | Q(type=dct))
        if incompatible_dcts.exists():
            if dct != self.instance.type:
                msg = "Type of DCT cannot be changed if it has compatible DCTs of different type"
                self.add_error("type", forms.ValidationError(msg))
            msg = (
                f"DCTs of different types cannot be compatible with each other. "
                f"Following DCTs are not of type {dct}: {list(incompatible_dcts.values_list('label', flat=True))}"
            )
            self.add_error("compatible_types", forms.ValidationError(msg))

    def is_valid(self) -> bool:
        # Set a flag to skip validation of type vs compatible types as they might be changed in the same form
        self.instance.skip_type_validation = True
        return super().is_valid()
