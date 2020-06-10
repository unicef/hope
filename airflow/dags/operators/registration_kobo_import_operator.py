from .base import DjangoOperator


class RegistrationKoboImportOperator(DjangoOperator):
    """
    Imports project data from Kobo via a REST API, parsing them and creating
    households/individuals in the Registration Datahub. Once finished it will
    update the status of that registration data import instance.
    """

    def execute(self, context):
        from registration_datahub.tasks.rdi_create import RdiKoboCreateTask

        dag_run = context["dag_run"]
        config_vars = dag_run.conf

        task = RdiKoboCreateTask()
        task.execute(
            registration_data_import_id=config_vars.get(
                "registration_data_import_id"
            ),
            import_data_id=config_vars.get("import_data_id"),
            business_area_id=config_vars.get("business_area"),
        )
