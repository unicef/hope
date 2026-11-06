from typing import Any

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet

from hope.models import BusinessArea, DataCollectingType, PayeeType, Program

DCT_ASSIGNED_TO_OTHER_PAYEE_TYPE_ERROR = "This DCT is already assigned to another Payee Type"
MIXED_DCT_TYPES_IN_PAYEE_TYPE_ERROR = "All Data Collecting Types of a Payee Type must have the same type"


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
            "collects_individual_data",
            "weight",
            "payee_type",
            "compatible_types",
            "limit_to",
        )

    def clean(self) -> None:
        household_filters_available = self.cleaned_data["household_filters_available"]
        dct = self.cleaned_data.get("type")
        self._validate_payee_type(dct)

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

    def _validate_payee_type(self, dct_type: str | None) -> None:
        payee_type = self.cleaned_data.get("payee_type")
        if payee_type is None:
            if not self.cleaned_data.get("deprecated"):
                self.add_error("payee_type", "Payee Type is required for a Data Collecting Type that is not deprecated")
        elif (
            dct_type
            and not self.cleaned_data.get("deprecated")
            and DataCollectingType.objects.filter(payee_type=payee_type)
            .exclude(pk=self.instance.pk)
            .exclude(Q(type=dct_type) | Q(type__isnull=True) | Q(deprecated=True))
            .exists()
        ):
            self.add_error("payee_type", MIXED_DCT_TYPES_IN_PAYEE_TYPE_ERROR)

        if not self.instance.pk or self.instance.payee_type_id is None:
            return
        if payee_type is not None and payee_type.pk == self.instance.payee_type_id:
            return
        if PayeeType.objects.filter(default_data_collecting_type=self.instance).exists():
            self.add_error("payee_type", "Cannot move or unassign the default Data Collecting Type of its Payee Type")
        if self.instance.payee_labels.exists():
            self.add_error(
                "payee_type", "Cannot move or unassign a Data Collecting Type that Payee Labels are restricted to"
            )
        if Program.all_objects.filter(data_collecting_type=self.instance).exists():
            self.add_error("payee_type", "Cannot move or unassign a Data Collecting Type used by programs")

    def is_valid(self) -> bool:
        # Set a flag to skip validation of type vs compatible types as they might be changed in the same form
        self.instance.skip_type_validation = True
        return super().is_valid()


class PayeeTypeForm(forms.ModelForm):
    data_collecting_types = forms.ModelMultipleChoiceField(
        queryset=DataCollectingType.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("Data Collecting Types", is_stacked=False),
    )

    class Meta:
        model = PayeeType
        fields = (
            "name",
            "gl_code",
            "description",
            "active",
            "weight",
            "data_collecting_types",
            "default_data_collecting_type",
        )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["data_collecting_types"].initial = self.instance.data_collecting_types.all()

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        selected = cleaned_data.get("data_collecting_types", DataCollectingType.objects.none())
        default_dct = cleaned_data.get("default_data_collecting_type")

        assigned_elsewhere = selected.filter(payee_type__isnull=False).exclude(payee_type=self.instance.pk)
        if assigned_elsewhere.exists():
            labels = ", ".join(assigned_elsewhere.values_list("label", flat=True))
            self.add_error("data_collecting_types", f"{DCT_ASSIGNED_TO_OTHER_PAYEE_TYPE_ERROR}: {labels}")
        typed_in_use = selected.exclude(Q(type__isnull=True) | Q(deprecated=True))
        if typed_in_use.order_by().values("type").distinct().count() > 1:
            self.add_error("data_collecting_types", MIXED_DCT_TYPES_IN_PAYEE_TYPE_ERROR)
        if self.instance.pk:
            removed = self.instance.data_collecting_types.exclude(pk__in=selected)
            restricted = removed.filter(payee_labels__isnull=False).distinct()
            if restricted.exists():
                labels = ", ".join(restricted.values_list("label", flat=True))
                self.add_error(
                    "data_collecting_types",
                    f"Cannot remove Data Collecting Types that Payee Labels are restricted to: {labels}",
                )
            used_by_programs = removed.filter(programs__isnull=False).distinct()
            if used_by_programs.exists():
                labels = ", ".join(used_by_programs.values_list("label", flat=True))
                self.add_error(
                    "data_collecting_types", f"Cannot remove Data Collecting Types used by programs: {labels}"
                )

        if default_dct and default_dct not in selected:
            self.add_error(
                "default_data_collecting_type", "Default Data Collecting Type must belong to this Payee Type"
            )
        if cleaned_data.get("active") and not default_dct:
            self.add_error("default_data_collecting_type", "Active Payee Type must have a default Data Collecting Type")
        return cleaned_data

    def _save_m2m(self) -> None:
        super()._save_m2m()
        # data_collecting_types is the reverse side of DataCollectingType.payee_type, so the FK is synced here;
        # clean() has already rejected DCTs owned elsewhere and removals of DCTs in use.
        selected = self.cleaned_data["data_collecting_types"]
        DataCollectingType.objects.filter(payee_type=self.instance).exclude(pk__in=selected).update(payee_type=None)
        DataCollectingType.objects.filter(pk__in=selected).update(payee_type=self.instance)
