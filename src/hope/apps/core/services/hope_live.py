class HopeLiveService:
    API_URL = ""
    API_KEY = ""

    ACTION_RDI_MERGED = "rdi_fully_imported"
    ACTION_PAYMENT_RECONCILED = "payment_reconciled"
    ACTION_PAYMENT_PLAN_APPROVED = "payment_plan_approved"
    ACTION_PROGRAM_OPENED = "program_opened"
    ACTION_PROGRAM_CLOSED = "program_closed"

    def notify(self, data_dict: dict):
        pass
