from .base import DjangoOperator


class PullFromCaDh(DjangoOperator):
    def execute(self, context, **kwargs):
        from cash_assist_datahub.tasks.pull_from_datahub import PullFromDatahubTask

        PullFromDatahubTask().execute()
