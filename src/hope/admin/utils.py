import uuid
from typing import Any, Sequence
from uuid import UUID

from admin_extra_buttons.buttons import Button
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin, confirm_action
from adminactions.helpers import AdminActionPermMixin
from adminfilters.mixin import AdminFiltersMixin
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Field, JSONField, Model, OneToOneRel, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from jsoneditor.forms import JSONEditor
from smart_admin.mixins import DisplayAllMixin as SmartDisplayAllMixin

from hope.apps.administration.widgets import JsonWidget
from hope.apps.core.celery import app as celery_app
from hope.models.business_area import BusinessArea
from hope.models.file_temp import FileTemp
from hope.models.payment_plan import PaymentPlan
from hope.apps.payment.utils import generate_cache_key
from hope.apps.utils.celery_utils import get_task_in_queue_or_running
from hope.apps.utils.security import is_root


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
        if isinstance(db_field, JSONField):
            if is_root(request) or settings.DEBUG or self.json_enabled:
                kwargs = {"widget": JSONEditor}
            else:
                kwargs = {"widget": JsonWidget}
            return db_field.formfield(**kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class LastSyncDateResetMixin:
    @button(permission=is_root)
    def reset_sync_date(self, request: HttpRequest) -> HttpResponse | None:
        if request.method == "POST":
            self.get_queryset(request).update(last_sync_at=None)
        else:
            return confirm_action(
                self,
                request,
                self.reset_sync_date,
                "Continuing will reset all records last_sync_date field.",
                "Successfully executed",
                title="aaaaa",
            )
        return None

    @button(label="reset sync date", permission=is_root)
    def reset_sync_date_single(self, request: HttpRequest, pk: UUID) -> HttpResponse | None:
        if request.method == "POST":
            self.get_queryset(request).filter(id=pk).update(last_sync_at=None)
        else:
            return confirm_action(
                self,
                request,
                self.reset_sync_date,
                "Continuing will reset last_sync_date field.",
                "Successfully executed",
            )
        return None


class HopeModelAdminMixin(ExtraButtonsMixin, SmartDisplayAllMixin, AdminActionPermMixin, AdminFiltersMixin):
    pass


class HOPEModelAdminBase(HopeModelAdminMixin, JSONWidgetMixin, admin.ModelAdmin):
    list_per_page = 50

    def get_fields(self, request: HttpRequest, obj: Any | None = None) -> Sequence[str | Sequence[str]]:
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

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> QuerySet:
        from hope.models.business_area import BusinessArea

        return BusinessArea.objects.values_list("code", "name").distinct()

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value():
            return queryset.filter(session__business_area=self.value()).distinct()
        return queryset


class BusinessAreaForCollectionsListFilter(admin.SimpleListFilter):
    model_filter_field = "households__business_area__id"
    title = "business area"
    parameter_name = "business_area__exact"
    template = "adminfilters/combobox.html"

    def lookups(self, request: HttpRequest, model_admin: ModelAdmin) -> QuerySet:
        return BusinessArea.objects.all().values_list("id", "name")

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if self.value():
            return queryset.filter(**{self.model_filter_field: self.value()}).distinct()
        return queryset


class BusinessAreaForHouseholdCollectionListFilter(BusinessAreaForCollectionsListFilter):
    model_filter_field = "households__business_area__id"


class BusinessAreaForIndividualCollectionListFilter(BusinessAreaForCollectionsListFilter):
    model_filter_field = "individuals__business_area__id"


def is_enabled(btn: Button) -> bool:
    return btn.request.user.is_superuser


def is_payment_plan_in_status(btn: Button, status: str) -> bool:
    return btn.original.status == status


def is_background_action_in_status(btn: Button, background_status: str) -> bool:
    return btn.original.background_action_status == background_status


def is_preparing_payment_plan(btn: Button) -> bool:
    return is_payment_plan_in_status(btn, PaymentPlan.Status.OPEN)


def is_locked_payment_plan(btn: Button) -> bool:
    return is_payment_plan_in_status(btn, PaymentPlan.Status.LOCKED)


def is_accepted_payment_plan(btn: Button) -> bool:
    return is_payment_plan_in_status(btn, PaymentPlan.Status.ACCEPTED)


def is_importing_entitlements_xlsx_file(btn: Button) -> bool:
    return is_background_action_in_status(btn, PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_ENTITLEMENTS)


def is_importing_reconciliation_xlsx_file(btn: Button) -> bool:
    return is_background_action_in_status(btn, PaymentPlan.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION)


def is_exporting_xlsx_file(btn: Button) -> bool:
    return is_background_action_in_status(btn, PaymentPlan.BackgroundActionStatus.XLSX_EXPORTING)


def revoke_with_termination(task_id: str) -> None:
    celery_app.control.revoke(task_id=task_id, terminate=True, signal="SIGKILL")


class PaymentPlanCeleryTasksMixin:
    prefix = "hope.apps.payment.celery_tasks"
    prepare_payment_plan_task = f"{prefix}.prepare_payment_plan_task"
    import_payment_plan_payment_list_from_xlsx = f"{prefix}.import_payment_plan_payment_list_from_xlsx"
    import_payment_plan_payment_list_per_fsp_from_xlsx = f"{prefix}.import_payment_plan_payment_list_per_fsp_from_xlsx"
    create_payment_plan_payment_list_xlsx = f"{prefix}.create_payment_plan_payment_list_xlsx"
    create_payment_plan_payment_list_xlsx_per_fsp = f"{prefix}.create_payment_plan_payment_list_xlsx_per_fsp"

    url = "admin:payment_paymentplan_change"

    @button(
        visible=lambda btn: is_preparing_payment_plan(btn),
        enabled=lambda btn: is_enabled(btn),
        permission=is_root,
    )
    def restart_preparing_payment_plan(self, request: HttpRequest, pk: str) -> HttpResponse | None:
        """Prepare Payment Plan."""
        from hope.apps.payment.celery_tasks import prepare_payment_plan_task

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
                "task_name": "prepare_payment_plan_task",
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
            prepare_payment_plan_task.delay(payment_plan.id)
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
        enabled=lambda btn: is_enabled(btn),
    )
    def restart_exporting_template_for_entitlement(self, request: HttpRequest, pk: str) -> HttpResponse | None:
        """Export template for entitlement."""
        from hope.apps.payment.celery_tasks import create_payment_plan_payment_list_xlsx

        if request.method == "POST":
            task_name = self.create_payment_plan_payment_list_xlsx
            payment_plan = PaymentPlan.objects.get(pk=pk)
            kwargs = {
                "payment_plan_id": uuid.UUID(pk),
                "user_id": uuid.UUID(str(payment_plan.created_by.id)),
            }
            task_data = get_task_in_queue_or_running(name=task_name, kwargs=kwargs)
            if task_data:
                task_id = task_data["id"]
                revoke_with_termination(task_id)
                create_payment_plan_payment_list_xlsx.apply_async(
                    kwargs={
                        "payment_plan_id": uuid.UUID(pk),
                        "user_id": uuid.UUID(str(request.user.id)),
                    },
                )
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
        enabled=lambda btn: is_enabled(btn),
    )
    def restart_importing_entitlements_xlsx_file(self, request: HttpRequest, pk: str) -> HttpResponse | None:
        """Import entitlement file."""
        from hope.apps.payment.celery_tasks import (
            import_payment_plan_payment_list_from_xlsx,
        )

        if request.method == "POST":
            task_name = self.import_payment_plan_payment_list_from_xlsx
            args = [uuid.UUID(pk)]
            task_data = get_task_in_queue_or_running(name=task_name, args=args)
            if task_data:
                task_id = task_data["id"]
                revoke_with_termination(task_id)
                import_payment_plan_payment_list_from_xlsx.apply_async(args=args)

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
        enabled=lambda btn: is_enabled(btn),
    )
    def restart_exporting_payment_plan_list(self, request: HttpRequest, pk: str) -> HttpResponse | None:
        """Export payment plan list."""
        from hope.apps.payment.celery_tasks import (
            create_payment_plan_payment_list_xlsx_per_fsp,
        )

        if request.method == "POST":
            task_name = self.create_payment_plan_payment_list_xlsx_per_fsp
            payment_plan = PaymentPlan.objects.get(pk=pk)
            args = [uuid.UUID(pk), uuid.UUID(str(payment_plan.created_by.id))]
            task_data = get_task_in_queue_or_running(name=task_name, args=args)
            if task_data:
                task_id = task_data["id"]
                revoke_with_termination(task_id)
                create_payment_plan_payment_list_xlsx_per_fsp.apply_async(args=args)

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
        enabled=lambda btn: is_enabled(btn),
    )
    def restart_importing_reconciliation_xlsx_file(self, request: HttpRequest, pk: str) -> HttpResponse | None:
        """Import payment plan list (from xlsx)."""
        from hope.apps.payment.celery_tasks import (
            import_payment_plan_payment_list_per_fsp_from_xlsx,
        )

        if request.method == "POST":
            task_name = self.import_payment_plan_payment_list_per_fsp_from_xlsx
            file_id = FileTemp.objects.get(object_id=pk).pk
            args = [uuid.UUID(pk), file_id]
            task_data = get_task_in_queue_or_running(name=task_name, args=args)
            if task_data:
                task_id = task_data["id"]
                revoke_with_termination(task_id)
                import_payment_plan_payment_list_per_fsp_from_xlsx.apply_async(args=args)

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

    @button()
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

    def get_related(self, user: Model, field: Field, manager: str, max_records: int = 200) -> dict[str, Any]:
        """Override 'get_related' from 'smart_admin', to take related objects with a custom manager."""
        info = {
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
            info["data"] = []  # type: ignore
            info["related_name"] = field.related_model._meta.verbose_name

        return info

    def admin_urlbasename(self, value: Any, arg: str) -> str:
        return "%s_%s_%s" % (value.app_label, value.model_name, arg)
