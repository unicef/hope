from .base import DjangoOperator


class CashPlanPullOperator(DjangoOperator):
    """
    This will pull both (new & completed) cash plans + all their associated
    payment records from the CA datahub to HCT database.
    """

    def try_execute(self, context):
        pass
