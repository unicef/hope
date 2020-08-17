from django.forms import model_to_dict
from constance import config

from household.documents import IndividualDocument
from household.models import Individual, DUPLICATE, NEEDS_ADJUDICATION

from registration_datahub.documents import ImportedIndividualDocument
from registration_datahub.models import ImportedIndividual, DUPLICATE_IN_BATCH


class DeduplicateTask:
    @staticmethod
    def _prepare_fields(individual, fields_names):
        fields = model_to_dict(individual, fields=fields_names)
        if "hash_key" in fields_names:
            fields["hash_key"] = individual.get_hash_key
        if not isinstance(fields["phone_no"], str):
            fields["phone_no"] = fields["phone_no"].raw_input
        if not isinstance(fields["phone_no_alternative"], str):
            fields["phone_no_alternative"] = fields[
                "phone_no_alternative"
            ].raw_input

        return fields

    @staticmethod
    def _prepare_query_dict(individual, fields, min_score, only_in_rdi=False):
        query_fields = []
        for field_name, field_value in fields.items():
            field_name_as_key = field_name.replace("__", ".")
            if field_name == "hash_key":
                single_query = {
                    "match": {field_name_as_key: {"query": field_value}}
                }
            elif field_name == "birth_date":
                single_query = {
                    "match": {field_name_as_key: {"query": str(field_value)}}
                }
            # elif field_name == "full_name":
            #     single_query = {
            #         "match": {
            #             field_name_as_key: {
            #                 "query": str(field_value),
            #                 "boost": 2,
            #             }
            #         }
            #     }
            else:
                single_query = {
                    "fuzzy": {
                        field_name_as_key: {
                            "value": field_value,
                            "fuzziness": "AUTO",
                            "transpositions": True,
                        }
                    }
                }

            query_fields.append(single_query)

        query_dict = {
            "min_score": min_score,
            "query": {
                "bool": {
                    "must": [{"dis_max": {"queries": query_fields}}],
                    "must_not": [{"match": {"id": {"query": individual.id}}}],
                }
            },
        }

        if only_in_rdi is True:
            query_dict["query"]["bool"]["must"].append(
                {
                    "match": {
                        "registration_data_import_id": {
                            "query": individual.registration_data_import.id
                        }
                    }
                },
            )

        return query_dict

    @staticmethod
    def _get_duplicates_tuple(
        query_dict, duplicate_score, document, individual
    ):
        duplicates = []
        possible_duplicates = []
        original_individuals_ids_duplicates = []
        original_individuals_ids_possible_duplicates = []
        query = document.search().from_dict(query_dict)

        query._index = document._index._name
        results = query.execute()

        for individual_hit in results:
            score = individual_hit.meta.score
            if score >= duplicate_score:
                duplicates.append(individual_hit.id)
                original_individuals_ids_duplicates.append(individual.id)
            else:
                possible_duplicates.append(individual_hit.id)
                original_individuals_ids_possible_duplicates.append(
                    individual.id
                )

        return (
            duplicates,
            possible_duplicates,
            original_individuals_ids_duplicates,
            original_individuals_ids_possible_duplicates,
        )

    @classmethod
    def deduplicate_single_imported_individual(
        cls, individual, only_in_rdi=False
    ):
        fields_names = (
            "given_name",
            "full_name",
            "middle_name",
            "family_name",
            "phone_no",
            "phone_no_alternative",
            "relationship",
            "sex",
            "birth_date",
            "hash_key",
        )
        fields = cls._prepare_fields(individual, fields_names)

        query_dict = cls._prepare_query_dict(
            individual,
            fields,
            0,
            only_in_rdi,
        )

        return cls._get_duplicates_tuple(
            query_dict,
            config.DEDUPLICATION_BATCH_DUPLICATE_SCORE,
            ImportedIndividualDocument,
            individual,
        )

    @classmethod
    def deduplicate_single_individual(cls, individual, only_in_rdi=False):
        fields_names = (
            "given_name",
            "full_name",
            "middle_name",
            "family_name",
            "phone_no",
            "phone_no_alternative",
            "relationship",
            "sex",
            "birth_date",
            "hash_key",
        )
        fields = cls._prepare_fields(individual, fields_names)

        query_dict = cls._prepare_query_dict(
            individual,
            fields,
            config.DEDUPLICATION_GOLDEN_RECORD_MIN_SCORE,
            only_in_rdi,
        )

        return cls._get_duplicates_tuple(
            query_dict,
            config.DEDUPLICATION_GOLDEN_RECORD_DUPLICATE_SCORE,
            IndividualDocument,
            individual,
        )

    @classmethod
    def _get_duplicated_individuals(cls, registration_data_import):
        individuals = Individual.objects.filter(
            registration_data_import=registration_data_import
        )
        all_duplicates = []
        all_possible_duplicates = []
        all_original_individuals_ids_duplicates = []
        all_original_individuals_ids_possible_duplicates = []
        for individual in individuals:
            (
                duplicates,
                possible_duplicates,
                original_individuals_ids_duplicates,
                original_individuals_ids_possible_duplicates,
            ) = cls.deduplicate_single_individual(individual)
            all_duplicates.extend(duplicates)
            all_possible_duplicates.extend(possible_duplicates)
            all_original_individuals_ids_duplicates.extend(
                original_individuals_ids_duplicates
            )
            all_original_individuals_ids_possible_duplicates.extend(
                original_individuals_ids_possible_duplicates
            )

        return (
            all_duplicates,
            all_possible_duplicates,
            all_original_individuals_ids_duplicates,
            all_original_individuals_ids_possible_duplicates,
        )

    @classmethod
    def deduplicate_individuals(cls, registration_data_import):
        (
            all_duplicates,
            all_possible_duplicates,
            all_original_individuals_ids_duplicates,
            all_original_individuals_ids_possible_duplicates,
        ) = cls._get_duplicated_individuals(registration_data_import)
        cls._mark_individuals(all_duplicates, all_possible_duplicates)

    @staticmethod
    def _mark_individuals(all_duplicates, all_possible_duplicates):
        Individual.objects.filter(id__in=all_possible_duplicates).update(
            deduplication_status=NEEDS_ADJUDICATION
        )

        Individual.objects.filter(id__in=all_duplicates).update(
            deduplication_status=DUPLICATE
        )

    @classmethod
    def deduplicate_imported_individuals(cls, registration_data_import_datahub):
        imported_individuals = ImportedIndividual.objects.filter(
            registration_data_import=registration_data_import_datahub
        )

        all_duplicates = []
        all_possible_duplicates = []
        all_original_individuals_ids_duplicates = []
        all_original_individuals_ids_possible_duplicates = []
        for imported_individual in imported_individuals:
            (
                imported_individuals_duplicates,
                imported_individuals_possible_duplicates,
                *rest,
            ) = cls.deduplicate_single_imported_individual(
                imported_individual, only_in_rdi=True
            )

            (
                _,
                _,
                original_individuals_ids_duplicates,
                original_individuals_ids_possible_duplicates,
            ) = cls.deduplicate_single_individual(imported_individual)

            all_duplicates.extend(imported_individuals_duplicates)
            all_possible_duplicates.extend(
                imported_individuals_possible_duplicates
            )
            all_original_individuals_ids_duplicates.extend(
                original_individuals_ids_duplicates
            )
            all_original_individuals_ids_possible_duplicates.extend(
                original_individuals_ids_possible_duplicates
            )

        # BATCH
        ImportedIndividual.objects.filter(id__in=all_duplicates).update(
            deduplication_batch_status=DUPLICATE_IN_BATCH
        )

        # GOLDEN RECORD
        ImportedIndividual.objects.filter(
            id__in=all_original_individuals_ids_duplicates
        ).update(deduplication_golden_record_status=DUPLICATE)

        ImportedIndividual.objects.filter(
            id__in=all_original_individuals_ids_possible_duplicates
        ).update(deduplication_golden_record_status=NEEDS_ADJUDICATION)
