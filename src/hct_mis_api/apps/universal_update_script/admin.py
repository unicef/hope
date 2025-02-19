from typing import Any, Iterator, Tuple

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.postgres.forms import SimpleArrayField
from django.db.models import QuerySet
from django.http import HttpRequest

from admin_extra_buttons.decorators import button

from hct_mis_api.apps.universal_update_script.celery_tasks import (
    generate_universal_individual_update_template,
    run_universal_individual_update,
)
from hct_mis_api.apps.universal_update_script.models import (
    DeliveryMechanism,
    DocumentType,
    UniversalUpdate,
)
from hct_mis_api.apps.universal_update_script.universal_individual_update_service.all_updatable_fields import (
    get_individual_flex_fields,
    household_fields,
    individual_fields,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


class ArrayFieldFilteredSelectMultiple(FilteredSelectMultiple):
    def format_value(self, value: str) -> list[str]:  # type: ignore
        """Return selected values as a list."""
        processed_value = []
        if value is None and self.allow_multiple_selected:
            return []
        elif self.allow_multiple_selected:
            processed_value = [v for v in value.split(",")]

        if not isinstance(value, (tuple, list)):
            processed_value = [value]

        results = [str(v) if v is not None else "" for v in processed_value]
        return results


class UniversalUpdateAdminForm(forms.ModelForm):
    individual_fields = SimpleArrayField(
        base_field=forms.CharField(max_length=255),  # type: ignore
        widget=ArrayFieldFilteredSelectMultiple("Individual Fields", is_stacked=False),
        required=False,
    )
    individual_flex_fields_fields = SimpleArrayField(
        base_field=forms.CharField(max_length=255),  # type: ignore
        widget=ArrayFieldFilteredSelectMultiple("Individual Flex Fields", is_stacked=False),
        required=False,
    )
    household_fields = SimpleArrayField(
        base_field=forms.CharField(max_length=255),  # type: ignore
        widget=ArrayFieldFilteredSelectMultiple("Household Fields", is_stacked=False),
        required=False,
    )

    class Meta:
        model = UniversalUpdate
        fields = "__all__"
        widgets = {
            "document_types": FilteredSelectMultiple("Document Types", is_stacked=False),
            "delivery_mechanisms": FilteredSelectMultiple("Delivery Mechanisms", is_stacked=False),
        }

    def __init__(self, *args: list[Any], **kwargs: dict[Any, Any]) -> None:
        super().__init__(*args, **kwargs)  # type: ignore
        self.fields["individual_fields"].widget.choices = list(self.get_dynamic_individual_fields_choices())
        self.fields["individual_flex_fields_fields"].widget.choices = list(
            self.get_dynamic_individual_flex_fields_choices()
        )
        self.fields["household_fields"].widget.choices = list(self.get_dynamic_household_fields_choices())
        self.fields["document_types"].queryset = self.get_dynamic_document_types_queryset()
        self.fields["delivery_mechanisms"].queryset = self.get_dynamic_delivery_mechanisms_queryset()

    def get_dynamic_individual_fields_choices(self) -> Iterator[Tuple[str, str]]:
        for field_data in individual_fields.values():
            yield (field_data[0], field_data[0])

    def get_dynamic_individual_flex_fields_choices(self) -> Iterator[Tuple[str, str]]:
        for field_data in get_individual_flex_fields().values():
            yield (field_data[0], field_data[0])

    def get_dynamic_household_fields_choices(self) -> Iterator[Tuple[str, str]]:
        for field_data in household_fields.values():
            yield (field_data[0], field_data[0])

    def get_dynamic_document_types_queryset(self) -> QuerySet[DocumentType]:
        return DocumentType.objects.all()

    def get_dynamic_delivery_mechanisms_queryset(self) -> QuerySet[DeliveryMechanism]:
        return DeliveryMechanism.objects.all()


@admin.register(UniversalUpdate)
class UniversalUpdateAdmin(HOPEModelAdminBase):
    form = UniversalUpdateAdminForm
    filter_horizontal = (
        "document_types",
        "delivery_mechanisms",
    )
    autocomplete_fields = ("program",)
    list_display = ("id", "program", "update_file", "created_at", "updated_at")
    readonly_fields = (
        "saved_logs",
        "logs_property",
        "backup_snapshot",
        "task_status",
        "template_file",
        "curr_async_result_id",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "program",
                    "template_file",
                    "update_file",
                    "unicef_ids",
                    "task_status",
                    "curr_async_result_id",
                ),
            },
        ),
        (
            "Field Configuration",
            {
                "fields": (
                    "individual_fields",
                    "individual_flex_fields_fields",
                    "household_fields",
                    "document_types",
                    "delivery_mechanisms",
                ),
            },
        ),
        (
            "Logs",
            {
                "fields": ("logs_property", "saved_logs"),
            },
        ),
        (
            "Backup",
            {
                "fields": ("backup_snapshot",),
            },
        ),
    )

    def logs_property(self, obj: UniversalUpdate) -> str:
        return obj.logs or "-"

    logs_property.short_description = "Live Logs"

    def task_status(self, obj: UniversalUpdate) -> str:
        return obj.celery_status or "-"

    task_status.short_description = "Task Status"

    @button(label="Generate Excel Template")
    def generate_xlsx_template(self, request: HttpRequest, pk: str) -> None:
        universal_update = self.get_object(request, pk)
        universal_update.queue(generate_universal_individual_update_template)
        self.message_user(request, "Gnerating Excel Template Task Scheduled")
        return None

    @button(label="Start Universal Update Task")
    def start_universal_update_task(self, request: HttpRequest, pk: str) -> None:
        universal_update = self.get_object(request, pk)
        universal_update.queue(run_universal_individual_update)
        self.message_user(request, "Universal individual update task scheduled")
        return None
