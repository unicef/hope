import logging
from typing import Dict, Iterable, List, Optional, Tuple

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from constance import config

from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketSystemFlaggingDetails,
)
from hct_mis_api.apps.grievance.notifications import GrievanceNotification
from hct_mis_api.apps.household.documents import (
    IndividualDocumentAfghanistan,
    IndividualDocumentOthers,
    IndividualDocumentUkraine,
    get_individual_doc,
)
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_NATIONAL_ID,
    Individual,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.sanction_list.models import SanctionListIndividual
from hct_mis_api.apps.utils.querysets import evaluate_qs

log = logging.getLogger(__name__)


class CheckAgainstSanctionListPreMergeTask:
    @staticmethod
    def _get_query_dict(individual: Individual) -> Dict:
        documents = [
            doc
            for doc in individual.documents.all()
            if doc.type_of_document.title() == "National Identification Number"
        ]
        document_queries = [
            {
                "bool": {
                    "must": [
                        {"match": {"documents.number": doc.document_number}},
                        {
                            "match": {
                                "documents.key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]
                            }
                        },
                        {"match": {"documents.country": getattr(doc.issuing_country, "iso_code3", "")}},
                    ],
                    "boost": 2,
                }
            }
            for doc in documents
        ]
        birth_dates_queries = [
            {"match": {"birth_date": {"query": dob.date, "boost": 1}}} for dob in individual.dates_of_birth.all()
        ]

        queries: List = [
            {"match": {"full_name": {"query": individual.full_name, "boost": 4, "operator": "and"}}},
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

        return query_dict

    @classmethod
    @transaction.atomic
    def execute(
        cls,
        individuals: Optional[Iterable[SanctionListIndividual]] = None,
        registration_data_import: Optional[RegistrationDataImport] = None,
    ) -> None:
        if individuals is None:
            individuals = SanctionListIndividual.objects.all()
        possible_match_score = config.SANCTION_LIST_MATCH_SCORE

        documents: Tuple = (
            (
                IndividualDocumentAfghanistan,
                IndividualDocumentUkraine,
                IndividualDocumentOthers,
            )
            if registration_data_import is None
            else (get_individual_doc(registration_data_import.business_area.slug),)
        )

        tickets_to_create = []
        ticket_details_to_create = []
        tickets_programs = []
        GrievanceTicketProgramThrough = GrievanceTicket.programs.through
        possible_matches = set()
        for individual in individuals:
            for document in documents:
                query_dict = cls._get_query_dict(individual)
                query = document.search().update_from_dict(query_dict)

                results = query.execute()

                for individual_hit in results:
                    score = individual_hit.meta.score
                    if score >= possible_match_score:
                        marked_individual = Individual.objects.filter(id=individual_hit.id).first()
                        if marked_individual:
                            possible_matches.add(marked_individual.id)
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
                                sanction_list_individual=individual,
                            )
                            details_already_exists = TicketSystemFlaggingDetails.objects.filter(
                                golden_records_individual=marked_individual,
                                sanction_list_individual=individual,
                            ).exists()
                            if details_already_exists is False:
                                tickets_to_create.append(ticket)
                                tickets_programs.append(
                                    GrievanceTicketProgramThrough(
                                        grievanceticket=ticket, program_id=marked_individual.program_id
                                    )
                                )
                                ticket_details_to_create.append(ticket_details)

                log.debug(
                    f"SANCTION LIST INDIVIDUAL: {individual.full_name} - reference number: {individual.reference_number}"
                    f" Scores: ",
                )
                log.debug([(r.full_name, r.meta.score) for r in results])
        cache.set("sanction_list_last_check", timezone.now(), None)

        possible_matches_individuals = evaluate_qs(
            Individual.objects.filter(id__in=possible_matches, sanction_list_possible_match=False)
            .select_for_update()
            .order_by("pk")
        )
        possible_matches_individuals.update(sanction_list_possible_match=True)

        not_possible_matches_individuals = evaluate_qs(
            Individual.objects.exclude(id__in=possible_matches)
            .filter(sanction_list_possible_match=True)
            .select_for_update()
            .order_by("pk")
        )
        not_possible_matches_individuals.update(sanction_list_possible_match=False)

        GrievanceTicket.objects.bulk_create(tickets_to_create)
        GrievanceTicketProgramThrough.objects.bulk_create(tickets_programs)
        for ticket in tickets_to_create:
            GrievanceNotification.send_all_notifications(
                GrievanceNotification.prepare_notification_for_ticket_creation(ticket)
            )
        TicketSystemFlaggingDetails.objects.bulk_create(ticket_details_to_create)
