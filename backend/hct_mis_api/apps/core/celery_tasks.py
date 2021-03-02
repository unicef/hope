from hct_mis_api.apps.core.celery import app


@app.task
def upload_new_kobo_template_and_update_flex_fields_task(xlsx_kobo_template_id):
    from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import (
        UploadNewKoboTemplateAndUpdateFlexFieldsTask,
    )

    UploadNewKoboTemplateAndUpdateFlexFieldsTask().execute(xlsx_kobo_template_id=xlsx_kobo_template_id)
