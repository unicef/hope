from typing import Any, cast

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from hope.admin.utils import HOPEModelAdminBase
from hope.models import AsyncJob, PeriodicAsyncJob


class HasErrorsListFilter(admin.SimpleListFilter):
    title = "has errors"
    parameter_name = "has_errors"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin[Any]
    ) -> tuple[tuple[str, str], tuple[str, str]]:
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request: HttpRequest, queryset: QuerySet[AsyncJob]) -> QuerySet[AsyncJob]:
        if self.value() == "yes":
            return queryset.exclude(errors={})
        if self.value() == "no":
            return queryset.filter(errors={})
        return queryset


class BaseAsyncJobAdmin(HOPEModelAdminBase):
    queue_name_filter: str | None = None
    exclude_queue_name: str | None = None

    list_display = (
        "id",
        "job_name",
        "type",
        "queue_name",
        "task_status_display",
        "local_status",
        "program",
        "gfk_display",
        "curr_async_result_id",
        "repeatable",
        "datetime_created",
        "datetime_queued",
    )
    list_filter = (
        ("program", AutoCompleteFilter),
        ("content_type", AutoCompleteFilter),
        ("job_name", AutoCompleteFilter),
        HasErrorsListFilter,
        "type",
        "repeatable",
        "local_status",
    )
    search_fields = (
        "job_name",
        "action",
        "program__id",
        "curr_async_result_id",
        "last_async_result_id",
        "object_id",
    )
    readonly_fields = (
        "task_status_display",
        "content_object_display",
        "id",
        "version",
        "description",
        "curr_async_result_id",
        "last_async_result_id",
        "datetime_created",
        "datetime_queued",
        "repeatable",
        "celery_history",
        "local_status",
        "queue_name",
        "owner",
        "group_key",
        "type",
        "config",
        "action",
        "sentry_id",
        "errors",
        "program",
        "content_type",
        "object_id",
        "job_name",
    )
    ordering = ("-datetime_created",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "job_name",
                    "type",
                    "task_status_display",
                    "local_status",
                    "description",
                    "action",
                    "config",
                    "errors",
                )
            },
        ),
        (
            "Relations",
            {
                "fields": (
                    "program",
                    "owner",
                    "content_type",
                    "object_id",
                    "content_object_display",
                )
            },
        ),
        (
            "Execution",
            {
                "fields": (
                    "repeatable",
                    "queue_name",
                    "group_key",
                    "curr_async_result_id",
                    "last_async_result_id",
                    "datetime_created",
                    "datetime_queued",
                    "sentry_id",
                    "celery_history",
                    "version",
                )
            },
        ),
    )

    @admin.display(description="Task status")
    def task_status_display(self, obj: AsyncJob) -> str:
        return obj.task_status

    @admin.display(description="GFK")
    def gfk_display(self, obj: AsyncJob) -> str:
        if not obj.content_type_id or not obj.object_id:
            return "-"
        return f"{obj.content_type}:{obj.object_id}"

    @admin.display(description="Content object")
    def content_object_display(self, obj: AsyncJob) -> str:
        return str(obj.content_object) if obj.content_object else "-"

    def get_queryset(self, request: HttpRequest) -> QuerySet[AsyncJob]:
        queryset = cast(
            "QuerySet[AsyncJob]",
            super()
            .get_queryset(request)
            .select_related("program", "owner", "content_type")
            .only(
                "id",
                "job_name",
                "type",
                "local_status",
                "program",
                "program__id",
                "program__name",
                "content_type",
                "content_type__app_label",
                "content_type__model",
                "object_id",
                "curr_async_result_id",
                "repeatable",
                "datetime_created",
                "datetime_queued",
                "description",
                "action",
                "config",
                "errors",
                "version",
                "last_async_result_id",
                "celery_history",
                "owner",
                "owner__id",
                "owner__username",
                "queue_name",
                "group_key",
                "sentry_id",
            ),
        )
        if self.queue_name_filter:
            queryset = queryset.filter(queue_name=self.queue_name_filter)
        if self.exclude_queue_name:
            queryset = queryset.exclude(queue_name=self.exclude_queue_name)
        return queryset

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return False


@admin.register(AsyncJob)
class AsyncJobAdmin(BaseAsyncJobAdmin):
    exclude_queue_name = PeriodicAsyncJob.celery_task_queue


@admin.register(PeriodicAsyncJob)
class PeriodicAsyncJobAdmin(BaseAsyncJobAdmin):
    queue_name_filter = PeriodicAsyncJob.celery_task_queue
