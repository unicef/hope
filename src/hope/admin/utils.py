from typing import Any, TypeVar
from uuid import UUID

from admin_extra_buttons.buttons import StandardButton
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin, confirm_action
from adminactions.helpers import AdminActionPermMixin
from adminfilters.mixin import AdminFiltersMixin
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.contrib.admin.options import get_content_type_for_model
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model, OneToOneRel, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from jsoneditor.forms import JSONEditor
from smart_admin.mixins import DisplayAllMixin as SmartDisplayAllMixin

from hope.apps.administration.widgets import JsonWidget
from hope.apps.payment.utils import generate_cache_key
from hope.apps.utils.security import is_root
from hope.models import AsyncJob, BusinessArea, PaymentPlan


class SoftDeletableAdminMixin(admin.ModelAdmin):
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = self.model.all_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_list_filter(self, request: HttpRequest) -> tuple:
        return tuple(list(super().get_list_filter(request)) + ["is_removed"])


class RdiMergeStatusAdminMixin(admin.ModelAdmin):
    def get_list_filter(self, request: HttpRequest) -> tuple:
        return tuple(list(super().get_list_filter(request)) + ["rdi_merge_status"])


class JSONWidgetMixin:
    json_enabled = False

    def formfield_for_dbfield(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.get_internal_type() == "JSONField":
            if is_root(request) or settings.DEBUG or self.json_enabled:
                kwargs = {"widget": JSONEditor}
            else:
                kwargs = {"widget": JsonWidget}
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class LastSyncDateResetMixin:
    @button(
        permission=lambda request, obj, handler: (
            is_root(request) and request.user.has_perm(f"{handler.model_admin.model._meta.app_label}.reset_sync_date")
        )
    )
    def reset_sync_date(self, request: HttpRequest) -> HttpResponse | None:
        if request.method == "POST":
            self.get_queryset(request).update(last_sync_at=None)
        else:
            return confirm_action(
                self,
                request,
                self.reset_sync_date,
                message="Continuing will reset all records last_sync_date field.",
                success_message="Successfully executed",
                title="aaaaa",
            )
        return None

    @button(
        label="reset sync date",
        permission=lambda request, obj, handler: (
            is_root(request) and (obj is not None and request.user.has_perm(f"{obj._meta.app_label}.reset_sync_date"))
        ),
    )
    def reset_sync_date_single(self, request: HttpRequest, pk: UUID) -> HttpResponse | None:
        if request.method == "POST":
            self.get_queryset(request).filter(id=pk).update(last_sync_at=None)
        else:
            return confirm_action(
                self,
                request,
                self.reset_sync_date,
                message="Continuing will reset last_sync_date field.",
                success_message="Successfully executed",
            )
        return None


class HopeModelAdminMixin(ExtraButtonsMixin, SmartDisplayAllMixin, AdminActionPermMixin, AdminFiltersMixin):
    pass


_ModelT = TypeVar("_ModelT", bound=Model)


class AutocompleteForeignKeyMixin:
    """Automatically use autocomplete widgets for all ForeignKey (and M2M) fields.

    - Related model admin has ``search_fields`` → autocomplete widget.
    - Related model admin exists but has no ``search_fields`` → raw id widget.
    - Fields already handled by ``filter_horizontal`` / ``filter_vertical`` are
      left untouched so they keep their multi-select widget.
    """

    def _related_admin_fields(self, request: HttpRequest) -> tuple[set[str], set[str]]:
        """Return (autocomplete_fields, raw_id_fields) computed from FK/M2M relations."""
        autocomplete: set[str] = set()
        raw_id: set[str] = set()
        filter_h = set(getattr(self, "filter_horizontal", ()) or ())
        filter_v = set(getattr(self, "filter_vertical", ()) or ())
        for field in self.model._meta.get_fields():
            if field.auto_created:
                continue
            if not hasattr(field, "related_model") or not field.related_model:
                continue
            if field.one_to_many:
                continue
            if field.many_to_many and field.name in (filter_h | filter_v):
                continue
            model_admin = self.admin_site._registry.get(field.related_model)
            if model_admin is None:
                continue
            if getattr(model_admin, "search_fields", None):
                autocomplete.add(field.name)
            elif not field.many_to_many:
                # M2M without search_fields can't use raw_id_fields — skip
                raw_id.add(field.name)
        return autocomplete, raw_id

    def get_autocomplete_fields(self, request: HttpRequest) -> list[str]:
        result = set(super().get_autocomplete_fields(request))
        autocomplete, _ = self._related_admin_fields(request)
        result.update(autocomplete)
        return list(result)

    def get_raw_id_fields(self, request: HttpRequest) -> list[str]:
        result = set(getattr(self, "raw_id_fields", ()) or ())
        _, raw_id = self._related_admin_fields(request)
        result.update(raw_id)
        return list(result)


class HOPEModelAdminBase(AutocompleteForeignKeyMixin, HopeModelAdminMixin, JSONWidgetMixin, admin.ModelAdmin[_ModelT]):
    list_per_page = 50

    def get_fields(self, request: HttpRequest, obj: Any | None = None) -> Any:
        return super().get_fields(request, obj)

    def get_actions(self, request: HttpRequest) -> dict:
        actions = super().get_actions(request)
        if "delete_selected" in actions and not is_root(request):
            del actions["delete_selected"]
        return actions

    def count_queryset(self, request: HttpRequest, queryset: QuerySet) -> None:
        count = queryset.count()
        self.message_user(request, f"Selection contains {count} records")


class HUBBusinessAreaFilter(SimpleListFilter):
    parameter_name = "ba"
    title = "Business Area"
    template = "adminfilters/combobox.html"

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> list[tuple[str, str]]:
        from hope.models import BusinessArea  # pragma: no cover

        return list(BusinessArea.objects.values_list("code", "name").distinct())

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value():
            return queryset.filter(session__business_area=self.value()).distinct()
        return queryset


class BusinessAreaForCollectionsListFilter(admin.SimpleListFilter):
    model_filter_field = "households__business_area__id"
    title = "business area"
    parameter_name = "business_area__exact"
    template = "adminfilters/combobox.html"

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> list[tuple[Any, str]]:
        return list(BusinessArea.objects.all().values_list("id", "name"))

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value():
            return queryset.filter(**{self.model_filter_field: self.value()}).distinct()
        return queryset


class BusinessAreaForHouseholdCollectionListFilter(BusinessAreaForCollectionsListFilter):
    model_filter_field = "households__business_area__id"


class BusinessAreaForIndividualCollectionListFilter(BusinessAreaForCollectionsListFilter):
    model_filter_field = "individuals__business_area__id"


def is_enabled(btn: StandardButton) -> bool:
    return btn.request.user.is_superuser


def is_payment_plan_in_status(btn: StandardButton, status: str) -> bool:
    return btn.original.status == status


def is_background_action_in_status(btn: StandardButton, background_status: str) -> bool:
    return btn.original.background_action_status == background_status


def is_preparing_payment_plan(btn: StandardButton) -> bool:
    return is_payment_plan_in_status(btn, PaymentPlan.Status.OPEN)


def is_locked_payment_plan(btn: StandardButton) -> bool:
    return is_payment_plan_in_status(btn, PaymentPlan.Status.LOCKED)


def is_accepted_payment_plan(btn: StandardButton) -> bool:
    return is_payment_plan_in_status(btn, PaymentPlan.Status.ACCEPTED)


def is_importing_entitlements_xlsx_file(btn: StandardButton) -> bool:
    return is_background_action_in_status(btn, PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS)


def is_importing_reconciliation_xlsx_file(btn: StandardButton) -> bool:
    return is_background_action_in_status(btn, PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION)


def is_exporting_xlsx_file(btn: StandardButton) -> bool:
    return is_background_action_in_status(btn, PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING)


class PaymentPlanCeleryTasksMixin:
    prepare_payment_plan_async_task = "prepare_payment_plan_async_task"
    import_payment_plan_payment_list_from_xlsx_async_task = "import_payment_plan_payment_list_from_xlsx_async_task"
    import_payment_plan_payment_list_per_fsp_from_xlsx_async_task = (
        "import_payment_plan_payment_list_per_fsp_from_xlsx_async_task"
    )
    create_payment_plan_payment_list_xlsx_async_task = "create_payment_plan_payment_list_xlsx_async_task"
    create_payment_plan_payment_list_xlsx_per_fsp_async_task = (
        "create_payment_plan_payment_list_xlsx_per_fsp_async_task"
    )

    url = "admin:payment_paymentplan_change"

    def _get_active_payment_plan_jobs(self, payment_plan: PaymentPlan, task_name: str) -> list[AsyncJob]:
        jobs = AsyncJob.objects.filter(
            content_type=get_content_type_for_model(payment_plan),
            object_id=str(payment_plan.pk),
            job_name=task_name,
        ).order_by("-datetime_queued", "-pk")
        return [job for job in jobs if job.task_status in job.ACTIVE_STATUSES]

    def _terminate_active_payment_plan_jobs(self, payment_plan: PaymentPlan, task_name: str) -> bool:
        jobs = self._get_active_payment_plan_jobs(payment_plan, task_name)
        if not jobs:
            return False

        for job in jobs:
            job.terminate()
        return True

    @button(
        visible=is_preparing_payment_plan,
        enabled=is_enabled,
        permission=lambda request, obj, handler: (
            is_root(request) and request.user.has_perm("payment.restart_preparing_payment_plan")
        ),
    )
    def restart_preparing_payment_plan(self, request: HttpRequest, pk: str) -> HttpResponse | None:
        """Prepare Payment Plan."""
        from hope.apps.payment.celery_tasks import prepare_payment_plan_async_task

        payment_plan = PaymentPlan.objects.get(pk=pk)
        if payment_plan.status != PaymentPlan.Status.OPEN:
            messages.add_message(
                request,
                messages.ERROR,
                f"The Payment Plan must has the status {PaymentPlan.Status.OPEN}",
            )
            return redirect(reverse(self.url, args=[pk]))
        # check if no task in a queue
        cache_key = generate_cache_key(
            {
                "task_name": "prepare_payment_plan_async_task",
                "payment_plan_id": pk,
            }
        )
        if cache.get(cache_key):
            messages.add_message(
                request,
                messages.ERROR,
                f"Task is already running for Payment Plan {payment_plan.unicef_id}.",
            )
            return redirect(reverse(self.url, args=[pk]))

        if request.method == "POST":
            prepare_payment_plan_async_task(payment_plan)
            messages.add_message(
                request,
                messages.SUCCESS,
                f"Task restarted for Payment Plan: {payment_plan.unicef_id}",
            )

            return redirect(reverse(self.url, args=[pk]))
        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.restart_preparing_payment_plan,
            message="Do you confirm to restart preparing Payment Plan task?",
        )

    @button(
        visible=lambda btn: is_exporting_xlsx_file(btn) and is_locked_payment_plan(btn),
        enabled=is_enabled,
        permission="payment.restart_exporting_template_for_entitlement",
    )
    def restart_exporting_template_for_entitlement(self, request: HttpRequest, pk: str) -> HttpResponse | None:
        """Export template for entitlement."""
        from hope.apps.payment.celery_tasks import create_payment_plan_payment_list_xlsx_async_task

        if request.method == "POST":
            task_name = self.create_payment_plan_payment_list_xlsx_async_task
            payment_plan = PaymentPlan.objects.get(pk=pk)
            if self._terminate_active_payment_plan_jobs(payment_plan, task_name):
                create_payment_plan_payment_list_xlsx_async_task(payment_plan, str(request.user.id))
                messages.add_message(request, messages.INFO, "Successfully executed.")
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"There is no current {task_name} for this payment plan",
                )

            return redirect(reverse(self.url, args=[pk]))
        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.restart_exporting_template_for_entitlement,
            message="Do you confirm to restart exporting xlsx file task?",
        )

    @button(
        visible=lambda btn: is_importing_entitlements_xlsx_file(btn) and is_locked_payment_plan(btn),
        enabled=is_enabled,
        permission="payment.restart_importing_entitlements_xlsx_file",
    )
    def restart_importing_entitlements_xlsx_file(self, request: HttpRequest, pk: str) -> HttpResponse | None:
        """Import entitlement file."""
        from hope.apps.payment.celery_tasks import (
            import_payment_plan_payment_list_from_xlsx_async_task,
        )

        if request.method == "POST":
            task_name = self.import_payment_plan_payment_list_from_xlsx_async_task
            payment_plan = PaymentPlan.objects.get(pk=pk)
            if self._terminate_active_payment_plan_jobs(payment_plan, task_name):
                import_payment_plan_payment_list_from_xlsx_async_task(payment_plan)

                messages.add_message(request, messages.INFO, "Successfully executed.")
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"There is no current {task_name} for this payment plan",
                )

            return redirect(reverse(self.url, args=[pk]))
        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.restart_importing_entitlements_xlsx_file,
            message="Do you confirm to restart importing entitlements xlsx file task?",
        )

    @button(
        visible=lambda btn: is_exporting_xlsx_file(btn) and is_accepted_payment_plan(btn),
        enabled=is_enabled,
        permission="payment.restart_exporting_payment_plan_list",
    )
    def restart_exporting_payment_plan_list(self, request: HttpRequest, pk: str) -> HttpResponse | None:
        """Export payment plan list."""
        from hope.apps.payment.celery_tasks import (
            create_payment_plan_payment_list_xlsx_per_fsp_async_task,
        )

        if request.method == "POST":
            task_name = self.create_payment_plan_payment_list_xlsx_per_fsp_async_task
            payment_plan = PaymentPlan.objects.get(pk=pk)
            if self._terminate_active_payment_plan_jobs(payment_plan, task_name):
                create_payment_plan_payment_list_xlsx_per_fsp_async_task(payment_plan, str(request.user.id))

                messages.add_message(request, messages.INFO, "Successfully executed.")
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"There is no current {task_name} for this payment plan",
                )
            return redirect(reverse(self.url, args=[pk]))
        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.restart_exporting_payment_plan_list,
            message="Do you confirm to restart exporting xlsx file task?",
        )

    @button(
        visible=lambda btn: is_importing_reconciliation_xlsx_file(btn) and is_accepted_payment_plan(btn),
        enabled=is_enabled,
        permission="payment.restart_importing_reconciliation_xlsx_file",
    )
    def restart_importing_reconciliation_xlsx_file(self, request: HttpRequest, pk: str) -> HttpResponse | None:
        """Import payment plan list (from xlsx)."""
        from hope.apps.payment.celery_tasks import (
            import_payment_plan_payment_list_per_fsp_from_xlsx_async_task,
        )

        if request.method == "POST":
            task_name = self.import_payment_plan_payment_list_per_fsp_from_xlsx_async_task
            pp = PaymentPlan.objects.get(pk=pk)
            file = pp.reconciliation_import_file
            if not file:
                messages.add_message(
                    request, messages.ERROR, "There is no reconciliation_import_file for this payment plan"
                )
                return redirect(reverse(self.url, args=[pk]))

            if self._terminate_active_payment_plan_jobs(pp, task_name):
                import_payment_plan_payment_list_per_fsp_from_xlsx_async_task(pp)

                messages.add_message(request, messages.INFO, "Successfully executed.")
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"There is no current {task_name} for this payment plan",
                )

            return redirect(reverse(self.url, args=[pk]))
        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.restart_importing_reconciliation_xlsx_file,
            message="Do you confirm to restart importing entitlements xlsx file task?",
        )


class LinkedObjectsManagerMixin:
    """Override 'LinkedObjectsMixin' from 'smart_admin', to call overridden method 'get_related'."""

    linked_objects_template = None
    linked_objects_hide_empty = True
    linked_objects_max_records = 200
    linked_objects_ignore = []
    linked_objects_link_to_changelist = True

    def get_ignored_linked_objects(self, request: HttpRequest) -> list[str]:
        return self.linked_objects_ignore

    @button(permission=lambda request, obj, handler: request.user.has_perm(f"{obj._meta.app_label}.see_linked_objects"))
    def linked_objects(self, request: HttpRequest, pk: int) -> TemplateResponse:
        ignored = self.get_ignored_linked_objects(request)
        opts = self.model._meta
        app_label = opts.app_label
        context = self.get_common_context(request, pk, title="linked objects")
        reverse = [
            f for f in self.model._meta.get_fields() if f.auto_created and not f.concrete and f.name not in ignored
        ]
        linked = []
        empty = []
        for f in reverse:
            info = self.get_related(
                context["original"],
                f,
                "all_merge_status_objects",
                max_records=self.linked_objects_max_records,
            )
            if info["count"] == 0 and self.linked_objects_hide_empty:
                empty.append(info)
            else:
                linked.append(info)

        context["empty"] = sorted(empty, key=lambda x: x["related_name"].lower())
        context["linked"] = sorted(linked, key=lambda x: x["related_name"].lower())
        context["reverse"] = reverse

        return TemplateResponse(
            request,
            self.linked_objects_template
            or [
                f"admin/{app_label}/{opts.model_name}/linked_objects.html",
                "admin/%s/linked_objects.html" % app_label,
                "smart_admin/linked_objects.html",
            ],
            context,
        )

    def get_related(self, user: Model, field: Any, manager: str, max_records: int = 200) -> dict[str, Any]:
        """Override 'get_related' from 'smart_admin', to take related objects with a custom manager."""
        info: dict[str, Any] = {
            "owner": user,
            "to": field.model._meta.model_name,
            "field_name": field.name,
            "count": 0,
            "link": self.admin_urlbasename(field.related_model._meta, "changelist"),
            "filter": "",
        }
        try:
            info["related_name"] = field.related_model._meta.verbose_name
            if field.related_name:
                related_attr = getattr(user, field.related_name)
                if hasattr(field.related_model, manager):
                    related_attr = getattr(field.related_model, manager).filter(**{field.field.name: user.pk})
            elif isinstance(field, OneToOneRel):
                related_attr = getattr(user, field.name)
            else:
                related_attr = getattr(user, f"{field.name}_set")
            info["filter"] = f"{field.field.name}={user.pk}"
            if hasattr(related_attr, "all") and callable(related_attr.all):
                related = related_attr.all()[: max_records or 200]
                count = related_attr.all().count()
            else:
                related = [related_attr]
                count = 1
            info["data"] = related
            info["count"] = count
        except ObjectDoesNotExist:
            info["data"] = []
            info["related_name"] = field.related_model._meta.verbose_name

        return info

    def admin_urlbasename(self, value: Any, arg: str) -> str:
        return "%s_%s_%s" % (value.app_label, value.model_name, arg)
