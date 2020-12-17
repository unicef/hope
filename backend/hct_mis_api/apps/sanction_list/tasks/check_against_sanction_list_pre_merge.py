import logging

from constance import config
from django.utils import timezone

from grievance.models import TicketSystemFlaggingDetails, GrievanceTicket
from household.documents import IndividualDocument
from household.models import Individual, IDENTIFICATION_TYPE_NATIONAL_ID
from sanction_list.models import SanctionListIndividual

log = logging.getLogger(__name__)


class CheckAgainstSanctionListPreMergeTask:
    @staticmethod
    def _get_query_dict(individual):
        documents_numbers = [
            doc.document_number
            for doc in individual.documents.all()
            if doc.type_of_document.title() == "National Identification Number"
        ]
        document_queries = [
            {
                "bool": {
                    "must": [
                        {"match": {"documents.number": number}},
                        {"match": {"documents.type": IDENTIFICATION_TYPE_NATIONAL_ID}},
                    ],
                }
            }
            for number in documents_numbers
        ]

        queries = [
            {
                "multi_match": {
                    "query": individual.full_name,
                    "fields": [
                        "full_name",
                        "first_name",
                        "second_name",
                        "third_name",
                        "fourth_name",
                        "alias_name.name",
                    ],
                    "boost": 2.0,
                }
            },
            {"terms": {"birth_date": [dob.date for dob in individual.dates_of_birth.all()]}},
        ]
        queries.extend(document_queries)

        query_dict = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "dis_max": {
                                "queries": queries,
                                "tie_breaker": 1.0,
                            }
                        }
                    ],
                }
            },
        }

        return query_dict

    @classmethod
    def execute(cls, individuals=None):
        if individuals is None:
            individuals = SanctionListIndividual.objects.all()
        possible_match_score = config.SANCTION_LIST_MATCH_SCORE
        document = IndividualDocument

        tickets_to_create = []
        ticket_details_to_create = []
        possible_matches = set()
        for individual in individuals:
            query_dict = cls._get_query_dict(individual)
            query = document.search().from_dict(query_dict)
            query._index = document._index._name

            results = query.execute()
            for individual_hit in results:
                score = individual_hit.meta.score
                if score >= possible_match_score:
                    marked_individual = Individual.objects.filter(id=individual_hit.id).first()
                    if marked_individual:
                        possible_matches.add(marked_individual.id)
                        ticket = GrievanceTicket(
                            category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
                            business_area=marked_individual.business_area,
                        )
                        ticket_details = TicketSystemFlaggingDetails(
                            ticket=ticket,
                            golden_records_individual=marked_individual,
                            sanction_list_individual=individual,
                        )
                        tickets_to_create.append(ticket)
                        ticket_details_to_create.append(ticket_details)

            print(
                f"SANCTION LIST INDIVIDUAL: {individual.full_name} - reference number: {individual.reference_number}"
                f" Scores: ",
            )
            print([(r.full_name, r.meta.score) for r in results])

        Individual.objects.filter(id__in=possible_matches).update(
            sanction_list_possible_match=True, sanction_list_last_check=timezone.now()
        )
        Individual.objects.exclude(id__in=possible_matches).update(
            sanction_list_possible_match=False, sanction_list_last_check=timezone.now()
        )

        GrievanceTicket.objects.bulk_create(tickets_to_create)
        TicketSystemFlaggingDetails.objects.bulk_create(ticket_details_to_create)
