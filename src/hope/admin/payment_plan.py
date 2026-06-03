from typing import TYPE_CHECKING, Any

from admin_cursor_paginator import CursorPaginatorAdmin
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter, ValueFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from django.contrib import admin, messages
from django.contrib.admin.options import get_content_type_for_model
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from hope.admin.utils import HOPEModelAdminBase, PaymentPlanCeleryTasksMixin
from hope.apps.account.permissions import Permissions
from hope.apps.payment.forms import BatchReexportForm
from hope.apps.payment.utils import get_quantity_in_usd
from hope.apps.utils.security import is_root
from hope.contrib.vision.models import FundsCommitmentItem
from hope.models import (
    AsyncJob,
    Payment,
    PaymentHouseholdSnapshot,
    PaymentPlan,
    PaymentPlanGroup,
    PaymentPlanSupportingDocument,
)

if TYPE_CHECKING:
    from uuid import UUID


class FundsCommitmentItemInline(admin.TabularInline):  # or admin.StackedInline
    model = FundsCommitmentItem
    extra = 0
    can_delete = False
    show_change_link = True
    fields = readonly_fields = (
        "rec_serial_number",
        "funds_commitment_group",
        "funds_commitment_item",
        "fc_status",
        "commitment_amount_local",
        "commitment_amount_usd",
        "total_open_amount_local",
        "total_open_amount_usd",
    )

    def has_add_permission(self: Any, request: Any, obj: Any = None) -> bool:
        return False

    def has_change_permission(self: Any, request: Any, obj: Any = None) -> bool:
        return False

    def has_delete_permission(self: Any, request: Any, obj: Any = None) -> bool:
        return False


def can_sync_with_payment_gateway(payment_plan: PaymentPlan) -> bool:
    return payment_plan.is_payment_gateway and payment_plan.status in [
        PaymentPlan.Status.ACCEPTED,
        PaymentPlan.Status.FINISHED,
    ]


def has_payment_plan_pg_sync_permission(request: Any, payment_plan: PaymentPlan) -> bool:
    return request.user.has_perm(
        Permissions.PM_SYNC_PAYMENT_PLAN_WITH_PG.value,
        payment_plan.program,
    )


@admin.register(PaymentPlan)
class PaymentPlanAdmin(HOPEModelAdminBase, PaymentPlanCeleryTasksMixin):
    list_display = (
        "unicef_id",
        "name",
        "business_area",
        "program_cycle",
        "status",
        "use_payment_gateway",
        "background_action_status",
        "build_status",
        "plan_type",
    )
    list_filter = (
        ("business_area", AutoCompleteFilter),
        ("program_cycle__program", AutoCompleteFilter),
        ("program_cycle__program__id", ValueFilter),
        ("currency__code", AutoCompleteFilter),
        ("status", ChoicesFieldComboFilter),
        "use_payment_gateway",
        ("background_action_status", ChoicesFieldComboFilter),
        ("build_status", ChoicesFieldComboFilter),
        ("created_by", AutoCompleteFilter),
        ("plan_type", ChoicesFieldComboFilter),
    )
    search_fields = ("id", "unicef_id", "name")
    date_hierarchy = "updated_at"
    filter_horizontal = ("payment_plan_purposes",)
    inlines = [FundsCommitmentItemInline]

    @button(permission="payment.view_paymentplan")
    def wu_reports(self, request: HttpRequest, pk: "UUID") -> HttpResponseRedirect:
        url = reverse("admin:payment_westernunionpaymentplanreport_changelist")
        return HttpResponseRedirect(f"{url}?payment_plan__id__exact={pk}")

    def get_form(self, request: HttpRequest, obj: Any = None, change: bool = False, **kwargs: Any) -> Any:
        request._payment_plan_obj = obj
        return super().get_form(request, obj, change, **kwargs)

    def formfield_for_manytomany(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "payment_plan_purposes":
            obj = getattr(request, "_payment_plan_obj", None)
            if obj is not None:
                kwargs["queryset"] = obj.program_cycle.program.payment_plan_purposes.all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return is_root(request)

    @button(
        visible=lambda btn: btn.original.status == PaymentPlan.Status.ACCEPTED,
        permission="payment.recalculate_exchange_rate",
    )
    def recalculate_exchange_rate(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        if request.method == "POST":
            with transaction.atomic():
                payment_plan = PaymentPlan.objects.get(pk=pk)
                if payment_plan.currency is None:
                    raise ValueError("PaymentPlan.currency must not be None")
                updates = []
                currency_exchange_date = payment_plan.currency_exchange_date
                for payment in payment_plan.eligible_payments:
                    payment.entitlement_quantity_usd = get_quantity_in_usd(
                        amount=payment.entitlement_quantity,
                        currency=payment_plan.currency,
                        exchange_rate=payment_plan.exchange_rate,
                        currency_exchange_date=currency_exchange_date,
                    )
                    payment.delivered_quantity_usd = get_quantity_in_usd(
                        amount=payment.delivered_quantity,
                        currency=payment_plan.currency,
                        exchange_rate=payment_plan.exchange_rate,
                        currency_exchange_date=currency_exchange_date,
                    )
                    updates.append(payment)
                Payment.objects.bulk_update(updates, ["entitlement_quantity_usd", "delivered_quantity_usd"])
                payment_plan.update_money_fields()

                # invalidate cache for program cycle list
                payment_plan.program_cycle.save()
            return redirect(reverse("admin:payment_paymentplan_change", args=[pk]))
        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.recalculate_exchange_rate,
            message="Do you confirm to recalculate USD values based on provided exchange rate?",
        )

    @button(
        visible=lambda btn: can_sync_with_payment_gateway(btn.original),
        permission=lambda request, payment_plan, *args, **kwargs: has_payment_plan_pg_sync_permission(
            request, payment_plan
        ),
    )
    def sync_with_payment_gateway(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        if request.method == "POST":
            from hope.apps.payment.services.payment_gateway import PaymentGatewayService

            payment_plan = PaymentPlan.objects.get(pk=pk)
            PaymentGatewayService().sync_payment_plan(payment_plan)

            return redirect(reverse("admin:payment_paymentplan_change", args=[pk]))
        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.sync_with_payment_gateway,
            message="Do you confirm to Sync with Payment Gateway?",
        )

    @button(
        visible=lambda btn: can_sync_with_payment_gateway(btn.original),
        permission=lambda request, payment_plan, *args, **kwargs: has_payment_plan_pg_sync_permission(
            request, payment_plan
        ),
    )
    def sync_missing_records_with_payment_gateway(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        if request.method == "POST":
            from hope.apps.payment.services.payment_gateway import PaymentGatewayService

            payment_plan = PaymentPlan.objects.get(pk=pk)
            PaymentGatewayService().add_missing_records_to_payment_instructions(payment_plan)

            return redirect(reverse("admin:payment_paymentplan_change", args=[pk]))
        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.sync_missing_records_with_payment_gateway,
            message="Do you confirm to Sync with Payment Gateway missing Records?",
        )

    @button(permission="payment.view_paymentplan")
    def related_configs(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        obj = PaymentPlan.objects.get(pk=pk)
        url = reverse("admin:payment_deliverymechanismconfig_changelist")
        if not obj.delivery_mechanism or not obj.financial_service_provider:
            self.message_user(
                request,
                "This payment plan has no delivery mechanism or financial service provider assigned.",
                level="warning",
            )
            return HttpResponseRedirect(url)
        flt = f"delivery_mechanism__exact={obj.delivery_mechanism.id}&fsp__exact={obj.financial_service_provider.id}"
        return HttpResponseRedirect(f"{url}?{flt}")

    @button(permission="payment.view_paymentplan")
    def payment_records(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        url = reverse("admin:payment_payment_changelist")
        filter_by_parent = f"&parent__exact={str(pk)}"
        return HttpResponseRedirect(f"{url}?{filter_by_parent}")


@admin.register(PaymentPlanGroup)
class PaymentPlanGroupAdmin(HOPEModelAdminBase):
    list_display = ("unicef_id", "name", "cycle")
    search_fields = ("name", "unicef_id")
    list_filter = (("cycle__program__business_area", AutoCompleteFilter),)

    @button(permission="payment.view_paymentplan")
    def payment_plans(self, request: HttpRequest, pk: "UUID") -> HttpResponseRedirect:
        url = reverse("admin:payment_paymentplan_changelist")
        return HttpResponseRedirect(f"{url}?payment_plan_group__id__exact={pk}")

    @button(permission="payment.restart_exporting_payment_plan_list")
    def reexport_batch(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        from hope.apps.payment.celery_tasks import (
            export_payment_plan_group_delivery_xlsx_async_task,
        )

        group = PaymentPlanGroup.objects.get(pk=pk)
        if request.method == "POST":
            form = BatchReexportForm(request.POST, payment_plan_group=group)
            if form.is_valid():
                export_tag = int(form.cleaned_data["export_tag"])
                if not group.can_reexport_batch(export_tag):
                    messages.error(
                        request,
                        f"Batch {export_tag} cannot be re-exported: it has no stored export file.",
                    )
                    return redirect(reverse("admin:payment_paymentplangroup_change", args=[pk]))
                template_obj = form.cleaned_data.get("template")
                fsp_xlsx_template_id = str(template_obj.id) if template_obj else None
                group.background_action_status_export = PaymentPlanGroup.BackgroundExportActionStatus.XLSX_EXPORTING
                group.save(update_fields=["background_action_status_export"])
                export_payment_plan_group_delivery_xlsx_async_task(
                    group, str(request.user.pk), fsp_xlsx_template_id, export_tag
                )
                messages.success(request, f"Re-export started for batch {export_tag}.")
                return redirect(reverse("admin:payment_paymentplangroup_change", args=[pk]))
        else:
            form = BatchReexportForm(payment_plan_group=group)

        return render(
            request,
            "admin/payment/reexport_batch_form.html",
            {"form": form, "payment_plan_group": group, "title": "Re-export a delivered batch"},
        )

    @button(
        visible=lambda btn: (
            btn.original.background_action_status_export == PaymentPlanGroup.BackgroundExportActionStatus.XLSX_EXPORTING
        ),
        permission="payment.restart_exporting_payment_plan_list",
    )
    def restart_exporting_delivery_xlsx(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        from hope.apps.payment.celery_tasks import (
            export_payment_plan_group_delivery_xlsx_async_task,
        )

        if request.method == "POST":
            group = PaymentPlanGroup.objects.get(pk=pk)

            active_jobs = [
                job
                for job in AsyncJob.objects.filter(
                    content_type=get_content_type_for_model(group),
                    object_id=str(group.pk),
                    job_name="export_payment_plan_group_delivery_xlsx_async_task",
                )
                if job.task_status in job.ACTIVE_STATUSES
            ]

            if not active_jobs:
                messages.error(request, "There is no active export job for this payment plan group.")
                return redirect(reverse("admin:payment_paymentplangroup_change", args=[pk]))

            config = active_jobs[0].config
            for job in active_jobs:
                job.terminate()

            export_tag = config.get("export_tag")
            fsp_xlsx_template_id = config.get("fsp_xlsx_template_id")
            user_id = str(request.user.pk)

            export_payment_plan_group_delivery_xlsx_async_task(group, user_id, fsp_xlsx_template_id, export_tag)

            messages.success(request, "Successfully restarted delivery XLSX export.")
            return redirect(reverse("admin:payment_paymentplangroup_change", args=[pk]))

        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.restart_exporting_delivery_xlsx,
            message="Do you confirm to restart exporting delivery XLSX file task?",
        )

    @button(
        visible=lambda btn: (
            btn.original.background_action_status_import
            == PaymentPlanGroup.BackgroundImportActionStatus.XLSX_IMPORTING_RECONCILIATION
        ),
        permission="payment.restart_importing_reconciliation_xlsx_file",
    )
    def restart_importing_reconciliation_xlsx_file(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        from hope.apps.payment.celery_tasks import import_payment_plan_group_delivery_from_xlsx_async_task

        if request.method == "POST":
            group = PaymentPlanGroup.objects.get(pk=pk)
            if not group.delivery_import_file:
                messages.error(request, "There is no import file for this payment plan group.")
                return redirect(reverse("admin:payment_paymentplangroup_change", args=[pk]))

            task_name = "import_payment_plan_group_delivery_from_xlsx_async_task"
            active_jobs = [
                job
                for job in AsyncJob.objects.filter(
                    content_type=get_content_type_for_model(group),
                    object_id=str(group.pk),
                    job_name=task_name,
                )
                if job.task_status in job.ACTIVE_STATUSES
            ]

            if active_jobs:
                for job in active_jobs:
                    job.terminate()
                import_payment_plan_group_delivery_from_xlsx_async_task(group)
                messages.success(request, "Successfully restarted reconciliation import.")
            else:
                messages.error(request, f"There is no current {task_name} for this payment plan group.")

            return redirect(reverse("admin:payment_paymentplangroup_change", args=[pk]))

        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.restart_importing_reconciliation_xlsx_file,
            message="Do you confirm to restart importing reconciliation XLSX file task?",
        )


class PaymentHouseholdSnapshotInline(admin.StackedInline):
    model = PaymentHouseholdSnapshot
    readonly_fields = ("snapshot_data", "household_id")


def has_payment_pg_sync_permission(request: Any, payment: Payment) -> bool:
    return request.user.has_perm(
        Permissions.PM_SYNC_PAYMENT_WITH_PG.value,
        payment.parent.program,
    )


@admin.register(Payment)
class PaymentAdmin(CursorPaginatorAdmin, AdminAdvancedFiltersMixin, HOPEModelAdminBase):
    search_fields = ("unicef_id",)
    list_display = (
        "unicef_id",
        "household",
        "business_area",
        "program",
        "delivery_type",
        "status",
        "parent",
        "entitlement_quantity",
        "delivered_quantity",
        "transaction_reference_id",
        "conflicted",
        "excluded",
        "is_follow_up",
        "is_cash_assist",
    )
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("program", AutoCompleteFilter),
        ("parent", AutoCompleteFilter),
        ("delivery_type", AutoCompleteFilter),
        ("financial_service_provider", AutoCompleteFilter),
        ("currency", AutoCompleteFilter),
    )
    advanced_filter_fields = (
        "status",
        "delivery_date",
        ("financial_service_provider__name", "Service Provider"),
        ("parent", "Payment Plan"),
    )
    cursor_ordering_field = "-created_at"
    inlines = [PaymentHouseholdSnapshotInline]
    exclude = ("delivery_type_choice",)
    readonly_fields = ("collector_type",)

    show_full_result_count = False

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .select_related(
                "household",
                "business_area",
                "program",
                "delivery_type",
                "parent",
            )
            .only(
                "id",
                "unicef_id",
                "status",
                "entitlement_quantity",
                "delivered_quantity",
                "transaction_reference_id",
                "conflicted",
                "excluded",
                "is_follow_up",
                "is_cash_assist",
                "household__unicef_id",
                "business_area__name",
                "program__name",
                "delivery_type__name",
                "parent__unicef_id",
            )
        )

    def has_delete_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        return False

    @button(
        visible=lambda btn: can_sync_with_payment_gateway(btn.original.parent),
        permission=lambda request, payment, *args, **kwargs: has_payment_pg_sync_permission(request, payment),
    )
    def sync_with_payment_gateway(self, request: HttpRequest, pk: "UUID") -> HttpResponse:
        if request.method == "POST":
            from hope.apps.payment.services.payment_gateway import PaymentGatewayService

            payment = Payment.objects.get(pk=pk)
            PaymentGatewayService().sync_record(payment)

            return redirect(reverse("admin:payment_payment_change", args=[pk]))
        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.sync_with_payment_gateway,
            message="Do you confirm to Sync with Payment Gateway?",
        )


@admin.register(PaymentPlanSupportingDocument)
class PaymentPlanSupportingDocumentAdmin(HOPEModelAdminBase):
    search_fields = ("title",)
    list_display = ("title", "payment_plan", "created_by", "uploaded_at")
    list_filter = (("created_by", AutoCompleteFilter),)
