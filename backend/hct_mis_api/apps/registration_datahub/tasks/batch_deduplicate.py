from django.forms import model_to_dict
from elasticsearch_dsl.query import MoreLikeThis, Fuzzy

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

    def __init__(
        self, registration_data_import_datahub: RegistrationDataImportDatahub
    ):
        self.registration_data_import_datahub = registration_data_import_datahub

    def deduplicate(self):
        import ipdb; ipdb.set_trace()
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

            query_fields = {
                field_name: {
                    "value": field_value,
                    "fuzziness": "10",
                    "max_expansions": 50,
                    "prefix_length": 0,
                    "transpositions": True,
                }
                for field_name, field_value in fields.items()
            }

            individual_doc = (
                ImportedIndividualDocument.search()
                .query("match", id=individual.id)
                .execute()[0]
            )
            # query = ImportedIndividualDocument.search().query(
            #     MoreLikeThis(
            #         like=[
            #             {
            #                 "_id": individual_doc.meta.id,
            #                 "_index": individual_doc.meta.index,
            #             }
            #         ],
            #         fields=fields_names,
            #         minimum_should_match="75%",
            #     ),
            # )

            query = ImportedIndividualDocument.search().query(
                Fuzzy(**query_fields)
            )

            result = query.execute()
            import ipdb

            ipdb.set_trace()
