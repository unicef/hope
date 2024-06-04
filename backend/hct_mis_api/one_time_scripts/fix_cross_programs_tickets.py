import logging

from django.db import transaction
from django.db.models import F

from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.models import Document
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import (
    HardDocumentDeduplication,
)

logger = logging.getLogger(__name__)


def fix_cross_programs_tickets() -> None:
    tickets_ids = list(
        TicketNeedsAdjudicationDetails.objects.filter(possible_duplicates__program_id__isnull=False)
        .exclude(golden_records_individual__program_id=F("possible_duplicates__program_id"))
        .exclude(ticket__status=GrievanceTicket.STATUS_CLOSED)
        .values_list("id", flat=True)
        .distinct()
    )
    logger.info(f"Found {len(tickets_ids)} tickets")
    documents_ids = list(
        Document.objects.filter(
            individual__ticket_duplicates__in=tickets_ids,
            status=Document.STATUS_NEED_INVESTIGATION,
        )
        .values_list("id", flat=True)
        .distinct()
    )
    programs_ids = (
        Document.objects.filter(
            individual__ticket_duplicates__in=tickets_ids,
            status=Document.STATUS_NEED_INVESTIGATION,
        )
        .values_list("individual__program_id", flat=True)
        .distinct()
    )

    programs = (
        Program.objects.filter(id__in=programs_ids)
        .select_related("business_area")
        .only("id", "name", "business_area__name")
    )

    logger.info(f"Found {programs.count()} programs")

    for program in programs:
        try:
            with transaction.atomic():
                logger.info(f"Fixing program {program.name} in business area {program.business_area.name}")

                updated_documents = Document.objects.filter(
                    id__in=documents_ids, individual__program_id=program.id
                ).update(status=Document.STATUS_PENDING)
                logger.info(f"Updated {updated_documents} documents")

                updated_tickets = GrievanceTicket.objects.filter(
                    needs_adjudication_ticket_details__id__in=tickets_ids,
                    needs_adjudication_ticket_details__possible_duplicates__program_id=program.id,
                ).update(
                    status=GrievanceTicket.STATUS_CLOSED, comments="Invalid ticket. Closed automatically by the system."
                )
                logger.info(f"Closed {updated_tickets} tickets")

                documents = Document.objects.filter(
                    id__in=documents_ids, individual__program_id=program.id, status=Document.STATUS_PENDING
                )
                HardDocumentDeduplication().deduplicate(documents)

                ind_ids = list(
                    Document.objects.filter(
                        id__in=documents_ids,
                        individual__program_id=program.id,
                        status=Document.STATUS_NEED_INVESTIGATION,
                    ).values_list("individual", flat=True)
                )
                tickets = GrievanceTicket.objects.filter(
                    needs_adjudication_ticket_details__possible_duplicates__in=ind_ids,
                    status=GrievanceTicket.STATUS_NEW,
                    registration_data_import_id__isnull=True,
                ).annotate(
                    rdi_id=F("needs_adjudication_ticket_details__possible_duplicates__registration_data_import_id")
                )
                logger.info(f"Created {tickets.count()} tickets")
                for ticket in tickets:
                    ticket.registration_data_import_id = ticket.rdi_id
                GrievanceTicket.objects.bulk_update(tickets, ["registration_data_import_id"])
        except Exception as e:
            logger.exception(e)
