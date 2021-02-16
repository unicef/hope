from .base import DjangoOperator


class PullFromErpDh(DjangoOperator):
    def try_execute(self, context, **kwargs):
        from hct_mis_api.apps.erp_datahub.tasks.pull_from_erp_datahub import (
            PullFromErpDatahubTask,
        )

        PullFromErpDatahubTask().execute()
