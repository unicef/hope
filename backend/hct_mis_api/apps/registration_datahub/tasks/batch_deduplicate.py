from django.forms import model_to_dict

from registration_datahub.documents import ImportedIndividualDocument
from registration_datahub.models import (
    RegistrationDataImportDatahub,
    ImportedIndividual,
)


class BatchDeduplicate:
    # 1. after successful RDI populate elasticsearch (that's done in RDI Task)
    # 2. for each individual from RDI call elasticsearch more_like_this query
    #  to get similar objects
    # 3. Check scoring and make actions based on the score

    # this should be a constant that can be set in django admin
    MIN_SCORE = 0.5

    def __init__(
        self, registration_data_import_datahub: RegistrationDataImportDatahub
    ):
        self.registration_data_import_datahub = registration_data_import_datahub

    def deduplicate(self):
        individuals = ImportedIndividual.objects.filter(
            registration_data_import=self.registration_data_import_datahub
        )
        for individual in individuals:
            fields_names = [
                "given_name",
                "full_name",
                "middle_name",
                "family_name",
                "phone_no",
                "phone_no_alternative",
                "relationship",
                "sex",
            ]
            fields = model_to_dict(individual, fields=fields_names)
            if not isinstance(fields["phone_no"], str):
                fields["phone_no"] = fields["phone_no"].raw_input
            if not isinstance(fields["phone_no_alternative"], str):
                fields["phone_no_alternative"] = fields[
                    "phone_no_alternative"
                ].raw_input

            query_fields = [
                {
                    "fuzzy": {
                        field_name: {
                            "value": field_value,
                            "fuzziness": "10",
                            "transpositions": True,
                        }
                    }
                }
                for field_name, field_value in fields.items()
            ]

            query_dict = {
                "min_score": self.MIN_SCORE,
                "query": {
                    "bool": {
                        "must": [{"dis_max": {"queries": query_fields}}],
                        "must_not": [
                            {
                                "match": {
                                    "id": {
                                        "query": individual.id
                                    }
                                }
                            }
                        ],
                    }
                }
            }

            # hit with a score equal or above 1.0 is a duplicate
            query = ImportedIndividualDocument.search().from_dict(query_dict)

            results = query.execute()
            import ipdb

            ipdb.set_trace()
