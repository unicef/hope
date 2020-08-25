
from .base import DjangoOperator


class GetRapidProVerificationsOperator(DjangoOperator):
    def execute(self, context, **kwargs):
        from payment.tasks.CheckRapidProVerificationTask import CheckRapidProVerificationTask
        CheckRapidProVerificationTask().execute()
