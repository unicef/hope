from .base import DjangoOperator


class RegistrationKoboImportOperator(DjangoOperator):
    """
    Imports project data from Kobo via a REST API, parsing them and creating
    households/individuals in the Registration Datahub. Once finished it will
    update the status of that registration data import instance.
    """

    def execute(self, context):
        from registration_datahub.tasks.rdi_create import RdiXlsxCreateTask

        dag_run = context["dag_run"]
        config_vars = dag_run.conf

        task = RdiXlsxCreateTask()
        task.execute(
            registration_data_import_id=config_vars.get(
                "registration_data_import_id"
            ),
            submission_data=config_vars.get("submission_data"),
            business_area_id=config_vars.get("business_area"),
        )
