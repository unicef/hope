from django.contrib import admin

from adminfilters.filters import (
    ChoicesFieldComboFilter,
    RelatedFieldComboFilter,
    TextFieldFilter,
)

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


@admin.register(GrievanceTicket)
class GrievanceTicketAdmin(HOPEModelAdminBase):
    list_display = ("created_at", "created_by", "assigned_to", "status", "category")
    raw_id_fields = ("created_by", "assigned_to")
    list_filter = (
        ("status", ChoicesFieldComboFilter),
        ("category", ChoicesFieldComboFilter),
        ("business_area", RelatedFieldComboFilter),
        TextFieldFilter.factory("created_by__username__istartswith"),
        TextFieldFilter.factory("assigned_to__username__istartswith"),
        "updated_at",
    )
    readonly_fields = ("unicef_id",)


@admin.register(TicketNote)
class TicketNoteAdmin(HOPEModelAdminBase):
    pass


@admin.register(TicketComplaintDetails)
class TicketComplaintDetailsAdmin(HOPEModelAdminBase):
    pass


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
