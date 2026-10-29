from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import confirm_action
from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from hope.admin.utils import HOPEModelAdminBase, ViewOnUiMixin
from hope.apps.payment.celery_tasks import recalculate_owner_exchange_rate_async_task
from hope.models import FollowUpInstruction


@admin.register(FollowUpInstruction)
class FollowUpInstructionAdmin(ViewOnUiMixin, HOPEModelAdminBase):
    list_display = (
        "unicef_id",
        "business_area",
        "program",
        "status",
        "background_action_status",
        "created_by",
        "created_at",
    )
    list_filter = ("business_area", "program")
    search_fields = ("id", "unicef_id", "program__name", "program__code")
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "unicef_id",
        "business_area",
        "program",
        "created_by",
        "financial_service_provider",
        "currency",
        "exchange_rate",
        "custom_exchange_rate",
        "custom_exchange_rate_set_by",
        "status",
    )

    def frontend_url(self, obj: FollowUpInstruction) -> str | None:
        return f"/{obj.business_area.slug}/programs/{obj.program.code}/payment-module/follow-up-instructions/{obj.id}"

    @button(permission="payment.view_followupinstruction")
    def payment_plans(self, request: HttpRequest, pk: str) -> HttpResponseRedirect:
        url = reverse("admin:payment_paymentplan_changelist")
        return HttpResponseRedirect(f"{url}?follow_up_instruction__id__exact={pk}")

    @button(
        label="Retry USD recalculation",
        visible=lambda btn: (
            btn.original.background_action_status == FollowUpInstruction.BackgroundActionStatus.RECALCULATING_ERROR
        ),
        permission="payment.recalculate_exchange_rate",
    )
    def retry_usd_recalculation(self, request: HttpRequest, pk: str) -> HttpResponse:
        if request.method == "POST":
            instruction = FollowUpInstruction.objects.get(pk=pk)
            if instruction.background_action_status != FollowUpInstruction.BackgroundActionStatus.RECALCULATING_ERROR:
                self.message_user(request, "A failed instruction USD recalculation is required", level=messages.ERROR)
            else:
                recalculate_owner_exchange_rate_async_task(instruction, str(request.user.pk), fetch_unore_rate=True)
                self.message_user(request, "Instruction USD recalculation retry queued", level=messages.SUCCESS)
            return redirect(reverse("admin:payment_followupinstruction_change", args=[pk]))
        return confirm_action(
            modeladmin=self,
            request=request,
            action=self.retry_usd_recalculation,
            message="Retry USD recalculation for every Payment Plan in this instruction?",
        )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False
