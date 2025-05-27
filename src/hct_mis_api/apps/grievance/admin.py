from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.grievance.models import (
    GrievanceDocument, GrievanceTicket, TicketAddIndividualDetails,
    TicketComplaintDetails, TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails, TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails, TicketNeedsAdjudicationDetails,
    TicketNegativeFeedbackDetails, TicketNote,
    TicketPaymentVerificationDetails, TicketPositiveFeedbackDetails,
    TicketReferralDetails, TicketSensitiveDetails)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


class GrievanceTicketCopiedToInline(admin.TabularInline):
    model = GrievanceTicket
    extra = 0
    fields = ("unicef_id",)
    readonly_fields = ("unicef_id",)
    show_change_link = True
    can_delete = False
    verbose_name_plural = "Grievance Ticket representations"

    def get_queryset(self, request: HttpRequest) -> QuerySet["GrievanceTicket"]:
        return GrievanceTicket.objects.all()


@admin.register(GrievanceTicket)
class GrievanceTicketAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    list_display = (
        "unicef_id",
        "created_at",
        "created_by",
        "assigned_to",
        "status",
        "category",
        "registration_data_import",
    )
    raw_id_fields = (
        "created_by",
        "assigned_to",
        "admin2",
        "business_area",
        "registration_data_import",
        "partner",
        "copied_from",
    )
    search_fields = ("unicef_id",)
    date_hierarchy = "created_at"
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("category", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
        ("programs", AutoCompleteFilter),
        ("registration_data_import", AutoCompleteFilter),
        ("created_by", AutoCompleteFilter),
        ("assigned_to", AutoCompleteFilter),
        "updated_at",
    )
    advanced_filter_fields = (
        "created_at",
        "status",
        "category",
        ("registration_data_import__name", "RDI"),
        ("created_by__username", "created by"),
        ("assigned_to__username", "assigned to"),
        ("business_area__name", "business area"),
    )

    readonly_fields = ("unicef_id",)
    filter_horizontal = ("linked_tickets", "programs")
    inlines = [GrievanceTicketCopiedToInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet["GrievanceTicket"]:
        qs = (
            self.model.objects.get_queryset()
            .select_related(
                "registration_data_import", "business_area", "assigned_to", "created_by", "admin2", "partner"
            )
            .prefetch_related("programs")
        )
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(TicketNote)
class TicketNoteAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "created_by")


@admin.register(TicketComplaintDetails)
class TicketComplaintDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household", "individual", "payment")


@admin.register(TicketSensitiveDetails)
class TicketSensitiveDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household", "individual")


@admin.register(TicketHouseholdDataUpdateDetails)
class TicketHouseholdDataUpdateDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household")


@admin.register(TicketIndividualDataUpdateDetails)
class TicketIndividualDataUpdateDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "individual")


@admin.register(TicketAddIndividualDetails)
class TicketAddIndividualDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household")


@admin.register(TicketDeleteIndividualDetails)
class TicketDeleteIndividualDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "individual")


@admin.register(TicketDeleteHouseholdDetails)
class TicketDeleteHouseholdDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household", "reason_household")


@admin.register(TicketNeedsAdjudicationDetails)
class TicketNeedsAdjudicationDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    raw_id_fields = (
        "ticket",
        "golden_records_individual",
        "possible_duplicate",
        "selected_individual",
        "possible_duplicates",
        "selected_individuals",
        "selected_distinct",
    )


@admin.register(TicketPaymentVerificationDetails)
class TicketPaymentVerificationDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "payment_verifications")
    filter_horizontal = ["payment_verifications"]


@admin.register(TicketPositiveFeedbackDetails)
class TicketPositiveFeedbackDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household", "individual")


@admin.register(TicketNegativeFeedbackDetails)
class TicketNegativeFeedbackDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household", "individual")


@admin.register(TicketReferralDetails)
class TicketReferralDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household", "individual")


@admin.register(GrievanceDocument)
class GrievanceDocumentAdmin(HOPEModelAdminBase):
    list_display = ("file_name",)
    raw_id_fields = ("created_by", "grievance_ticket")
