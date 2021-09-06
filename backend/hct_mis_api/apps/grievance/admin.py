from admin_extra_urls.decorators import button
from django.contrib import admin
from django.contrib.admin import TabularInline

from adminfilters.filters import (
    ChoicesFieldComboFilter,
    RelatedFieldComboFilter,
    TextFieldFilter,
)
from advanced_filters.admin import AdminAdvancedFiltersMixin

from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNote,
    TicketSensitiveDetails,
)
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase


class GrievanceInline(TabularInline):
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


class GrievanceNoteInline(GrievanceInline):
    model = TicketNote


class TicketComplaintInline(GrievanceInline):
    model = TicketComplaintDetails


class TicketSensitiveDetailsInline(GrievanceInline):
    model = TicketSensitiveDetails


@admin.register(GrievanceTicket)
class GrievanceTicketAdmin(AdminAdvancedFiltersMixin, HOPEModelAdminBase):
    inlines = [GrievanceNoteInline, TicketComplaintInline, TicketSensitiveDetailsInline]
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
    pass


@admin.register(TicketHouseholdDataUpdateDetails)
class TicketHouseholdDataUpdateDetailsAdmin(HOPEModelAdminBase):
    pass


@admin.register(TicketIndividualDataUpdateDetails)
class TicketIndividualDataUpdateDetailsAdmin(HOPEModelAdminBase):
    pass


@admin.register(TicketAddIndividualDetails)
class TicketAddIndividualDetailsAdmin(HOPEModelAdminBase):
    pass


@admin.register(TicketDeleteIndividualDetails)
class TicketDeleteIndividualDetailsAdmin(HOPEModelAdminBase):
    pass
