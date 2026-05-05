from datetime import timedelta
from typing import Any, cast

from admin_extra_buttons.buttons import StandardButton
from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.core.celery_tasks import (
    DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MAX_AGE_SECONDS,
    DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MIN_AGE_SECONDS,
    requeue_async_job,
)
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


class MissingListFilter(admin.SimpleListFilter):
    title = "missing in Celery, recovery candidates"
    parameter_name = "missing_age"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin[Any]
    ) -> tuple[tuple[str, str], tuple[str, str], tuple[str, str]]:
        return (
            ("4_12", "Queued 4-12h ago, status missing"),
            ("12_24", "Queued 12-24h ago, status missing"),
            ("24_72", "Queued 24-72h ago, status missing"),
        )

    def queryset(self, request: HttpRequest, queryset: QuerySet[AsyncJob]) -> QuerySet[AsyncJob]:
        now = timezone.now()
        value = self.value()
        if value == "4_12":
            newest_allowed = now - timedelta(seconds=DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MIN_AGE_SECONDS)
            oldest_allowed = now - timedelta(seconds=DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MAX_AGE_SECONDS)
        elif value == "12_24":
            newest_allowed = now - timedelta(hours=12)
            oldest_allowed = now - timedelta(hours=24)
        elif value == "24_72":
            newest_allowed = now - timedelta(hours=24)
            oldest_allowed = now - timedelta(hours=72)
        else:
            return queryset

        candidates = queryset.filter(
            curr_async_result_id__isnull=False,
            datetime_queued__isnull=False,
            datetime_queued__gte=oldest_allowed,
            datetime_queued__lte=newest_allowed,
        )
        missing_ids = [job.pk for job in candidates if job.task_status == job.MISSING]
        return queryset.filter(pk__in=missing_ids)


def is_missing(btn: StandardButton) -> bool:
    job = btn.original
    return bool(job and job.task_status == job.MISSING)


class BaseAsyncJobAdmin(HOPEModelAdminBase):
    list_display = (
        "id",
        "job_name",
        "type",
        "task_status_display",
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
        MissingListFilter,
        "repeatable",
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
        return cast(
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
                "group_key",
                "sentry_id",
            ),
        )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return False

    @button(label="Recover If Missing", enabled=is_missing, permission="core.recover_missing_async_job")
    def recover_missing(self, request: HttpRequest, pk: str) -> Any:
        job = cast("AsyncJob | PeriodicAsyncJob | None", self.get_object(request, pk))
        if job is None:
            self.message_user(request, "Async job not found", messages.ERROR)
            return redirect(reverse(f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist"))

        if job.task_status != job.MISSING:
            self.message_user(request, f"Async job is not missing. Current status: {job.task_status}", messages.INFO)
            return redirect(
                reverse(
                    f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                    args=[job.pk],
                )
            )
        if not job.repeatable:
            self.message_user(request, "Async job is not repeatable and cannot be requeued", messages.ERROR)
            return redirect(
                reverse(
                    f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                    args=[job.pk],
                )
            )
        if requeue_async_job(job):
            self.message_user(request, "Async job was requeued", messages.SUCCESS)
        else:
            self.message_user(request, "Async job requeue failed", messages.ERROR)
        return redirect(
            reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                args=[job.pk],
            )
        )


@admin.register(AsyncJob)
class AsyncJobAdmin(BaseAsyncJobAdmin):
    pass


@admin.register(PeriodicAsyncJob)
class PeriodicAsyncJobAdmin(BaseAsyncJobAdmin):
    pass
