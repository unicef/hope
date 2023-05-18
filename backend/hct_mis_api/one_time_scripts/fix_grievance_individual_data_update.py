from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketIndividualDataUpdateDetails,
)


def fix_individual_data_update_details_document_type() -> None:
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

    tickets_qs = TicketIndividualDataUpdateDetails.objects.exclude(ticket__status=GrievanceTicket.STATUS_CLOSED)
    print(
        f"Found {tickets_qs.count()} tickets. \n Start fixing...",
    )

    for ticket_details in tickets_qs:
        update = False

        ind_data = ticket_details.individual_data  # json
        for documents_list in ("documents", "documents_to_edit"):  # fix only 'documents' and 'documents_to_edit' lists
            if docs := ind_data.get(documents_list):
                for doc in docs:
                    for key in ("value", "previous_value"):
                        if doc_value := doc.get(key):  # {"type": "drivers_license", "number": "23"}
                            if doc_type := doc_value.pop("type", None):
                                doc_value.update({"key": doc_type.lower()})
                                update = True
        if update:
            ticket_details.save(update_fields=["individual_data"])
            print(f"Fixed GrievanceTicket: {ticket_details.ticket.unicef_id}")

    print("Finished fixing.")
