from .base import DjangoOperator


class UploadNewKoboTemplateAndUpdateFlexFieldsOperator(DjangoOperator):
    def execute(self, context):
        from hct_mis_api.apps.core.tasks.upload_new_template_and_update_flex_fields import (
            UploadNewKoboTemplateAndUpdateFlexFieldsTask,
        )

        dag_run = context["dag_run"]
        config_vars = dag_run.conf

        task = UploadNewKoboTemplateAndUpdateFlexFieldsTask()
        task.execute(
            xlsx_kobo_template_id=config_vars.get("xlsx_kobo_template_id")
        )
