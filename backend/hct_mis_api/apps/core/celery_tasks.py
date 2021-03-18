from hct_mis_api.apps.core.celery import app
from hct_mis_api.apps.core.models import XLSXKoboTemplate
from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import KoboRetriableError


@app.task(bind=True, default_retry_delay=60)
def upload_new_kobo_template_and_update_flex_fields_task_with_retry(self, xlsx_kobo_template_id):
    from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import (
        UploadNewKoboTemplateAndUpdateFlexFieldsTask,
    )
    from datetime import datetime, timedelta

    try:
        UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=xlsx_kobo_template_id)
    except KoboRetriableError as exc:
        one_day_earlier_time = datetime.now() - timedelta(days=1)
        if exc.xlsx_kobo_template_object.first_connection_failed_time > one_day_earlier_time:
            raise self.retry(exc=exc)
        else:
            exc.xlsx_kobo_template_object.status = XLSXKoboTemplate.UNSUCCESSFUL


@app.task
def upload_new_kobo_template_and_update_flex_fields_task(xlsx_kobo_template_id):
    from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import (
        UploadNewKoboTemplateAndUpdateFlexFieldsTask,
    )

    try:
        UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=xlsx_kobo_template_id)
    except KoboRetriableError:
        upload_new_kobo_template_and_update_flex_fields_task_with_retry.delay(xlsx_kobo_template_id)
