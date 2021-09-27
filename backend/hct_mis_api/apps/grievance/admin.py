from django.contrib import admin
from django.contrib.admin import TabularInline

from admin_extra_urls.mixins import ExtraUrlMixin
from adminfilters.autocomplete import AutoCompleteFilter
from adminfilters.filters import (
    ChoicesFieldComboFilter,
    RelatedFieldComboFilter,
    TextFieldFilter,
)
from advanced_filters.admin import AdminAdvancedFiltersMixin
from smart_admin.mixins import LinkedObjectsMixin

from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
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
class GrievanceTicketAdmin(LinkedObjectsMixin, ExtraUrlMixin, AdminAdvancedFiltersMixin, HOPEModelAdminBase):
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
        ("business_area", RelatedFieldComboFilter),
        ("registration_data_import", AutoCompleteFilter),
        TextFieldFilter.factory("created_by__username__istartswith"),
        TextFieldFilter.factory("created_by__username__istartswith"),
        TextFieldFilter.factory("assigned_to__username__istartswith"),
        "updated_at",
    )
    advanced_filter_fields = (
        "created_at",
        "status",
        "category",
        ("created_by__username", "created by"),
        ("assigned_to__username", "assigned to"),
        ("business_area__name", "business area"),
    )

    readonly_fields = ("unicef_id",)


@admin.register(TicketNote)
class TicketNoteAdmin(HOPEModelAdminBase):
    raw_id_fields = ("ticket", "created_by")


@admin.register(TicketComplaintDetails)
class TicketComplaintDetailsAdmin(HOPEModelAdminBase):
    raw_id_fields = ("ticket", "payment_record", "household", "individual")


@admin.register(TicketSensitiveDetails)
class TicketSensitiveDetailsAdmin(HOPEModelAdminBase):
    raw_id_fields = ("ticket", "payment_record", "household", "individual")


@admin.register(TicketHouseholdDataUpdateDetails)
class TicketHouseholdDataUpdateDetailsAdmin(HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household")


@admin.register(TicketIndividualDataUpdateDetails)
class TicketIndividualDataUpdateDetailsAdmin(HOPEModelAdminBase):
    raw_id_fields = ("ticket", "individual")


@admin.register(TicketAddIndividualDetails)
class TicketAddIndividualDetailsAdmin(HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household")


@admin.register(TicketDeleteIndividualDetails)
class TicketDeleteIndividualDetailsAdmin(HOPEModelAdminBase):
    raw_id_fields = ("ticket", "individual")


@admin.register(TicketNeedsAdjudicationDetails)
class TicketNeedsAdjudicationDetailsAdmin(HOPEModelAdminBase):
    raw_id_fields = ("ticket", "golden_records_individual", "possible_duplicate", "selected_individual")


@admin.register(TicketPaymentVerificationDetails)
class TicketPaymentVerificationDetailsAdmin(HOPEModelAdminBase):
    raw_id_fields = ("ticket",)


@admin.register(TicketPositiveFeedbackDetails)
class TicketPositiveFeedbackDetailsAdmin(HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household", "individual")


@admin.register(TicketNegativeFeedbackDetails)
class TicketNegativeFeedbackDetailsAdmin(HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household", "individual")


@admin.register(TicketReferralDetails)
class TicketReferralDetailsAdmin(HOPEModelAdminBase):
    raw_id_fields = ("ticket", "household", "individual")
