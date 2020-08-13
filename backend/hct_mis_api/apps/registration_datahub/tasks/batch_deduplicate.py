from django.forms import model_to_dict
from constance import config

from registration_datahub.documents import ImportedIndividualDocument
from registration_datahub.models import (
    RegistrationDataImportDatahub,
    ImportedIndividual,
)


class BatchDeduplicate:
    def __init__(
        self, registration_data_import_datahub: RegistrationDataImportDatahub
    ):
        self.registration_data_import_datahub = registration_data_import_datahub

    def deduplicate(self):
        individuals = ImportedIndividual.objects.filter(
            registration_data_import=self.registration_data_import_datahub
        )

        to_remove = []
        to_mark_as_possible_duplicate = []
        for individual in individuals:
            fields_names = config.DEDUPLICATION_BATCH_FIELDS
            fields = model_to_dict(individual, fields=fields_names)
            if not isinstance(fields["phone_no"], str):
                fields["phone_no"] = fields["phone_no"].raw_input
            if not isinstance(fields["phone_no_alternative"], str):
                fields["phone_no_alternative"] = fields[
                    "phone_no_alternative"
                ].raw_input

            # TODO: should we boost some more important fields?
            query_fields = [
                {
                    "fuzzy": {
                        field_name.replace("__", "."): {
                            "value": field_value,
                            "fuzziness": "10",
                            "transpositions": True,
                        }
                    }
                }
                for field_name, field_value in fields.items()
            ]

            query_dict = {
                "min_score": config.DEDUPLICATION_BATCH_MIN_SCORE,
                "query": {
                    "bool": {
                        "must": [{"dis_max": {"queries": query_fields}}],
                        "must_not": [
                            {"match": {"id": {"query": individual.id}}}
                        ],
                    }
                },
            }

            query = ImportedIndividualDocument.search().from_dict(query_dict)
            results = query.execute()
            for individual_hit in results:
                score = individual_hit.meta.score
                if score >= config.DEDUPLICATION_BATCH_DUPLICATE_SCORE:
                    to_remove.append(individual_hit.id)
                else:
                    to_mark_as_possible_duplicate.append(individual_hit.id)

        # mark possible duplicates
        ImportedIndividual.objects.filter(
            id__in=to_mark_as_possible_duplicate
        ).update(possible_duplicate_flag=True)
        # remove duplicates
        ImportedIndividual.objects.filter(id__in=to_remove).delete()
