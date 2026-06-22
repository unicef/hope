from admin_extra_buttons.decorators import button
from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

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
        "export_file_download_link",
        "reconciliation_import_file",
        "reconciliation_import_file_download_link",
    )

    @button(permission="payment.view_followupinstruction")
    def payment_plans(self, request: HttpRequest, pk: str) -> HttpResponseRedirect:
        url = reverse("admin:payment_paymentplan_changelist")
        return HttpResponseRedirect(f"{url}?follow_up_instruction__id__exact={pk}")

    def export_file_download_link(self, obj: FollowUpInstruction) -> str:
        if not obj.export_file or not obj.export_file.file:
            return "-"
        return format_html('<a href="{}" target="_blank">Download</a>', obj.export_file.file.url)

    export_file_download_link.short_description = "Export File Download"

    def reconciliation_import_file_download_link(self, obj: FollowUpInstruction) -> str:
        if not obj.reconciliation_import_file or not obj.reconciliation_import_file.file:
            return "-"
        return format_html('<a href="{}" target="_blank">Download</a>', obj.reconciliation_import_file.file.url)

    reconciliation_import_file_download_link.short_description = "Reconciliation File Download"
