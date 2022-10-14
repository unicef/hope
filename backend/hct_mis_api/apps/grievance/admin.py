from django.contrib import admin

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import ChoicesFieldComboFilter
from advanced_filters.admin import AdminAdvancedFiltersMixin
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.grievance.models import (
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
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


@admin.register(GrievanceTicket)
class GrievanceTicketAdmin(LinkedObjectsMixin, ExtraButtonsMixin, AdminAdvancedFiltersMixin, HOPEModelAdminBase):
    list_display = (
        "unicef_id",
        "created_at",
        "created_by",
        "assigned_to",
        "status",
        "category",
        "registration_data_import",
    )
    raw_id_fields = ("created_by", "assigned_to", "admin2", "business_area", "registration_data_import")
    search_fields = ("unicef_id",)
    date_hierarchy = "created_at"
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("category", ChoicesFieldComboFilter),
        ("business_area", AutoCompleteFilter),
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


@admin.register(TicketNote)
class TicketNoteAdmin(LinkedObjectsMixin, ExtraButtonsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "created_by")


@admin.register(TicketComplaintDetails)
class TicketComplaintDetailsAdmin(LinkedObjectsMixin, ExtraButtonsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "payment_record", "household", "individual")


@admin.register(TicketSensitiveDetails)
class TicketSensitiveDetailsAdmin(LinkedObjectsMixin, ExtraButtonsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "payment_record", "household", "individual")


@admin.register(TicketHouseholdDataUpdateDetails)
class TicketHouseholdDataUpdateDetailsAdmin(LinkedObjectsMixin, ExtraButtonsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household")


@admin.register(TicketIndividualDataUpdateDetails)
class TicketIndividualDataUpdateDetailsAdmin(LinkedObjectsMixin, ExtraButtonsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "individual")


@admin.register(TicketAddIndividualDetails)
class TicketAddIndividualDetailsAdmin(LinkedObjectsMixin, ExtraButtonsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household")


@admin.register(TicketDeleteIndividualDetails)
class TicketDeleteIndividualDetailsAdmin(LinkedObjectsMixin, ExtraButtonsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "individual")


@admin.register(TicketDeleteHouseholdDetails)
class TicketDeleteHouseholdDetailsAdmin(LinkedObjectsMixin, ExtraButtonsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household")


@admin.register(TicketNeedsAdjudicationDetails)
class TicketNeedsAdjudicationDetailsAdmin(LinkedObjectsMixin, ExtraButtonsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "golden_records_individual", "possible_duplicate", "selected_individual")
    filter_horizontal = ("possible_duplicates", "selected_individuals")


@admin.register(TicketPaymentVerificationDetails)
class TicketPaymentVerificationDetailsAdmin(LinkedObjectsMixin, ExtraButtonsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket",)


@admin.register(TicketPositiveFeedbackDetails)
class TicketPositiveFeedbackDetailsAdmin(LinkedObjectsMixin, ExtraButtonsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household", "individual")


@admin.register(TicketNegativeFeedbackDetails)
class TicketNegativeFeedbackDetailsAdmin(LinkedObjectsMixin, ExtraButtonsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household", "individual")


@admin.register(TicketReferralDetails)
class TicketReferralDetailsAdmin(LinkedObjectsMixin, ExtraButtonsMixin, HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household", "individual")


@admin.register(GrievanceDocument)
class GrievanceDocumentAdmin(HOPEModelAdminBase):
    list_display = ("file_name",)
