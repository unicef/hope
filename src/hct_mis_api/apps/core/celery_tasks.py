import logging
from functools import wraps
from typing import Any, Callable

from django.db import transaction

from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.models import XLSXKoboTemplate
from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import (
    KoboRetriableError,
)
from hct_mis_api.apps.utils.logs import log_start_and_end
from hct_mis_api.apps.utils.sentry import sentry_tags

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
                logger.exception(e)

        return app.task(*self.task_args, **self.task_kwargs)(wrapper_func)


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
        exc.xlsx_kobo_template_object.status = XLSXKoboTemplate.UNSUCCESSFUL
    except Exception as e:
        logger.warning(e)
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
