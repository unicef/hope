from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from adminfilters.combo import ChoicesFieldComboFilter

from hct_mis_api.admin.utils import HOPEModelAdminBase
from hct_mis_api.apps.periodic_data_update.models import (
    PeriodicDataUpdateXlsxTemplate,
    PeriodicDataUpdateXlsxUpload,
)


class PeriodicDataUpdateUploadInline(admin.TabularInline):
    model = PeriodicDataUpdateXlsxUpload
    extra = 0
    show_change_link = True
    can_add = False
    fields = ("id", "status", "created_by", "created_at")
    readonly_fields = fields

    def has_add_permission(self, request: HttpRequest, obj: PeriodicDataUpdateXlsxUpload | None = None) -> bool:
        return False


@admin.register(PeriodicDataUpdateXlsxTemplate)
class PeriodicDataUpdateTemplateAdmin(HOPEModelAdminBase):
    list_display = ("id", "status", "business_area", "program", "created_by", "created_at")
    list_filter = (
        ("business_area", LinkedAutoCompleteFilter.factory(parent=None)),
        ("program", LinkedAutoCompleteFilter.factory(parent="business_area")),
        ("status", ChoicesFieldComboFilter),
        ("created_by", AutoCompleteFilter),
    )
    readonly_fields = (
        "task_status",
        "celery_task_result_id",
    )
    exclude = ("celery_tasks_results_ids",)
    raw_id_fields = ("file", "program", "business_area", "created_by")
    inlines = [PeriodicDataUpdateUploadInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("created_by", "program", "business_area")

    def task_status(self, obj: PeriodicDataUpdateXlsxTemplate) -> str:
        return obj.celery_statuses.get("export")

    def celery_task_result_id(self, obj: PeriodicDataUpdateXlsxTemplate) -> str:
        return obj.celery_tasks_results_ids.get("export")


@admin.register(PeriodicDataUpdateXlsxUpload)
class PeriodicDataUpdateUploadAdmin(HOPEModelAdminBase):
    list_display = ("id", "status", "template", "created_by", "created_at")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("created_by", AutoCompleteFilter),
    )
    readonly_fields = (
        "task_status",
        "celery_task_result_id",
    )
    exclude = ("celery_tasks_results_ids",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "created_by",
                "template",
            )
        )

    def task_status(self, obj: PeriodicDataUpdateXlsxTemplate) -> str:
        return obj.celery_statuses.get("import")

    def celery_task_result_id(self, obj: PeriodicDataUpdateXlsxTemplate) -> str:
        return obj.celery_tasks_results_ids.get("import")
