from admin_extra_buttons.decorators import button
from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from hope.admin.utils import HOPEModelAdminBase
from hope.models import FollowUpInstruction


@admin.register(FollowUpInstruction)
class FollowUpInstructionAdmin(HOPEModelAdminBase):
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
        "status",
        "background_action_status",
        "created_at",
        "updated_at",
        "export_file",
        "reconciliation_import_file",
    )

    @button(permission="payment.view_followupinstruction")
    def payment_plans(self, request: HttpRequest, pk: str) -> HttpResponseRedirect:
        url = reverse("admin:payment_paymentplan_changelist")
        return HttpResponseRedirect(f"{url}?follow_up_instruction__id__exact={pk}")
