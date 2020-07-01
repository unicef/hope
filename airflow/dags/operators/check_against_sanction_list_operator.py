from .base import DjangoOperator


class CheckAgainstSanctionListOperator(DjangoOperator):
    def execute(self, context):
        from sanction_list.tasks.check_against_sanction_list import (
            CheckAgainstSanctionListTask,
        )

        dag_run = context["dag_run"]
        config_vars = dag_run.conf

        task = CheckAgainstSanctionListTask()
        task.execute(uploaded_file_id=config_vars.get("uploaded_file_id"))
