import logging

from django.contrib.auth import get_user_model

from sentry_sdk import configure_scope

from hct_mis_api.apps.accountability.models import Survey
from hct_mis_api.apps.accountability.services.export_survey_sample_service import (
    ExportSurveySampleService,
)
from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

logger = logging.getLogger(__name__)


@app.task
@log_start_and_end
@sentry_tags
def export_survey_sample_task(survey_id, user_id):
    try:
        survey = Survey.objects.get(id=survey_id)
        user = get_user_model().objects.get(pk=user_id)

        with configure_scope() as scope:
            scope.set_tag("business_area", survey.business_area)

            service = ExportSurveySampleService(survey, user)
            service.export_sample()
            service.send_email()
    except Exception as e:
        logger.exception(e)
        raise
