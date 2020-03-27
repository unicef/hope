from .base import DjangoOperator


class TargetPopulationCAPushOperator(DjangoOperator):
    """
    This will take a finalized target population and push to CA datahub the
    households and any other relevant data necessary.
    """

    def execute(self, context):
        pass
