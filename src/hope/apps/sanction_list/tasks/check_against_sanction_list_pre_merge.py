import logging
from typing import Any, Iterable

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from constance import config

from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketSystemFlaggingDetails,
)
from hope.apps.grievance.notifications import GrievanceNotification
from hope.apps.household.documents import get_individual_doc
from hope.apps.household.models import (
    IDENTIFICATION_TYPE_NATIONAL_ID,
    Individual,
)
from hope.apps.program.models import Program
from hope.apps.registration_data.models import RegistrationDataImport
from hope.apps.sanction_list.models import SanctionListIndividual
from hope.apps.utils.querysets import evaluate_qs

log = logging.getLogger(__name__)


def _get_query_dict(sanction_list_individual: SanctionListIndividual, individuals_ids: list[str] | None) -> dict:
    documents = [
        doc
        for doc in sanction_list_individual.documents.all()
        if doc.type_of_document.title() == "National Identification Number"
    ]
    document_queries = [
        {
            "bool": {
                "must": [
                    {"match": {"documents.number": doc.document_number}},
                    {"match": {"documents.key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]}},
                    {"match": {"documents.country": getattr(doc.issuing_country, "iso_code3", "")}},
                ],
                "boost": 2,
            }
        }
        for doc in documents
    ]
    birth_dates_queries = [
        {"match": {"birth_date": {"query": dob.date, "boost": 1}}}
        for dob in sanction_list_individual.dates_of_birth.all()
    ]
    possible_names = [
        sanction_list_individual.full_name,
    ]
    possible_names += [alias_name.name for alias_name in sanction_list_individual.alias_names.all()]
    queries: list = [
        {
            "match": {
                "full_name": {
                    "query": name,
                    "boost": 4,
                    "operator": "and",
                }
            }
        }
        for name in possible_names
    ]

    queries.extend(document_queries)
    queries.extend(birth_dates_queries)

    query_dict = {
        "size": 10000,
        "query": {
            "bool": {
                "minimum_should_match": 1,
                "should": queries,
            },
        },
        "_source": ["id", "full_name"],
    }
    if individuals_ids:
        query_dict["query"]["bool"]["filter"] = [{"terms": {"id": [str(ind_id) for ind_id in individuals_ids]}}]  # type: ignore
    return query_dict


def _generate_ticket(
    marked_individual: Individual,
    registration_data_import: RegistrationDataImport | None,
    sanction_list_individual: SanctionListIndividual,
) -> tuple[GrievanceTicket, TicketSystemFlaggingDetails, Any] | None:
    GrievanceTicketProgramThrough = GrievanceTicket.programs.through
    household = marked_individual.household
    admin_level_2 = getattr(household, "admin2", None)
    area = getattr(household, "village", "")
    ticket = GrievanceTicket(
        category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
        business_area=marked_individual.business_area,
        admin2=admin_level_2,
        area=area,
        registration_data_import=registration_data_import,
        household_unicef_id=household.unicef_id if household else "",
    )
    ticket_details = TicketSystemFlaggingDetails(
        ticket=ticket,
        golden_records_individual=marked_individual,
        sanction_list_individual=sanction_list_individual,
    )
    details_already_exists = TicketSystemFlaggingDetails.objects.filter(
        golden_records_individual=marked_individual,
        sanction_list_individual=sanction_list_individual,
    ).exists()
    if details_already_exists is True:
        return None
    return (
        ticket,
        ticket_details,
        GrievanceTicketProgramThrough(
            grievanceticket=ticket,
            program_id=marked_individual.program_id,
        ),
    )


@transaction.atomic
def check_against_sanction_list_pre_merge(
    program_id: str,
    individuals_ids: list[str] | None = None,
    sanction_list_individuals: Iterable[SanctionListIndividual] | None = None,
    registration_data_import: RegistrationDataImport | None = None,
) -> None:
    program = Program.objects.get(id=program_id)
    sanction_lists = program.sanction_lists
    if not sanction_lists.exists():  # pragma: no cover
        log.debug(f"No sanction lists found for program {program_id}. Skipping check against sanction list.")
        return
    sanction_list_individuals_queryset = SanctionListIndividual.objects.filter(
        sanction_list__in=sanction_lists.all(),
        active=True,
    )
    if sanction_list_individuals is not None:  # pragma: no cover
        sanction_list_individuals_queryset = sanction_list_individuals_queryset.filter(
            id__in=sanction_list_individuals,
        )
    if not individuals_ids:
        individuals_ids = Individual.objects.filter(program_id=program_id).values_list("id", flat=True)  # type: ignore
    individuals_ids = [str(ind_id) for ind_id in individuals_ids]
    possible_match_score = config.SANCTION_LIST_MATCH_SCORE
    documents: tuple = (get_individual_doc(program.business_area.slug),)

    tickets_to_create = []
    ticket_details_to_create = []
    tickets_programs = []
    possible_matches = set()
    for sanction_list_individual in sanction_list_individuals_queryset:
        for document in documents:
            query_dict = _get_query_dict(sanction_list_individual, individuals_ids=individuals_ids)
            query = document.search().update_from_dict(query_dict)

            results = query.execute()
            for individual_hit in results:
                # Skip if the individual is not in the provided IDs
                # This is filtered in ES query, but we double-check here
                if individuals_ids and individual_hit.id not in individuals_ids:
                    continue
                score = individual_hit.meta.score
                if score < possible_match_score:
                    continue
                marked_individual = Individual.objects.filter(id=individual_hit.id).first()
                if marked_individual.program_id != program.id:
                    log.debug(
                        f"Skipping individual {marked_individual.unicef_id} with ID {marked_individual.id} "
                        f"as it does not belong to program {program_id}."
                    )
                    continue

                if not marked_individual:
                    log.debug(f"Skipping individual with ID {individual_hit.id} as it does not exist in the database.")
                    continue
                possible_matches.add(marked_individual.id)
                tickets_info = _generate_ticket(
                    marked_individual,
                    registration_data_import,
                    sanction_list_individual,
                )
                if tickets_info:
                    ticket, ticket_details, tickets_program = tickets_info
                    tickets_to_create.append(ticket)
                    ticket_details_to_create.append(ticket_details)
                    tickets_programs.append(tickets_program)

            log.debug(
                f"SANCTION LIST INDIVIDUAL: {sanction_list_individual.full_name} - reference number: {sanction_list_individual.reference_number}"
                f" Scores: ",
            )
            log.debug([(r.full_name, r.meta.score) for r in results])
    cache.set("sanction_list_last_check", timezone.now(), None)

    possible_matches_individuals = evaluate_qs(
        Individual.objects.filter(id__in=possible_matches, sanction_list_possible_match=False, program_id=program.id)
        .select_for_update()
        .order_by("pk")
    )
    possible_matches_individuals.update(sanction_list_possible_match=True)

    if not individuals_ids:
        # If we not pass individuals_ids, it means we want to check all individuals in the program.
        # So we know that individuals which are not found in the possible matches need to be marked as not possible matches.
        not_possible_matches_individuals = evaluate_qs(
            Individual.objects.exclude(id__in=possible_matches)
            .filter(sanction_list_possible_match=True)
            .select_for_update()
            .order_by("pk")
        )
        not_possible_matches_individuals.update(sanction_list_possible_match=False)

    GrievanceTicket.objects.bulk_create(tickets_to_create)
    GrievanceTicketProgramThrough = GrievanceTicket.programs.through
    GrievanceTicketProgramThrough.objects.bulk_create(tickets_programs)
    for ticket in tickets_to_create:
        GrievanceNotification.send_all_notifications(
            GrievanceNotification.prepare_notification_for_ticket_creation(ticket)
        )
    TicketSystemFlaggingDetails.objects.bulk_create(ticket_details_to_create)
