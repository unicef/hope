from typing import TYPE_CHECKING

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import confirm_action
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter
from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponseBase, HttpResponseRedirect
from django.urls import reverse
from smart_admin.mixins import LinkedObjectsMixin

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.payment.services.verification_plan_status_change_services import (
    VerificationPlanStatusChangeServices,
)
from hope.models import PaymentVerificationPlan

if TYPE_CHECKING:
    from uuid import UUID


@admin.register(PaymentVerificationPlan)
class PaymentVerificationPlanAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = (
        "payment_plan",
        "status",
        "verification_channel",
        "sampling",
        "sample_size",
        "activation_date",
        "completion_date",
        "responded_count",
        "received_count",
        "not_received_count",
        "received_with_problems_count",
        "xlsx_file_exporting",
        "xlsx_file_imported",
        "error",
    )
    list_filter = (
        ("payment_plan__program_cycle__program__business_area", AutoCompleteFilter),
        ("payment_plan__program_cycle__program", AutoCompleteFilter),
        ("payment_plan", AutoCompleteFilter),
        ("status", ChoicesFieldComboFilter),
        ("verification_channel", ChoicesFieldComboFilter),
        "sampling",
        "xlsx_file_exporting",
        "xlsx_file_imported",
    )
    date_hierarchy = "updated_at"
    search_fields = ("payment_plan__name",)
    raw_id_fields = ("payment_plan",)

    @button(permission="payment.view_paymentverification")
    def verifications(self, request: HttpRequest, pk: "UUID") -> HttpResponseRedirect:
        list_url = reverse("admin:payment_paymentverification_changelist")
        url = f"{list_url}?payment_verification_plan__exact={pk}"
        return HttpResponseRedirect(url)

    @button(permission="core.execute_sync_rapid_pro")
    def execute_sync_rapid_pro(self, request: HttpRequest) -> HttpResponseBase | None:
        if request.method == "POST":
            from hope.apps.payment.celery_tasks import CheckRapidProVerificationTask

            task = CheckRapidProVerificationTask()
            task.execute()
            self.message_user(request, "Rapid Pro synced", messages.SUCCESS)
        else:
            return confirm_action(
                self,
                request,
                self.execute_sync_rapid_pro,
                message="""<h1>DO NOT CONTINUE IF YOU ARE NOT SURE WHAT YOU ARE DOING</h1>
                        <h3>Import will only be simulated</h3>
                        """,
                success_message="Successfully executed",
                template="admin_extra_buttons/confirm.html",
            )
        return None

    def activate(self, request: HttpRequest, pk: "UUID") -> HttpResponseBase | None:
        def _do_activate(request: HttpRequest) -> None:
            VerificationPlanStatusChangeServices(PaymentVerificationPlan.objects.get(pk=pk)).activate()

        return confirm_action(
            self,
            request,
            _do_activate,
            message="This action will trigger Cash Plan Payment Verification activation"
            " (also sending messages via Rapid Pro).",
            success_message="Successfully activated.",
        )
