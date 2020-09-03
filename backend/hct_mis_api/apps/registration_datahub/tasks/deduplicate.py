import logging

from django.core.management import call_command
from django.db.models import Q
from django.forms import model_to_dict
from constance import config

from household.documents import IndividualDocument
from household.elasticsearch_utils import rebuild_search_index
from household.models import Individual, DUPLICATE, NEEDS_ADJUDICATION, UNIQUE, NOT_PROCESSED
from registration_data.models import RegistrationDataImport

from registration_datahub.documents import ImportedIndividualDocument
from registration_datahub.models import (
    ImportedIndividual,
    DUPLICATE_IN_BATCH,
    SIMILAR_IN_BATCH,
    UNIQUE_IN_BATCH,
)


log = logging.getLogger(__name__)


class DeduplicateTask:
    business_area = None

    @staticmethod
    def _prepare_fields(individual, fields_names):
        fields = model_to_dict(individual, fields=fields_names)
        if "hash_key" in fields_names:
            fields["hash_key"] = individual.get_hash_key
        if not isinstance(fields["phone_no"], str):
            fields["phone_no"] = fields["phone_no"].raw_input
        if not isinstance(fields["phone_no_alternative"], str):
            fields["phone_no_alternative"] = fields["phone_no_alternative"].raw_input

        return fields

    @classmethod
    def _prepare_query_dict(cls, individual, fields, min_score, only_in_rdi=False):
        query_fields = []
        for field_name, field_value in fields.items():
            field_name_as_key = field_name.replace("__", ".")
            if field_name == "hash_key":
                single_query = {"match": {field_name_as_key: {"query": field_value}}}
            elif field_name == "birth_date":
                single_query = {"match": {field_name_as_key: {"query": str(field_value)}}}
            elif field_name == "full_name":
                single_query = {"match": {field_name_as_key: {"query": field_value, "boost": 2.0}}}
            else:
                single_query = {
                    "fuzzy": {field_name_as_key: {"value": field_value, "fuzziness": "AUTO", "transpositions": True}}
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
            query_dict["query"]["bool"]["filter"] = [
                {"term": {"registration_data_import_id": str(individual.registration_data_import.id)}},
            ]
        # business area should never be None but better double check
        elif only_in_rdi is False and cls.business_area is not None:
            query_dict["query"]["bool"]["filter"] = [
                {"term": {"business_area": cls.business_area}},
            ]

        return query_dict

    @staticmethod
    def _get_duplicates_tuple(query_dict, duplicate_score, document, individual):
        duplicates = []
        possible_duplicates = []
        original_individuals_ids_duplicates = []
        original_individuals_ids_possible_duplicates = []
        query = document.search().from_dict(query_dict)

        query._index = document._index._name
        results = query.execute()

        results_data = {
            "duplicates": [],
            "possible_duplicates": [],
        }
        for individual_hit in results:
            score = individual_hit.meta.score
            # individual is mark as duplicate if have score above defined
            # in settings or if sha256 hashes for both individuals are the same
            if str(individual.get_hash_key) == individual_hit.hash_key or score >= duplicate_score:
                duplicates.append(individual_hit.id)
                original_individuals_ids_duplicates.append(individual.id)
                results_data["duplicates"].append(
                    {
                        "hit_id": individual_hit.id,
                        "full_name": individual_hit.full_name,
                        "score": individual_hit.meta.score,
                        "proximity_to_score": score - duplicate_score,
                    }
                )
            elif document == IndividualDocument:
                possible_duplicates.append(individual_hit.id)
                original_individuals_ids_possible_duplicates.append(individual.id)
                results_data["possible_duplicates"].append(
                    {
                        "hit_id": individual_hit.id,
                        "full_name": individual_hit.full_name,
                        "score": individual_hit.meta.score,
                        "proximity_to_score": score - config.DEDUPLICATION_GOLDEN_RECORD_MIN_SCORE,
                    }
                )
        log.info(f"INDIVIDUAL {individual}")
        log.info([(r.full_name, r.meta.score) for r in results])

        return (
            duplicates,
            possible_duplicates,
            original_individuals_ids_duplicates,
            original_individuals_ids_possible_duplicates,
            results_data,
        )

    @classmethod
    def deduplicate_single_imported_individual(cls, individual, only_in_rdi=False):
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

        # query_dict = cls._prepare_query_dict(individual, fields, config.DEDUPLICATION_BATCH_MIN_SCORE, only_in_rdi,)
        query_dict = cls._prepare_query_dict(individual, fields, 0, only_in_rdi,)

        return cls._get_duplicates_tuple(
            query_dict, config.DEDUPLICATION_BATCH_DUPLICATE_SCORE, ImportedIndividualDocument, individual,
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
            individual, fields, config.DEDUPLICATION_GOLDEN_RECORD_MIN_SCORE, only_in_rdi,
        )

        return cls._get_duplicates_tuple(
            query_dict, config.DEDUPLICATION_GOLDEN_RECORD_DUPLICATE_SCORE, IndividualDocument, individual,
        )

    @classmethod
    def _get_duplicated_individuals(cls, registration_data_import):
        individuals = Individual.objects.filter(registration_data_import=registration_data_import)
        all_duplicates = []
        all_possible_duplicates = []
        all_original_individuals_ids_duplicates = []
        all_original_individuals_ids_possible_duplicates = []
        to_bulk_update_results = []
        for individual in individuals:
            (
                duplicates,
                possible_duplicates,
                original_individuals_ids_duplicates,
                original_individuals_ids_possible_duplicates,
                results_data,
            ) = cls.deduplicate_single_individual(individual)

            individual.deduplication_results = results_data
            to_bulk_update_results.append(individual)

            all_duplicates.extend(duplicates)
            all_possible_duplicates.extend(possible_duplicates)
            all_original_individuals_ids_duplicates.extend(original_individuals_ids_duplicates)
            all_original_individuals_ids_possible_duplicates.extend(original_individuals_ids_possible_duplicates)

        return (
            all_duplicates,
            all_possible_duplicates,
            all_original_individuals_ids_duplicates,
            all_original_individuals_ids_possible_duplicates,
            to_bulk_update_results,
        )

    @classmethod
    def deduplicate_individuals(cls, registration_data_import):
        rebuild_search_index()

        cls.business_area = registration_data_import.business_area.slug
        (
            all_duplicates,
            all_possible_duplicates,
            all_original_individuals_ids_duplicates,
            all_original_individuals_ids_possible_duplicates,
            to_bulk_update_results,
        ) = cls._get_duplicated_individuals(registration_data_import)
        cls._mark_individuals(all_duplicates, all_possible_duplicates, to_bulk_update_results)

    @staticmethod
    def _mark_individuals(all_duplicates, all_possible_duplicates, to_bulk_update_results):
        Individual.objects.filter(id__in=all_duplicates).update(deduplication_status=DUPLICATE)

        Individual.objects.filter(id__in=set(all_possible_duplicates).difference(set(all_duplicates))).update(
            deduplication_status=NEEDS_ADJUDICATION
        )

        Individual.objects.bulk_update(
            to_bulk_update_results, ["deduplication_results",],
        )

    @staticmethod
    def set_error_message_and_status(registration_data_import, message):
        registration_data_import.error_message = message
        registration_data_import.status = RegistrationDataImport.DEDUPLICATION_FAILED
        registration_data_import.save()

    @classmethod
    def deduplicate_imported_individuals(cls, registration_data_import_datahub):
        rebuild_search_index()

        imported_individuals = ImportedIndividual.objects.filter(
            registration_data_import=registration_data_import_datahub
        )
        registration_data_import = RegistrationDataImport.objects.get(id=registration_data_import_datahub.hct_id)
        cls.business_area = registration_data_import_datahub.business_area_slug
        allowed_duplicates_batch_amount = round(
            (imported_individuals.count() or 1) * (config.DEDUPLICATION_BATCH_DUPLICATES_PERCENTAGE / 100)
        )
        allowed_duplicates_golden_record_amount = round(
            (imported_individuals.count() or 1) * (config.DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_PERCENTAGE / 100)
        )

        print(allowed_duplicates_batch_amount)
        print(allowed_duplicates_golden_record_amount)

        all_duplicates = []
        all_possible_duplicates = []
        all_original_individuals_ids_duplicates = []
        all_original_individuals_ids_possible_duplicates = []
        to_bulk_update_results = []
        checked_individuals_ids = []
        for imported_individual in imported_individuals:
            (
                imported_individuals_duplicates,
                imported_individuals_possible_duplicates,
                _,
                _,
                results_data_imported,
            ) = cls.deduplicate_single_imported_individual(imported_individual, only_in_rdi=True)

            if len(results_data_imported["duplicates"]) > config.DEDUPLICATION_BATCH_DUPLICATES_ALLOWED:
                message = "Amount of duplicates for single individual within a batch reached maximum number."
                cls.set_error_message_and_status(registration_data_import, message)
                break

            imported_individual.deduplication_batch_results = results_data_imported

            (
                _,
                _,
                original_individuals_ids_duplicates,
                original_individuals_ids_possible_duplicates,
                results_data,
            ) = cls.deduplicate_single_individual(imported_individual)

            if len(results_data["duplicates"]) > config.DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_ALLOWED:
                message = "Amount of duplicates for single individual within a golden record reached maximum number."
                cls.set_error_message_and_status(registration_data_import, message)
                break

            imported_individual.deduplication_golden_record_results = results_data

            all_duplicates.extend(imported_individuals_duplicates)
            all_possible_duplicates.extend(imported_individuals_possible_duplicates)
            all_original_individuals_ids_duplicates.extend(original_individuals_ids_duplicates)
            all_original_individuals_ids_possible_duplicates.extend(original_individuals_ids_possible_duplicates)
            to_bulk_update_results.append(imported_individual)

            set_of_all_duplicates = set(all_duplicates)
            set_of_all_original_individuals_ids_duplicates = set(all_original_individuals_ids_duplicates)

            batch_amount_exceeded = len(set_of_all_duplicates) >= allowed_duplicates_batch_amount
            golden_record_amount_exceeded = (
                len(set_of_all_original_individuals_ids_duplicates) >= allowed_duplicates_golden_record_amount
            )

            checked_individuals_ids.append(imported_individual.id)

            if batch_amount_exceeded:
                message = (
                    "Percentage of records within a batch that can be deemed as 'duplicate' reached maximum number."
                )
                cls.set_error_message_and_status(registration_data_import, message)
                break
            elif golden_record_amount_exceeded:
                message = (
                    "Percentage of records within a golden record that can "
                    "be deemed as 'duplicate' reached maximum number."
                )
                cls.set_error_message_and_status(registration_data_import, message)
                break
            elif batch_amount_exceeded and golden_record_amount_exceeded:
                message = (
                    "Percentage of records within a batch and golden record that can "
                    "be deemed as 'duplicate' reached maximum number."
                )
                cls.set_error_message_and_status(registration_data_import, message)
                break

        # BATCH
        set_of_all_possible_duplicates = set(all_possible_duplicates)
        set_of_all_duplicates = set(all_duplicates)

        ImportedIndividual.objects.filter(id__in=set_of_all_duplicates).update(
            deduplication_batch_status=DUPLICATE_IN_BATCH
        )

        # ImportedIndividual.objects.filter(
        #     id__in=set_of_all_possible_duplicates.difference(set_of_all_duplicates)
        # ).update(deduplication_batch_status=SIMILAR_IN_BATCH)

        # GOLDEN RECORD
        set_of_all_original_individuals_ids_duplicates = set(all_original_individuals_ids_duplicates)
        set_of_all_original_individuals_ids_possible_duplicates = set(all_original_individuals_ids_possible_duplicates)

        ImportedIndividual.objects.filter(id__in=set_of_all_original_individuals_ids_duplicates).update(
            deduplication_golden_record_status=DUPLICATE
        )
        ImportedIndividual.objects.filter(
            id__in=set_of_all_original_individuals_ids_possible_duplicates.difference(
                set_of_all_original_individuals_ids_duplicates
            )
        ).update(deduplication_golden_record_status=NEEDS_ADJUDICATION)

        ImportedIndividual.objects.bulk_update(
            to_bulk_update_results, ["deduplication_batch_results", "deduplication_golden_record_results",],
        )
        registration_data_import_datahub.refresh_from_db()
        if registration_data_import.status == RegistrationDataImport.DEDUPLICATION_FAILED:
            registration_data_import_datahub.individuals.filter(
                Q(deduplication_batch_status=UNIQUE_IN_BATCH) & Q(deduplication_golden_record_status=UNIQUE)
            ).exclude(id__in=checked_individuals_ids).update(
                deduplication_batch_status=NOT_PROCESSED, deduplication_golden_record_status=NOT_PROCESSED,
            )
        else:
            registration_data_import_datahub.individuals.exclude(
                Q(id__in=set_of_all_duplicates.union(set_of_all_possible_duplicates))
            ).update(deduplication_batch_status=UNIQUE_IN_BATCH)
            registration_data_import_datahub.individuals.exclude(
                id__in=set_of_all_original_individuals_ids_duplicates.union(
                    set_of_all_original_individuals_ids_possible_duplicates
                )
            ).update(deduplication_golden_record_status=UNIQUE)

            registration_data_import.status = RegistrationDataImport.IN_REVIEW
            registration_data_import.error_message = ""
            registration_data_import.save()
