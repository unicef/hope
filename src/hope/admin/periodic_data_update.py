from typing import TYPE_CHECKING

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import confirm_action
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from adminfilters.combo import ChoicesFieldComboFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.periodic_data_update.celery_tasks import export_periodic_data_update_export_template_service_async_task
from hope.models import PDUOnlineEdit, PDUXlsxTemplate, PDUXlsxUpload

if TYPE_CHECKING:  # pragma: no cover
    from uuid import UUID


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
    inlines = [PDUXlsxUploadInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("created_by", "program", "business_area")

    def task_status(self, obj: PDUXlsxTemplate) -> str:
        job = (
            obj.async_jobs.filter(job_name=PDUXlsxTemplate.EXPORT_JOB_NAME).order_by("-datetime_created", "-pk").first()
        )
        return job.task_status if job else PDUXlsxTemplate.CELERY_STATUS_NOT_SCHEDULED

    def celery_task_result_id(self, obj: PDUXlsxTemplate) -> str:
        job = (
            obj.async_jobs.filter(job_name=PDUXlsxTemplate.EXPORT_JOB_NAME).order_by("-datetime_created", "-pk").first()
        )
        return job.curr_async_result_id if job and job.curr_async_result_id else ""

    @button(
        visible=lambda btn: btn.original.status == PDUXlsxTemplate.Status.FAILED,
        permission="periodic_data_update.restart_export_task",
    )
    def restart_export_task(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        if request.method == "POST":
            periodic_data_update_template = PDUXlsxTemplate.objects.get(pk=pk)
            export_periodic_data_update_export_template_service_async_task(periodic_data_update_template)
            return redirect(reverse("admin:periodic_data_update_pduxlsxtemplate_change", args=[pk]))
        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.restart_export_task,
            message="Do you confirm to restart the export task?",
        )


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
        job = obj.async_jobs.filter(job_name=PDUXlsxUpload.IMPORT_JOB_NAME).order_by("-datetime_created", "-pk").first()
        return job.task_status if job else PDUXlsxUpload.CELERY_STATUS_NOT_SCHEDULED

    def celery_task_result_id(self, obj: PDUXlsxTemplate) -> str:
        job = obj.async_jobs.filter(job_name=PDUXlsxUpload.IMPORT_JOB_NAME).order_by("-datetime_created", "-pk").first()
        return job.curr_async_result_id if job and job.curr_async_result_id else ""


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

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related("created_by", "program", "business_area")

    def task_statuses(self, obj: PDUOnlineEdit) -> dict:
        return {
            job.job_name: job.task_status
            for job in obj.async_jobs.exclude(job_name=PDUOnlineEdit.SEND_NOTIFICATION_JOB_NAME)
        }

    def celery_tasks_results_ids(self, obj: PDUOnlineEdit) -> dict:
        return {
            job.job_name: job.curr_async_result_id
            for job in obj.async_jobs.exclude(job_name=PDUOnlineEdit.SEND_NOTIFICATION_JOB_NAME).exclude(
                curr_async_result_id__isnull=True
            )
        }
