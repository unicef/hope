from typing import cast

from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from smart_admin.mixins import LinkedObjectsMixin

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.grievance.models import (
    GrievanceDocument,
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketNegativeFeedbackDetails,
    TicketNote,
    TicketPaymentVerificationDetails,
    TicketPositiveFeedbackDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
)


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
    filter_horizontal = ("programs",)
    inlines = [GrievanceTicketCopiedToInline]
    show_full_result_count = False

    def get_queryset(self, request: HttpRequest) -> QuerySet["GrievanceTicket"]:
        qs = cast(
            "QuerySet[GrievanceTicket]",
            super()
            .get_queryset(request)
            .select_related("created_by", "assigned_to", "registration_data_import")
            .only(
                "id",
                "unicef_id",
                "created_at",
                "status",
                "category",
                "registration_data_import__name",
                "created_by__first_name",
                "created_by__last_name",
                "created_by__email",
                "created_by__username",
                "assigned_to__first_name",
                "assigned_to__last_name",
                "assigned_to__email",
                "assigned_to__username",
            ),
        )
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(TicketNote)
class TicketNoteAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    pass


@admin.register(TicketComplaintDetails)
class TicketComplaintDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    pass


@admin.register(TicketSensitiveDetails)
class TicketSensitiveDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    pass


@admin.register(TicketHouseholdDataUpdateDetails)
class TicketHouseholdDataUpdateDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    pass


@admin.register(TicketIndividualDataUpdateDetails)
class TicketIndividualDataUpdateDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    pass


@admin.register(TicketAddIndividualDetails)
class TicketAddIndividualDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    pass


@admin.register(TicketDeleteIndividualDetails)
class TicketDeleteIndividualDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    pass


@admin.register(TicketDeleteHouseholdDetails)
class TicketDeleteHouseholdDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    pass


@admin.register(TicketNeedsAdjudicationDetails)
class TicketNeedsAdjudicationDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    pass


@admin.register(TicketPaymentVerificationDetails)
class TicketPaymentVerificationDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    filter_horizontal = ["payment_verifications"]


@admin.register(TicketPositiveFeedbackDetails)
class TicketPositiveFeedbackDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    pass


@admin.register(TicketNegativeFeedbackDetails)
class TicketNegativeFeedbackDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    pass


@admin.register(TicketReferralDetails)
class TicketReferralDetailsAdmin(LinkedObjectsMixin, HOPEModelAdminBase):
    pass


@admin.register(GrievanceDocument)
class GrievanceDocumentAdmin(HOPEModelAdminBase):
    list_display = ("file_name",)
