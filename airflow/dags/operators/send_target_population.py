from .base import DjangoOperator


class SendTargetPopulationOperator(DjangoOperator):
    def execute(self, context, **kwargs):
        from mis_datahub.tasks.send_tp_to_datahub import SendTPToDatahubTask

        SendTPToDatahubTask().execute()
