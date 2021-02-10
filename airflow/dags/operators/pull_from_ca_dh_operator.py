from .base import DjangoOperator


class PullFromCaDh(DjangoOperator):
    def try_execute(self, context, **kwargs):
        from hct_mis_api.apps.cash_assist_datahub.tasks.pull_from_datahub import PullFromDatahubTask

        PullFromDatahubTask().execute()
