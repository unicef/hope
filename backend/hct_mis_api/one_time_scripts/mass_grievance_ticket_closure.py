import os
from typing import Generator

from hct_mis_api.apps.grievance.models import GrievanceTicket


def chunks(file_name: str, size: int = 1000) -> Generator:
    with open(file_name) as f:
        while content := f.readline():
            for _ in range(size - 1):
                content += f.readline()

            yield content.splitlines()


def close_tickets() -> None:
    tickets_to_close = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files", "tickets_to_close.txt")
    split_files = chunks(tickets_to_close)
    tickets_to_update = []
    updated_count = 0

    for chunk in split_files:
        for ticket in GrievanceTicket.objects.filter(unicef_id__in=chunk):
            ticket.status = GrievanceTicket.STATUS_CLOSED
            ticket.extras["reason"] = "Afghanistan request: 1 May 2023"
            tickets_to_update.append(ticket)

        GrievanceTicket.objects.bulk_update(tickets_to_update, ["status", "extras"])
        updated_count += len(tickets_to_update)
        tickets_to_update = []
        print(f"{updated_count} tickets were updated")
