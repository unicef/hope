from .base import DjangoOperator


class RegistrationKoboImportOperator(DjangoOperator):
    """
    Imports project data from Kobo via a REST API, parsing them and creating
    households/individuals in the Registration Datahub. Once finished it will
    update the status of that registration data import instance.
    """

    def execute(self, context):
        pass
