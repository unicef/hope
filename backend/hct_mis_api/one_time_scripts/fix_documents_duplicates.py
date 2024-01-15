import logging

from django.db.models import Count

from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.models import Document, Individual

logger = logging.getLogger(__name__)


def fix_documents_duplicates() -> None:
    logger.info("Starting fix_documents_duplicates")
    documents = (
        Document.objects.filter(status="VALID")
        .values("document_number", "type_id", "country__name")
        .annotate(count=Count("document_number"))
        .filter(count__gt=1)
    )
    logger.info(f"Found {len(documents)}")
    documents_to_update = []
    for document in documents:
        individuals = Individual.objects.filter(
            documents__document_number=document["document_number"],
            documents__type_id=document["type_id"],
            documents__status=Document.STATUS_VALID,
        )
        main_individual = individuals[0]
        possible_duplicates = individuals[1:]

        business_area = main_individual.business_area
        registration_data_import = main_individual.registration_data_import

        ticket_already_exists = (
            TicketNeedsAdjudicationDetails.objects.exclude(ticket__status=GrievanceTicket.STATUS_CLOSED)
            .filter(golden_records_individual__in=individuals, possible_duplicates__in=individuals)
            .exists()
        )
        if ticket_already_exists:
            continue

        household = main_individual.household
        admin_level_2 = household.admin2 if household else None
        area = household.village if household else ""

        logger.info(f"Creating ticket for {main_individual.unicef_id}")
        ticket = GrievanceTicket.objects.create(
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            business_area=business_area,
            admin2=admin_level_2,
            area=area,
            registration_data_import=registration_data_import,
        )

        ticket_details = TicketNeedsAdjudicationDetails.objects.create(
            ticket=ticket,
            golden_records_individual=main_individual,
            possible_duplicate=possible_duplicates[0],
            is_multiple_duplicates_version=True,
            selected_individual=None,
            extra_data={},
            score_min=0.0,
            score_max=0.0,
        )
        logger.info(f"Created GrievanceTicket [{ticket.id}] TicketNeedsAdjudicationDetails [{ticket_details.id}]")

        ticket_details.possible_duplicates.add(*possible_duplicates)
        documents_to_update.append(document["document_number"])
    logger.info(f"Updating document's status for numbers {documents_to_update}")
    Document.objects.filter(document_number__in=documents_to_update, status=Document.STATUS_VALID).update(
        status=Document.STATUS_PENDING
    )
    logger.info("Finished updating document's")
