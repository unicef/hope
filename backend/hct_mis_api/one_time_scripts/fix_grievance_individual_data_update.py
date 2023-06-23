from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketIndividualDataUpdateDetails,
)


def fix_grievance_individual_data_update() -> None:
    """
    "individualData": {
      "documents_to_edit": [
        {
          "value": {
            "type": "DRIVERS_LICENSE",
            "number": "123123123",
            "country": "BHS",
          },
          "approve_status": false,
          "previous_value": {
            "type": "national_ID",
            "number": "CSH221395"
          }
        }
      ]
    }
    """

    tickets_update_ind_qs = TicketIndividualDataUpdateDetails.objects.exclude(
        ticket__status=GrievanceTicket.STATUS_CLOSED
    )
    print(
        f"Found {tickets_update_ind_qs.count()} tickets. \n Start fixing...",
    )

    for ticket_details in tickets_update_ind_qs:
        update = False

        ind_data = ticket_details.individual_data  # json
        # fix only 'documents' and 'documents_to_edit' lists
        for documents_list in ("documents", "documents_to_edit"):
            docs = ind_data.get(documents_list, [])

            for doc in docs:
                for k in ("value", "previous_value"):
                    if doc_dict := doc.get(k):  # {"type": "drivers_license", "number": "23"}
                        if doc_type := doc_dict.pop("type", None):
                            doc_dict.update({"key": doc_type.lower()})
                            update = True
        if update:
            ticket_details.save(update_fields=["individual_data"])
            print(f"Fixed GrievanceTicket: {ticket_details.ticket.unicef_id}")

    print("Finished fixing.")


def fix_grievance_add_individual_data() -> None:
    """
    "ind_data": {
        'documents': [
            {
                'type': 'BANK_STATEMENT',
                'number': '123123',
            },
            {
                'type': 'NATIONAL_ID',
                'number': '1122',
            }
        ],
    }
    """

    ticket_details_add_new_ind_qs = TicketAddIndividualDetails.objects.exclude(
        ticket__status=GrievanceTicket.STATUS_CLOSED
    )
    print(f"Found {ticket_details_add_new_ind_qs.count()} tickets. \n Start fixing...")

    for ticket_details in ticket_details_add_new_ind_qs:
        update = False

        ind_data = ticket_details.individual_data  # json
        docs = ind_data.get("documents", [])
        for doc in docs:
            if doc_type := doc.pop("type", None):  # {"type": "ADC", "number": "23"}
                doc.update({"key": doc_type.lower()})  # {"key": "adc", "number": "23"}
                update = True
        if update:
            ticket_details.save(update_fields=["individual_data"])
            print(f"Fixed GrievanceTicket: {ticket_details.ticket.unicef_id}")

    print("Finished fixing.")
