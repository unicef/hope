from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from adminfilters.combo import ChoicesFieldComboFilter
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.periodic_data_update.models import (
    PDUXlsxTemplate,
    PDUXlsxUpload,
    PDUOnlineEdit,
)


class PDUXlsxUploadInline(admin.TabularInline):
    model = PDUXlsxUpload
    extra = 0
    show_change_link = True
    can_add = False
    fields = ("id", "status", "created_by", "created_at")
    readonly_fields = fields

    def has_add_permission(self, request: HttpRequest, obj: PDUXlsxUpload | None = None) -> bool:
        return False


@admin.register(PDUXlsxTemplate)
class PDUXlsxTemplateAdmin(HOPEModelAdminBase):
    list_display = (
        "id",
        "status",
        "business_area",
        "program",
        "created_by",
        "created_at",
    )
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
    inlines = [PDUXlsxUploadInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("created_by", "program", "business_area")

    def task_status(self, obj: PDUXlsxTemplate) -> str:
        return obj.celery_statuses.get("export")

    def celery_task_result_id(self, obj: PDUXlsxTemplate) -> str:
        return obj.celery_tasks_results_ids.get("export")


@admin.register(PDUXlsxUpload)
class PDUXlsxUploadAdmin(HOPEModelAdminBase):
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

    def task_status(self, obj: PDUXlsxTemplate) -> str:
        return obj.celery_statuses.get("import")

    def celery_task_result_id(self, obj: PDUXlsxTemplate) -> str:
        return obj.celery_tasks_results_ids.get("import")


@admin.register(PDUOnlineEdit)
class PDUOnlineEditAdmin(HOPEModelAdminBase):
    list_display = ("id", "status", "business_area", "program", "created_by", "created_at")
    filter_horizontal = ("authorized_users",)
    list_filter = (
        ("business_area", LinkedAutoCompleteFilter.factory(parent=None)),
        ("program", LinkedAutoCompleteFilter.factory(parent="business_area")),
        ("status", ChoicesFieldComboFilter),
        ("created_by", AutoCompleteFilter),
    )
    readonly_fields = (
        "task_statuses",
        "celery_tasks_results_ids",
    )
    raw_id_fields = ("program", "business_area", "created_by")

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("created_by", "program", "business_area")

    def task_statuses(self, obj: PDUOnlineEdit) -> dict:
        return obj.celery_statuses
