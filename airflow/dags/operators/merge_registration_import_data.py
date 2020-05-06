from .base import DjangoOperator


class MergeRegistrationImportDataOperator(DjangoOperator):
    def execute(self, context, **kwargs):
        from registration_datahub.tasks.rdi_merge import RdiMergeTask

        dag_run = context["dag_run"]
        config_vars = dag_run.conf
        registration_data_import_id = config_vars.get(
            "registration_data_import_id"
        )
        RdiMergeTask().execute(registration_data_import_id)
