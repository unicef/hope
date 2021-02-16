
from .base import DjangoOperator


class GetRapidProVerificationsOperator(DjangoOperator):
    def try_execute(self, context, **kwargs):
        from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import CheckRapidProVerificationTask
        CheckRapidProVerificationTask().execute()
