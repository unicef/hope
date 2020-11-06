from django.contrib import admin

from grievance.models import (
    GrievanceTicket,
    TicketNotes,
    TicketComplaintDetails,
    TicketSensitiveDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketAddIndividualDetails,
    TicketDeleteIndividualDetails,
)


@admin.register(GrievanceTicket)
class GrievanceTicketAdmin(admin.ModelAdmin):
    pass


@admin.register(TicketNotes)
class TicketNotesAdmin(admin.ModelAdmin):
    pass


@admin.register(TicketComplaintDetails)
class TicketComplaintDetailsAdmin(admin.ModelAdmin):
    pass


@admin.register(TicketSensitiveDetails)
class TicketSensitiveDetailsAdmin(admin.ModelAdmin):
    pass


@admin.register(TicketHouseholdDataUpdateDetails)
class TicketHouseholdDataUpdateDetailsAdmin(admin.ModelAdmin):
    pass


@admin.register(TicketIndividualDataUpdateDetails)
class TicketIndividualDataUpdateDetailsAdmin(admin.ModelAdmin):
    pass


@admin.register(TicketAddIndividualDetails)
class TicketAddIndividualDetailsAdmin(admin.ModelAdmin):
    pass


@admin.register(TicketDeleteIndividualDetails)
class TicketDeleteIndividualDetailsAdmin(admin.ModelAdmin):
    pass
