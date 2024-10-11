from pathlib import Path

import openpyxl

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.household.services.household_withdraw import HouseholdWithdraw


def mass_withdraw_sudan_hhs() -> None:
    # get the file path to mass_withdraw_sudan_hhs.xlsx
    file_path = Path(__file__).resolve().parent / "files" / "mass_withdraw_sudan_hhs.xlsx"
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    for row in sheet.iter_rows(min_row=2, values_only=True):
        unicef_id = row[0]
        if not unicef_id:
            break
        household = Household.objects.filter(unicef_id=unicef_id, withdrawn=False, program__isnull=False).first()
        tag = row[1]
        if household:
            tickets = GrievanceTicket.objects.belong_household(household)
            tickets = filter(lambda t: t.ticket.status != GrievanceTicket.STATUS_CLOSED, tickets)
            service = HouseholdWithdraw(household)
            service.withdraw(tag=tag)
            service.change_tickets_status(tickets)
