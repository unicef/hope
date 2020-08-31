import logging
from pprint import pprint

from constance import config

from household.documents import IndividualDocument
from household.models import Individual
from sanction_list.models import SanctionListIndividual


log = logging.getLogger(__name__)


class CheckAgainstSanctionListPreMergeTask:
    @staticmethod
    def _get_query_dict(individual):
        query_dict = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "dis_max": {
                                "queries": [
                                    {"match": {"full_name": {"query": individual.full_name}}},
                                    {"terms": {"birth_date": [dob.date for dob in individual.dates_of_birth.all()]}},
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
