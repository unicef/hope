from .base import DjangoOperator


class ProgramCAPushOperator(DjangoOperator):
    """
    This will push approved programs (programmes)
    from HCT database to CA datahub.
    """

    def execute(self, context):
        pass
