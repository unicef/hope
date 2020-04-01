from .base import DjangoOperator


class RegistrationDataPullOperator(DjangoOperator):
    """
    This is when the user merges to population an approved registration data
    import. This will copy the data over (taking care of parsing etc.) from
    registration datahub to the HCT database (golden record). Once finished it
    will update the status of that registration data import
    instance (to 'merged').
    """

    def execute(self, context):
        pass
