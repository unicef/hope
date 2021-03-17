from hct_mis_api.apps.core.celery import app


@app.task
def upload_new_kobo_template_and_update_flex_fields_task(xlsx_kobo_template_id):
    from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import (
        UploadNewKoboTemplateAndUpdateFlexFieldsTask,
    )

    UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=xlsx_kobo_template_id)


@app.task
def check_periodically_connection_failed_tasks():
    from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import (
        UploadNewKoboTemplateAndUpdateFlexFieldsTask,
    )
    from datetime import datetime, timedelta
    from hct_mis_api.apps.core.models import XLSXKoboTemplate

    one_day_earlier_time = datetime.now() - timedelta(days=1)
    template = (
        XLSXKoboTemplate.objects.filter(
            first_connection_failed_time__gt=one_day_earlier_time, status=XLSXKoboTemplate.CONNECTION_FAILED
        )
        .order_by("created_at")
        .first()
    )
    UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=template.id)
