from .base import DjangoOperator


class DeduplicateAndCheckAgainstSanctionsListOperator(DjangoOperator):
    def execute(self, context):
        from grievance.tasks.deduplicate_and_check_sanctions import (
            DeduplicateAndCheckAgainstSanctionsListTask,
        )

        dag_run = context["dag_run"]
        config_vars = dag_run.conf

        should_populate_index = config_vars.get("should_populate_index")
        registration_data_import_id = config_vars.get(
            "registration_data_import_id"
        )
        individuals_ids = config_vars.get("individuals_ids")

        task = DeduplicateAndCheckAgainstSanctionsListTask()
        task.execute(
            should_populate_index, registration_data_import_id, individuals_ids
        )
