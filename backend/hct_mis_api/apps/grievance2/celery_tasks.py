import logging

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.grievance import models as models_destination
from hct_mis_api.apps.grievance2 import models as models_backup


def copy_model_object(model_object, model):
    model_dict = {}
    model_dict.update(model_object.__dict__)
    del model_dict["_state"]
    return model(**model_dict)


logger = logging.getLogger(__name__)


@app.task()
def restore_backup():
    try:
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
    except Exception as e:
        logger.exception(e)
