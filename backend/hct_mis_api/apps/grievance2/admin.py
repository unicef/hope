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


def copy_model_object(model_object, model):
    model_dict = {}
    model_dict.update(model_object.__dict__)
    del model_dict["_state"]
    return model(**model_dict)


@admin.register(GrievanceTicket)
class GrievanceTicketAdmin(ExtraUrlMixin, AdminAdvancedFiltersMixin, HOPEModelAdminBase):
    @button()
    def copy_to_old_db(self, request):
        models = [
            "GrievanceTicket",
            "GrievanceTicketThrough",
            "TicketNote",
            "TicketComplaintDetails",
            "TicketSensitiveDetails",
            "TicketHouseholdDataUpdateDetails",
            "TicketIndividualDataUpdateDetails",
            "TicketAddIndividualDetails",
            "TicketDeleteIndividualDetails",
            "TicketSystemFlaggingDetails",
            "TicketNeedsAdjudicationDetails",
            "TicketPositiveFeedbackDetails",
            "TicketNegativeFeedbackDetails",
            "TicketReferralDetails",
        ]
        for model_name in models:
            model_backup = getattr(models_backup, model_name)
            model_destination = getattr(models_destination, model_name)
            for obj_backup in model_backup.objects.all():
                try:
                    obj_destination = copy_model_object(obj_backup, model_destination)
                    obj_destination.save()
                except ValidationError:
                    pass
                except Exception as e:
                    if 'is not present in table "household_individual"' in str(e):
                        pass
                    elif 'is not present in table "household_household"' in str(e):
                        pass
                    else:
                        raise


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
