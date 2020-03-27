from .base import DjangoOperator


class RegistrationXLSXImportOperator(DjangoOperator):
    """
    Works on valid XLSX files, parsing them and creating households/individuals
    in the Registration Datahub. Once finished it will update the status of
    that registration data import instance.
    """

    def execute(self, context):
        pass
