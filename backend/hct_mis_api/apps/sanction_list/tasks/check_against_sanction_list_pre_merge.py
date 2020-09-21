import logging

from constance import config

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
        query_dict = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "dis_max": {
                                "queries": [
                                    {"match": {"full_name": {"query": individual.full_name}}},
                                    {"terms": {"birth_date": [dob.date for dob in individual.dates_of_birth.all()]}},
                                    {"terms": {"documents.number": documents_numbers}},
                                    {
                                        "terms": {
                                            "documents.type": [
                                                IDENTIFICATION_TYPE_NATIONAL_ID for _ in documents_numbers
                                            ]
                                        }
                                    },
                                ]
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

        possible_matches = set()
        for individual in individuals:
            query_dict = cls._get_query_dict(individual)
            query = document.search().from_dict(query_dict)
            query._index = document._index._name

            results = query.execute()
            for individual_hit in results:
                score = individual_hit.meta.score
                if score >= possible_match_score:
                    possible_matches.add(individual_hit.id)

            log.info(
                f"SANCTION LIST INDIVIDUAL: {individual.full_name} - reference number: {individual.reference_number}"
                f"Scores: ",
            )
            log.info([(r.full_name, r.meta.score) for r in results])

        Individual.objects.filter(id__in=possible_matches).update(sanction_list_possible_match=True)
        Individual.objects.exclude(id__in=possible_matches).update(sanction_list_possible_match=False)
