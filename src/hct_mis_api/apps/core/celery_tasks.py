import csv
import logging
import os
import tempfile
from datetime import datetime
from functools import wraps
from typing import Any, Callable

from django.db import transaction
from django.utils import timezone

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.models import StorageFile, XLSXKoboTemplate
from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import (
    KoboRetriableError,
)
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.household.models import (
    COLLECT_TYPE_SIZE_ONLY,
    HEAD,
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    IDENTIFICATION_TYPE_TAX_ID,
    MALE,
    ROLE_PRIMARY,
    BankAccountInfo,
    Document,
    DocumentType,
    Household,
    Individual,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.targeting.services.targeting_stats_refresher import refresh_stats
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.models import MergeStatusModel
from hct_mis_api.apps.utils.sentry import sentry_tags, set_sentry_business_area_tag

logger = logging.getLogger(__name__)


class transaction_celery_task:  # used as decorator
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.task_args = args
        self.task_kwargs = kwargs

    def __call__(self, func: Callable) -> Any:
        @wraps(func)
        def wrapper_func(*args: Any, **kwargs: Any) -> None:
            try:
                with transaction.atomic():
                    return func(*args, **kwargs)
            except Exception as e:
                logger.error(e)

        task_func = app.task(*self.task_args, **self.task_kwargs)(wrapper_func)
        return task_func


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def upload_new_kobo_template_and_update_flex_fields_task_with_retry(self: Any, xlsx_kobo_template_id: str) -> None:
    try:
        from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import (
            UploadNewKoboTemplateAndUpdateFlexFieldsTask,
        )

        UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=xlsx_kobo_template_id)
    except KoboRetriableError as exc:
        from datetime import timedelta

        from django.utils import timezone

        one_day_earlier_time = timezone.now() - timedelta(days=1)
        if exc.xlsx_kobo_template_object.first_connection_failed_time > one_day_earlier_time:
            logger.exception(exc)
            raise self.retry(exc=exc)
        else:
            exc.xlsx_kobo_template_object.status = XLSXKoboTemplate.UNSUCCESSFUL
    except Exception as e:
        logger.exception(e)
        raise


@app.task(bind=True, default_retry_delay=60, max_retries=3)
@log_start_and_end
@sentry_tags
def upload_new_kobo_template_and_update_flex_fields_task(self: Any, xlsx_kobo_template_id: str) -> None:
    try:
        from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import (
            UploadNewKoboTemplateAndUpdateFlexFieldsTask,
        )

        UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=xlsx_kobo_template_id)
    except KoboRetriableError:
        upload_new_kobo_template_and_update_flex_fields_task_with_retry.delay(xlsx_kobo_template_id)
    except Exception as e:
        logger.exception(e)
        raise self.retry(exc=e)
