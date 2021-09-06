from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin
from django.contrib import admin
from django.contrib.admin import TabularInline

from adminfilters.filters import (
    ChoicesFieldComboFilter,
    RelatedFieldComboFilter,
    TextFieldFilter,
)
from advanced_filters.admin import AdminAdvancedFiltersMixin
from django.core.exceptions import ValidationError
from django.db.transaction import atomic, savepoint, savepoint_commit, savepoint_rollback
from psycopg2._psycopg import IntegrityError
from smart_admin.decorators import smart_register

from hct_mis_api.apps.grievance2.celery_tasks import restore_backup
from hct_mis_api.apps.grievance2.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNote,
    TicketSensitiveDetails,
    TicketNeedsAdjudicationDetails,
    TicketSystemFlaggingDetails,
    TicketPositiveFeedbackDetails,
    TicketNegativeFeedbackDetails,
    TicketReferralDetails,
)
from hct_mis_api.apps.grievance2 import models as models_backup
from hct_mis_api.apps.grievance import models as models_destination
from hct_mis_api.apps.utils.admin import HOPEModelAdminBase





@admin.register(GrievanceTicket)
class GrievanceTicketAdmin(ExtraUrlMixin, AdminAdvancedFiltersMixin, HOPEModelAdminBase):
    @button()
    def copy_to_old_db_async(self, request):
        restore_backup.delay()
        self.message_user(request, "Copy started")

    @button()
    def copy_to_old_db(self, request):
        restore_backup()
        self.message_user(request, "Copy started")


@smart_register(
    (
        TicketNote,
        TicketComplaintDetails,
        TicketSensitiveDetails,
        TicketHouseholdDataUpdateDetails,
        TicketIndividualDataUpdateDetails,
        TicketAddIndividualDetails,
        TicketDeleteIndividualDetails,
        TicketSystemFlaggingDetails,
        TicketNeedsAdjudicationDetails,
        TicketPositiveFeedbackDetails,
        TicketNegativeFeedbackDetails,
        TicketReferralDetails,
    )
)
class TicketNoteAdmin(HOPEModelAdminBase):
    pass
