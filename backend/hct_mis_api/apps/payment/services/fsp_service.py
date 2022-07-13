from hct_mis_api.apps.payment.models import FinancialServiceProvider


class FSPService:
    def __init__(self, fsp: FinancialServiceProvider) -> None:
        self.fsp = fsp

    def create(self):
        pass
