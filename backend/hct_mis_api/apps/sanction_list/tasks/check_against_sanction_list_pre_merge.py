from constance import config

from household.models import Individual
from sanction_list.documents import SanctionListIndividualESDocument


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
                                    {"match": {"dates_of_birth.date": {"query": individual.birth_date}}},
                                ]
                            }
                        }
                    ],
                }
            },
        }

        return query_dict

    @classmethod
    def execute(cls, registration_data_import):
        individuals = registration_data_import.individuals.all()
        duplicate_score = config.SANCTION_LIST_MATCH_SCORE
        document = SanctionListIndividualESDocument

        possible_matches = set()
        for individual in individuals:
            query_dict = cls._get_query_dict(individual)
            query = document.search().from_dict(query_dict)
            query._index = document._index._name

            results = query.execute()
            for individual_hit in results:
                score = individual_hit.meta.score
                if score >= duplicate_score:
                    possible_matches.add(individual)
                    if individual not in possible_matches:
                        individual.sanction_list_possible_match = True

            individual.sanction_list_results = [
                {"hit_id": r.id, "full_name": r.full_name, "score": r.meta.score} for r in results
            ]

        Individual.objects.bulk_update(possible_matches, ("sanction_list_results", "sanction_list_possible_match"))
