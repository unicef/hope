from typing import Any, Iterator

from admin_extra_buttons.buttons import Button
from admin_extra_buttons.decorators import button
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.postgres.forms import SimpleArrayField
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.payment.models import AccountType
from hope.apps.universal_update_script.models import DocumentType, UniversalUpdate
from hope.apps.universal_update_script.universal_individual_update_service.all_updatable_fields import (
    get_household_flex_fields,
    get_individual_flex_fields,
    household_fields,
    individual_fields,
)


class ArrayFieldFilteredSelectMultiple(FilteredSelectMultiple):
    def format_value(self, value: str | tuple | list) -> list[str]:  # type: ignore
        """Return selected values as a list."""
        if value is None and self.allow_multiple_selected:
            return []
        if self.allow_multiple_selected:
            value = value.split(",")

        if not isinstance(value, tuple | list):
            value = [value]

        return [str(v) if v is not None else "" for v in value]


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

    household_flex_fields_fields = SimpleArrayField(
        base_field=forms.CharField(max_length=255),  # type: ignore
        widget=ArrayFieldFilteredSelectMultiple("Household Flex Fields", is_stacked=False),
        required=False,
    )
    household_fields = SimpleArrayField(
        base_field=forms.CharField(max_length=255),  # type: ignore
        widget=ArrayFieldFilteredSelectMultiple("Household Fields", is_stacked=False),
        required=False,
    )

    class Meta:
        model = UniversalUpdate
        fields = (
            "individual_fields",
            "individual_flex_fields_fields",
            "household_fields",
            "household_flex_fields_fields",
            "document_types",
            "account_types",
            "template_file",
            "update_file",
            "program",
            "backup_snapshot",
            "saved_logs",
            "unicef_ids",
        )
        widgets = {
            "document_types": FilteredSelectMultiple("Document Types", is_stacked=False),
            "account_types": FilteredSelectMultiple("Account Types", is_stacked=False),
        }

    def __init__(self, *args: list[Any], **kwargs: dict[Any, Any]) -> None:
        super().__init__(*args, **kwargs)  # type: ignore
        self.fields["individual_fields"].widget.choices = list(self.get_dynamic_individual_fields_choices())
        self.fields["individual_flex_fields_fields"].widget.choices = list(
            self.get_dynamic_individual_flex_fields_choices()
        )
        self.fields["household_flex_fields_fields"].widget.choices = list(
            self.get_dynamic_household_flex_fields_choices()
        )
        self.fields["household_fields"].widget.choices = list(self.get_dynamic_household_fields_choices())
        self.fields["document_types"].queryset = self.get_dynamic_document_types_queryset()
        self.fields["account_types"].queryset = self.get_dynamic_account_types_queryset()

    def get_dynamic_individual_fields_choices(self) -> Iterator[tuple[str, str]]:
        for field_data in individual_fields.values():
            yield (field_data[0], field_data[0])

    def get_dynamic_individual_flex_fields_choices(self) -> Iterator[tuple[str, str]]:
        for field_data in get_individual_flex_fields().values():
            yield (field_data[0], field_data[0])

    def get_dynamic_household_fields_choices(self) -> Iterator[tuple[str, str]]:
        for field_data in household_fields.values():
            yield (field_data[0], field_data[0])

    def get_dynamic_household_flex_fields_choices(self) -> Iterator[tuple[str, str]]:
        for field_data in get_household_flex_fields().values():
            yield (field_data[0], field_data[0])

    def get_dynamic_document_types_queryset(self) -> QuerySet[DocumentType]:
        return DocumentType.objects.all()

    def get_dynamic_account_types_queryset(self) -> QuerySet[AccountType]:
        return AccountType.objects.all()


@admin.register(UniversalUpdate)
class UniversalUpdateAdmin(HOPEModelAdminBase):
    form = UniversalUpdateAdminForm
    filter_horizontal = (
        "document_types",
        "account_types",
    )
    autocomplete_fields = ("program",)
    list_display = ("id", "program", "update_file", "created_at", "updated_at")
    readonly_fields = (
        "saved_logs",
        "logs_property",
        "backup_snapshot",
        "task_statuses",
        "template_file",
        "celery_tasks_results_ids",
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
                    "task_statuses",
                    "celery_tasks_results_ids",
                ),
            },
        ),
        (
            "Field Configuration",
            {
                "fields": (
                    "individual_fields",
                    "individual_flex_fields_fields",
                    "household_flex_fields_fields",
                    "household_fields",
                    "document_types",
                    "account_types",
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

    def task_statuses(self, obj: UniversalUpdate) -> dict:
        return obj.celery_statuses

    task_statuses.short_description = "Task Statuses"

    @staticmethod
    def start_universal_update_task_visible(btn: Button) -> bool:
        universal_update = get_object_or_404(UniversalUpdate, pk=btn.request.resolver_match.kwargs["object_id"])
        return bool(universal_update.update_file)

    @button(
        label="Generate Excel Template",
        permision="universal_update_script.can_generate_universal_update_template",
    )
    def generate_xlsx_template(self, request: HttpRequest, pk: str) -> None:
        universal_update = self.get_object(request, pk)
        universal_update.queue("generate_universal_individual_update_template")
        self.message_user(request, "Generating Excel Template Task Scheduled")

    @button(
        label="Start Universal Update Task",
        permision="universal_update_script.can_run_universal_update",
        visible=start_universal_update_task_visible,
        html_attrs={"style": "background-color:#44AA44;color:black"},
    )
    def start_universal_update_task(self, request: HttpRequest, pk: str) -> None:
        universal_update = self.get_object(request, pk)
        universal_update.queue("run_universal_individual_update")
        self.message_user(request, "Universal individual update task scheduled")
