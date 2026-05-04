from datetime import timedelta
from typing import Any, cast

from admin_extra_buttons.buttons import ButtonWidget
from admin_extra_buttons.decorators import button
from adminfilters.autocomplete import AutoCompleteFilter, LinkedAutoCompleteFilter
from django.contrib import admin, messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils import timezone

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.core.celery_tasks import (
    DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MAX_AGE_SECONDS,
    DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MIN_AGE_SECONDS,
    requeue_async_job,
)
from hope.models import AsyncJob, BusinessArea, PeriodicAsyncJob, Program


def format_duration_label(seconds: int) -> str:
    total_minutes = seconds // 60
    hours, minutes = divmod(total_minutes, 60)
    if minutes:
        return f"{hours}h {minutes}m"
    return f"{hours}h"


def build_autocomplete_response(queryset: QuerySet, page_size: int = 20) -> JsonResponse:
    results = [{"id": str(obj.pk), "text": str(obj)} for obj in queryset[: page_size + 1]]
    has_more = len(results) > page_size
    return JsonResponse(
        {
            "results": results[:page_size],
            "pagination": {"more": has_more},
        }
    )


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


class UsedValuesListFilter(admin.SimpleListFilter):
    template = "adminfilters/combobox.html"

    @staticmethod
    def async_job_queryset(request: HttpRequest, model_admin: admin.ModelAdmin[Any]) -> QuerySet[AsyncJob]:
        return cast("QuerySet[AsyncJob]", model_admin.get_queryset(request))


class AsyncJobAdminAutoCompleteFilter(AutoCompleteFilter):
    autocomplete_view_name_suffix: str = ""

    def get_url(self) -> str:
        return reverse(
            f"{self.admin_site.name}:{self.model_admin.model._meta.app_label}_"
            f"{self.model_admin.model._meta.model_name}_{self.autocomplete_view_name_suffix}"
        )


class AsyncJobAdminLinkedAutoCompleteFilter(LinkedAutoCompleteFilter):
    autocomplete_view_name_suffix: str = ""

    def has_output(self) -> bool:
        if self.lookup_val:
            return True
        return super().has_output()

    def get_url(self) -> str:
        base_url = reverse(
            f"{self.admin_site.name}:{self.model_admin.model._meta.app_label}_"
            f"{self.model_admin.model._meta.model_name}_{self.autocomplete_view_name_suffix}"
        )
        parent_lookup_kwarg = cast("str | None", getattr(self, "parent_lookup_kwarg", None))
        if parent_lookup_kwarg and parent_lookup_kwarg in self.request.GET:
            flt = parent_lookup_kwarg.split("__")[-2]
            oid = self.request.GET[parent_lookup_kwarg]
            return f"{base_url}?{flt}={oid}"
        return base_url


class UsedBusinessAreaAutoCompleteFilter(AsyncJobAdminLinkedAutoCompleteFilter):
    autocomplete_view_name_suffix = "used_business_area_autocomplete"


class UsedProgramAutoCompleteFilter(AsyncJobAdminLinkedAutoCompleteFilter):
    parent = "program__business_area"  # type: ignore[assignment]
    autocomplete_view_name_suffix = "used_program_autocomplete"


class UsedContentTypeListFilter(UsedValuesListFilter):
    title = "content type"
    parameter_name = "content_type__exact"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin[Any]) -> list[tuple[str, str]]:
        used_content_type_ids = (
            self.async_job_queryset(request, model_admin)
            .exclude(content_type__isnull=True)
            .values_list("content_type_id", flat=True)
        )
        return [
            (str(content_type.pk), f"{content_type.app_label}.{content_type.model}")
            for content_type in ContentType.objects.filter(pk__in=used_content_type_ids).order_by(
                "app_label",
                "model",
            )
            if content_type.model_class() is not None
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet[AsyncJob]) -> QuerySet[AsyncJob]:
        if self.value():
            return queryset.filter(content_type_id=self.value())
        return queryset


class UsedJobNameListFilter(UsedValuesListFilter):
    title = "job name"
    parameter_name = "job_name__exact"

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin[Any]) -> list[tuple[str, str]]:
        return [
            (job_name, job_name)
            for job_name in self.async_job_queryset(request, model_admin)
            .exclude(job_name__isnull=True)
            .exclude(job_name="")
            .order_by("job_name")
            .values_list("job_name", flat=True)
            .distinct()
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet[AsyncJob]) -> QuerySet[AsyncJob]:
        if self.value():
            return queryset.filter(job_name=self.value())
        return queryset


class MissingListFilter(admin.SimpleListFilter):
    title = "missing in Celery"
    parameter_name = "missing_age"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin[Any]
    ) -> tuple[tuple[str, str], tuple[str, str], tuple[str, str]]:
        return (
            (
                "recoverable",
                (
                    "Missing jobs: queued "
                    f"{format_duration_label(DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MIN_AGE_SECONDS)}-"
                    f"{format_duration_label(DEFAULT_RECOVER_MISSING_ASYNC_JOBS_MAX_AGE_SECONDS)} ago "
                    "(auto recovery window)"
                ),
            ),
            ("12_24", "Missing jobs: queued 12-24h ago"),
            ("24_72", "Missing jobs: queued 24-72h ago"),
        )

    def queryset(self, request: HttpRequest, queryset: QuerySet[AsyncJob]) -> QuerySet[AsyncJob]:
        now = timezone.now()
        value = self.value()
        if value == "recoverable":
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


def is_missing(btn: ButtonWidget) -> bool:
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
        ("program__business_area", UsedBusinessAreaAutoCompleteFilter),
        ("program", UsedProgramAutoCompleteFilter),
        UsedContentTypeListFilter,
        UsedJobNameListFilter,
        HasErrorsListFilter,
        MissingListFilter,
        "repeatable",
    )
    search_fields = (
        "job_name",
        "action",
        "program__id",
        "program__name",
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

    def get_urls(self) -> list[Any]:
        info = self.model._meta.app_label, self.model._meta.model_name
        custom_urls = [
            path(
                "used-business-area-autocomplete/",
                self.admin_site.admin_view(self.used_business_area_autocomplete_view),
                name=f"{info[0]}_{info[1]}_used_business_area_autocomplete",
            ),
            path(
                "used-program-autocomplete/",
                self.admin_site.admin_view(self.used_program_autocomplete_view),
                name=f"{info[0]}_{info[1]}_used_program_autocomplete",
            ),
        ]
        return custom_urls + super().get_urls()

    def used_business_area_autocomplete_view(self, request: HttpRequest) -> JsonResponse:
        queryset = self.get_queryset(request)
        used_business_area_ids = queryset.exclude(program__business_area__isnull=True).values_list(
            "program__business_area_id",
            flat=True,
        )
        business_areas = BusinessArea.objects.filter(pk__in=used_business_area_ids).order_by("name")
        if term := request.GET.get("term"):
            business_areas = business_areas.filter(
                Q(name__icontains=term) | Q(slug__icontains=term) | Q(code__icontains=term)
            )
        return build_autocomplete_response(business_areas.distinct())

    def used_program_autocomplete_view(self, request: HttpRequest) -> JsonResponse:
        queryset = self.get_queryset(request)
        used_program_ids = queryset.exclude(program__isnull=True).values_list("program_id", flat=True)
        programs = Program.objects.filter(pk__in=used_program_ids).order_by("name")
        if business_area_id := request.GET.get("business_area"):
            programs = programs.filter(business_area_id=business_area_id)
        if term := request.GET.get("term"):
            programs = programs.filter(Q(name__icontains=term) | Q(code__icontains=term))
        return build_autocomplete_response(programs.distinct())

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
