import itertools
import logging
from collections import defaultdict
from dataclasses import dataclass, fields
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from django.db import transaction
from django.db.models import Case, CharField, F, Q, QuerySet, Value, When
from django.db.models.functions import Concat

from constance import config
from psycopg2._psycopg import IntegrityError

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import to_dict
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
)
from hct_mis_api.apps.household.documents import IndividualDocument, get_individual_doc
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    NEEDS_ADJUDICATION,
    NOT_PROCESSED,
    UNIQUE,
    UNIQUE_IN_BATCH,
    Document,
    Individual,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.documents import (
    ImportedIndividualDocument,
    get_imported_individual_doc,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedIndividual,
    RegistrationDataImportDatahub,
)
from hct_mis_api.apps.registration_datahub.utils import post_process_dedupe_results
from hct_mis_api.apps.utils.elasticsearch_utils import (
    populate_index,
    remove_elasticsearch_documents_by_matching_ids,
    wait_until_es_healthy,
)
from hct_mis_api.apps.utils.querysets import evaluate_qs

log = logging.getLogger(__name__)


@dataclass
class Thresholds:
    # use 0 to check django-constance values are loaded
    DEDUPLICATION_DUPLICATE_SCORE: float = 0.0
    DEDUPLICATION_POSSIBLE_DUPLICATE_SCORE: int = 0
    DEDUPLICATION_BATCH_DUPLICATES_PERCENTAGE: int = 0
    DEDUPLICATION_BATCH_DUPLICATES_ALLOWED: int = 0

    DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_PERCENTAGE: int = 0
    DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_ALLOWED: int = 0

    def __post_init__(self) -> None:
        for f in fields(self):
            setattr(self, f.name, getattr(config, f.name))

    @classmethod
    def from_business_area(cls, ba: BusinessArea) -> "Thresholds":
        t = cls()
        for f in fields(cls):
            setattr(t, f.name, getattr(ba, f.name.lower()))
        return t


@dataclass
class TicketData:
    ticket: GrievanceTicket
    ticket_details: TicketNeedsAdjudicationDetails
    possible_duplicates_throughs: List[Any]


@dataclass
class DeduplicationResult:
    duplicates: List
    possible_duplicates: List
    original_individuals_ids_duplicates: List
    original_individuals_ids_possible_duplicates: List
    results_data: Dict[str, Any]


class DeduplicateTask:
    """
    WARNING: when deduplication for all business areas will be enabled we need to find a way to block
    other task from interfering with elasticsearch indexes
    (disabling parallel)
    """

    FUZZINESS = "AUTO:3,6"

    def __init__(self, business_area_slug: str):
        self.business_area: BusinessArea = BusinessArea.objects.get(slug=business_area_slug)
        self.thresholds: Thresholds = Thresholds.from_business_area(self.business_area)

    def deduplicate_individuals_against_population(self, individuals: QuerySet[Individual]) -> None:
        wait_until_es_healthy()

        all_duplicates = []
        all_possible_duplicates = []
        all_original_individuals_ids_duplicates = []
        all_original_individuals_ids_possible_duplicates = []
        to_bulk_update_results = []
        individual_fields = [
            "given_name",
            "full_name",
            "middle_name",
            "family_name",
            "phone_no",
            "phone_no_alternative",
            "relationship",
            "sex",
            "birth_date",
            "unicef_id",
        ]
        individual_qs = individuals.only(*individual_fields).prefetch_related("identities")
        for individual in individual_qs:
            deduplication_result = self._deduplicate_single_individual(individual)

            individual.deduplication_golden_record_results = deduplication_result.results_data
            to_bulk_update_results.append(individual)

            all_duplicates.extend(deduplication_result.duplicates)
            all_possible_duplicates.extend(deduplication_result.possible_duplicates)
            all_original_individuals_ids_duplicates.extend(deduplication_result.original_individuals_ids_duplicates)
            all_original_individuals_ids_possible_duplicates.extend(
                deduplication_result.original_individuals_ids_possible_duplicates
            )

        Individual.objects.filter(id__in=all_duplicates + all_original_individuals_ids_duplicates).update(
            deduplication_golden_record_status=DUPLICATE
        )
        Individual.objects.filter(
            id__in=all_possible_duplicates + all_original_individuals_ids_possible_duplicates
        ).update(deduplication_golden_record_status=NEEDS_ADJUDICATION)

        Individual.objects.bulk_update(
            to_bulk_update_results,
            ("deduplication_golden_record_results",),
        )

    def deduplicate_individuals_from_other_source(self, individuals: QuerySet[Individual]) -> None:
        wait_until_es_healthy()

        to_bulk_update_results = []
        all_duplicates = []
        all_possible_duplicates = []
        individual_fields = [
            "given_name",
            "full_name",
            "middle_name",
            "family_name",
            "phone_no",
            "phone_no_alternative",
            "relationship",
            "sex",
            "birth_date",
            "unicef_id",
        ]
        individual_qs = individuals.only(*individual_fields).prefetch_related("identities")
        for individual in evaluate_qs(individual_qs.select_for_update().order_by("pk")):
            deduplication_result = self._deduplicate_single_individual(individual)

            individual.deduplication_golden_record_results = deduplication_result.results_data
            if deduplication_result.duplicates:
                all_duplicates.append(individual.id)
            elif deduplication_result.possible_duplicates:
                all_possible_duplicates.append(individual.id)

            to_bulk_update_results.append(individual)

        Individual.objects.filter(id__in=all_duplicates).update(deduplication_golden_record_status=DUPLICATE)
        Individual.objects.filter(id__in=all_possible_duplicates).update(
            deduplication_golden_record_status=NEEDS_ADJUDICATION
        )
        Individual.objects.bulk_update(
            to_bulk_update_results,
            ("deduplication_golden_record_results",),
        )

    def deduplicate_imported_individuals(self, registration_data_import_datahub: RegistrationDataImportDatahub) -> None:
        imported_individuals = ImportedIndividual.objects.filter(
            registration_data_import_id=registration_data_import_datahub.id
        )

        wait_until_es_healthy()
        populate_index(imported_individuals, get_imported_individual_doc(self.business_area.slug))

        registration_data_import = RegistrationDataImport.objects.get(id=registration_data_import_datahub.hct_id)
        allowed_duplicates_in_batch = round(
            (imported_individuals.count() or 1) * (self.thresholds.DEDUPLICATION_BATCH_DUPLICATES_PERCENTAGE / 100)
        )
        allowed_duplicates_in_population = round(
            (imported_individuals.count() or 1)
            * (self.thresholds.DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_PERCENTAGE / 100)
        )

        to_bulk_update_results = []
        duplicates_in_batch = set()
        possible_duplicates_in_batch = set()
        duplicates_in_population = set()
        possible_duplicates_in_population = set()
        checked_individuals_ids = set()

        for imported_individual in imported_individuals:
            checked_individuals_ids.add(imported_individual.id)
            to_bulk_update_results.append(imported_individual)

            # Check against the batch
            imported_deduplication_result = self._deduplicate_single_imported_individual(
                imported_individual, registration_data_import_datahub.id
            )

            imported_individual.deduplication_batch_results = imported_deduplication_result.results_data
            post_process_dedupe_results(imported_individual)

            if imported_deduplication_result.results_data["duplicates"]:
                imported_individual.deduplication_batch_status = DUPLICATE_IN_BATCH
            else:
                imported_individual.deduplication_batch_status = UNIQUE_IN_BATCH
            duplicates_in_batch.update(imported_deduplication_result.duplicates)
            possible_duplicates_in_batch.update(imported_deduplication_result.possible_duplicates)

            if (
                len(imported_deduplication_result.results_data["duplicates"])
                > self.thresholds.DEDUPLICATION_BATCH_DUPLICATES_ALLOWED
            ):
                message = (
                    "The number of individuals deemed duplicate with an individual record of the batch "
                    f"exceed the maximum allowed ({self.thresholds.DEDUPLICATION_BATCH_DUPLICATES_ALLOWED})"
                )
                self._set_error_message_and_status(registration_data_import, message)
                break

            if (len(duplicates_in_batch) >= allowed_duplicates_in_batch) and imported_individuals.count() > 1:
                message = (
                    f"The percentage of records ({self.thresholds.DEDUPLICATION_BATCH_DUPLICATES_PERCENTAGE}%), "
                    "deemed as 'duplicate', within a batch has reached the maximum number."
                )
                self._set_error_message_and_status(registration_data_import, message)
                break

            # Check against the population
            deduplication_result = self._deduplicate_single_individual(imported_individual)
            imported_individual.deduplication_golden_record_results = deduplication_result.results_data
            if deduplication_result.results_data["duplicates"]:
                imported_individual.deduplication_golden_record_status = DUPLICATE
            elif deduplication_result.results_data["possible_duplicates"]:
                imported_individual.deduplication_golden_record_status = NEEDS_ADJUDICATION
            else:
                imported_individual.deduplication_golden_record_status = UNIQUE
            duplicates_in_population.update(deduplication_result.original_individuals_ids_duplicates)
            possible_duplicates_in_population.update(deduplication_result.original_individuals_ids_possible_duplicates)

            if (
                len(deduplication_result.results_data["duplicates"])
                > self.thresholds.DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_ALLOWED
            ):
                message = (
                    "The number of individuals deemed duplicate with an individual record of the batch "
                    f"exceed the maximum allowed ({self.thresholds.DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_ALLOWED})"
                )
                self._set_error_message_and_status(registration_data_import, message)
                break

            if (len(duplicates_in_population) >= allowed_duplicates_in_population) and imported_individuals.count() > 1:
                message = (
                    f"The percentage of records ({self.thresholds.DEDUPLICATION_GOLDEN_RECORD_DUPLICATES_PERCENTAGE}%), "
                    "deemed as 'duplicate', within a population has reached the maximum number."
                )
                self._set_error_message_and_status(registration_data_import, message)
                break

        ImportedIndividual.objects.bulk_update(
            to_bulk_update_results,
            [
                "deduplication_batch_results",
                "deduplication_golden_record_results",
                "deduplication_batch_status",
                "deduplication_golden_record_status",
            ],
        )
        if registration_data_import.status == RegistrationDataImport.DEDUPLICATION_FAILED:
            ImportedIndividual.objects.filter(
                registration_data_import_id=registration_data_import_datahub.id,
                deduplication_batch_status=UNIQUE_IN_BATCH,
                deduplication_golden_record_status=UNIQUE,
            ).exclude(id__in=checked_individuals_ids).update(
                deduplication_batch_status=NOT_PROCESSED,
                deduplication_golden_record_status=NOT_PROCESSED,
            )
        else:
            ImportedIndividual.objects.filter(registration_data_import_id=registration_data_import_datahub.id).exclude(
                id__in=duplicates_in_batch.union(possible_duplicates_in_batch)
            ).update(deduplication_batch_status=UNIQUE_IN_BATCH)
            ImportedIndividual.objects.filter(registration_data_import_id=registration_data_import_datahub.id).exclude(
                id__in=duplicates_in_population.union(possible_duplicates_in_population)
            ).update(deduplication_golden_record_status=UNIQUE)
            old_rdi = RegistrationDataImport.objects.get(id=registration_data_import.id)
            registration_data_import.status = RegistrationDataImport.IN_REVIEW
            registration_data_import.error_message = ""
            registration_data_import.save()

            log_create(
                RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", None, old_rdi, registration_data_import
            )

        remove_elasticsearch_documents_by_matching_ids(
            list(imported_individuals.values_list("id", flat=True)),
            get_imported_individual_doc(self.business_area.slug),
        )

    def _prepare_fields(
        self,
        individual: Union[Individual, ImportedIndividual],
        fields_names: Tuple[str, ...],
        dict_fields: Dict[str, Any],
    ) -> Dict[str, Any]:
        fields = to_dict(individual, fields=fields_names, dict_fields=dict_fields)
        if not isinstance(fields["phone_no"], str):
            fields["phone_no"] = fields["phone_no"].raw_input
        if not isinstance(fields["phone_no_alternative"], str):
            fields["phone_no_alternative"] = fields["phone_no_alternative"].raw_input
        return fields

    def _prepare_query_dict(
        self, individual_id: str, individual_fields: Dict, min_score: Union[int, float]
    ) -> Dict[str, Any]:
        fields_meta = {
            "birth_date": {"boost": 2},
            "phone_no": {"boost": 2},
            "phone_no_alternative": {"boost": 2},
            "sex": {"boost": 1},
            "relationship": {"boost": 1},
            "middle_name": {"boost": 1},
            "admin1": {"boost": 1},
            "admin2": {"boost": 1},
        }
        queries_list = []
        queries_list.extend(self._prepare_queries_for_names_from_fields(individual_fields))
        queries_list.extend(self._prepare_identities_queries_from_fields(individual_fields.pop("identities", [])))

        for field_name, field_value in individual_fields.items():
            if field_value is None:
                continue
            if isinstance(field_value, str) and field_value == "":
                continue
            if field_name not in fields_meta.keys():
                continue
            field_meta = fields_meta[field_name]
            queries_list.append(
                {
                    "match": {
                        field_name: {
                            "query": field_value,
                            "boost": field_meta.get("boost", 1),
                            "operator": "OR",
                        }
                    }
                }
            )

        return {
            "min_score": min_score,
            "size": "100",
            "query": {
                "bool": {
                    "minimum_should_match": 1,
                    "should": queries_list,
                    "must_not": [{"match": {"id": {"query": individual_id, "boost": 0}}}],
                }
            },
        }

    def _prepare_queries_for_names_from_fields(self, individual_fields: Dict) -> List[Dict]:
        """
        prepares ES queries for
        * givenName
        * familyName
        or
        * full_name
        max_score 8 if exact match or phonetic exact match
        """
        given_name = individual_fields.pop("given_name")
        family_name = individual_fields.pop("family_name")
        full_name = individual_fields.pop("full_name")
        if all(x is None for x in (given_name, family_name, full_name)):
            return []

        if not given_name or not family_name:
            # max possible score 7
            return [{"match": {"full_name": {"query": full_name, "boost": 8.0, "operator": "AND"}}}]

        given_name_complex_query = self._get_complex_query_for_name(given_name, "given_name")
        family_name_complex_query = self._get_complex_query_for_name(family_name, "family_name")
        names_should_query = {
            "bool": {
                "should": [
                    given_name_complex_query,
                    family_name_complex_query,
                ]
            }
        }
        # max possible score 8
        names_must_query = {
            "bool": {
                "must": [
                    given_name_complex_query,
                    family_name_complex_query,
                ],
                "boost": 4,
            }
        }
        max_from_should_and_must = {"dis_max": {"queries": [names_should_query, names_must_query], "tie_breaker": 0}}

        return [max_from_should_and_must]

    def _get_complex_query_for_name(self, name: str, field_name: str) -> Dict:
        name_phonetic_query_dict = {"match": {f"{field_name}.phonetic": {"query": name}}}
        # phonetic analyzer not working with fuzziness
        name_fuzzy_query_dict = {
            "match": {
                field_name: {
                    "query": name,
                    "fuzziness": self.FUZZINESS,
                    "max_expansions": 50,
                    "prefix_length": 0,
                    "fuzzy_transpositions": True,
                }
            }
        }
        # choose max from fuzzy and phonetic
        # phonetic score === 0 or 1
        # fuzzy score <=1 changes if there is need make change
        return {"dis_max": {"queries": [name_fuzzy_query_dict, name_phonetic_query_dict], "tie_breaker": 0}}

    def _prepare_identities_queries_from_fields(self, identities: List) -> List[Dict]:
        queries = []
        for item in identities:
            doc_number = item.get("number")
            doc_type = item.get("partner")
            if doc_number and doc_type:
                queries.extend(
                    [
                        {
                            "bool": {
                                "must": [
                                    {"match": {"identities.number": {"query": str(doc_number)}}},
                                    {"match": {"identities.partner": {"query": doc_type}}},
                                ],
                                "boost": 4,
                            },
                        }
                    ]
                )

        return queries

    def _get_deduplicate_result(
        self,
        query_dict: Dict,
        duplicate_score: float,
        document: Union[Type[IndividualDocument], Type[ImportedIndividualDocument]],
        individual: Union[Individual, ImportedIndividual],
    ) -> DeduplicationResult:
        duplicates = []
        possible_duplicates = []
        original_individuals_ids_duplicates = []
        original_individuals_ids_possible_duplicates = []
        query = document.search().params(search_type="dfs_query_then_fetch").from_dict(query_dict)
        query._index = document._index._name
        results = query.execute()
        results_data = {
            "duplicates": [],
            "possible_duplicates": [],
        }
        should_ignore_withdraw = isinstance(individual, Individual) and self.business_area.deduplication_ignore_withdraw

        individual_hit_ids = Individual.objects.filter(
            withdrawn=True, id__in=[result.id for result in results]
        ).values_list("id", flat=True)

        for individual_hit in results:
            if should_ignore_withdraw and individual_hit.id in individual_hit_ids:
                continue
            score = individual_hit.meta.score
            results_core_data = {
                "hit_id": individual_hit.id,
                "full_name": individual_hit.full_name,
                "score": individual_hit.meta.score,
                "location": individual_hit.admin2,  # + village
                "dob": individual_hit.birth_date.strftime("%Y-%m-%d"),
            }
            if score >= duplicate_score:
                duplicates.append(individual_hit.id)
                original_individuals_ids_duplicates.append(individual.id)
                results_core_data["proximity_to_score"] = score - duplicate_score
                results_data["duplicates"].append(results_core_data)
            elif document == get_individual_doc(self.business_area.slug):
                possible_duplicates.append(individual_hit.id)
                original_individuals_ids_possible_duplicates.append(individual.id)
                results_core_data["proximity_to_score"] = score - self.thresholds.DEDUPLICATION_POSSIBLE_DUPLICATE_SCORE
                results_data["possible_duplicates"].append(results_core_data)
        log.debug(f"INDIVIDUAL {individual}")
        log.debug([(r.full_name, r.meta.score) for r in results])
        return DeduplicationResult(
            duplicates,
            possible_duplicates,
            original_individuals_ids_duplicates,
            original_individuals_ids_possible_duplicates,
            results_data,
        )

    def _deduplicate_single_imported_individual(
        self, individual: ImportedIndividual, rdi_id: str
    ) -> DeduplicationResult:
        fields_names: Tuple[str, ...] = (
            "given_name",
            "full_name",
            "middle_name",
            "family_name",
            "phone_no",
            "phone_no_alternative",
            "relationship",
            "sex",
            "birth_date",
        )
        dict_fields: Dict[str, Tuple[str, ...]] = {
            "identities": ("document_number", "partner"),
        }
        individual_fields = self._prepare_fields(individual, fields_names, dict_fields)

        query_dict = self._prepare_query_dict(
            individual.id,
            individual_fields,
            self.thresholds.DEDUPLICATION_DUPLICATE_SCORE,
        )

        query_dict["query"]["bool"]["filter"] = [
            {"term": {"registration_data_import_id": rdi_id}},
        ]
        return self._get_deduplicate_result(
            query_dict,
            self.thresholds.DEDUPLICATION_DUPLICATE_SCORE,
            get_imported_individual_doc(self.business_area.slug),
            individual,
        )

    def _deduplicate_single_individual(self, individual: Union[Individual, ImportedIndividual]) -> DeduplicationResult:
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
        )
        dict_fields = {
            "identities": ("number", "partner.name"),
        }
        individual_fields = self._prepare_fields(individual, fields_names, dict_fields)

        query_dict = self._prepare_query_dict(
            individual.id,
            individual_fields,
            self.thresholds.DEDUPLICATION_POSSIBLE_DUPLICATE_SCORE,
        )
        query_dict["query"]["bool"]["filter"] = [
            {"term": {"business_area": self.business_area.slug}},
        ]

        document = get_individual_doc(self.business_area.slug)

        return self._get_deduplicate_result(
            query_dict,
            self.thresholds.DEDUPLICATION_DUPLICATE_SCORE,
            document,
            individual,
        )

    def _set_error_message_and_status(self, registration_data_import: RegistrationDataImport, message: str) -> None:
        old_rdi = RegistrationDataImport.objects.get(id=registration_data_import.id)
        registration_data_import.error_message = message
        registration_data_import.status = RegistrationDataImport.DEDUPLICATION_FAILED
        registration_data_import.save(
            update_fields=(
                "error_message",
                "status",
            )
        )
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", None, old_rdi, registration_data_import
        )


class HardDocumentDeduplication:
    @transaction.atomic
    def deduplicate(
        self, new_documents: QuerySet[Document], registration_data_import: Optional[RegistrationDataImport] = None
    ) -> None:
        documents_to_dedup = evaluate_qs(
            new_documents.exclude(status=Document.STATUS_VALID)
            .filter(type__is_identity_document=True)
            .select_related("individual", "type")
            .select_for_update(of=("self",))  # no need to lock individuals
            .order_by("pk")
        )
        documents_numbers = [x.document_number for x in documents_to_dedup]
        new_document_signatures = [self._generate_signature(d) for d in documents_to_dedup]
        new_document_signatures_duplicated_in_batch = [
            d for d in new_document_signatures if new_document_signatures.count(d) > 1
        ]
        all_matching_number_documents = (
            Document.objects.select_related("individual", "individual__household", "individual__business_area")
            .filter(document_number__in=documents_numbers, status=Document.STATUS_VALID)
            .annotate(
                signature=Concat(
                    Case(
                        When(
                            Q(type__valid_for_deduplication=True),
                            then=Concat(F("type_id"), Value("--"), output_field=CharField()),
                        ),
                        default=Value(""),
                    ),
                    F("document_number"),
                    Value("--"),
                    F("country_id"),
                    output_field=CharField(),
                )
            )
        )
        all_matching_number_documents_dict = {d.signature: d for d in all_matching_number_documents}
        all_matching_number_documents_signatures = all_matching_number_documents_dict.keys()
        already_processed_signatures = []
        ticket_data_dict = {}
        possible_duplicates_individuals_id_set = set()

        for new_document in documents_to_dedup:
            new_document_signature = self._generate_signature(new_document)

            if new_document_signature in all_matching_number_documents_signatures:
                new_document.status = Document.STATUS_NEED_INVESTIGATION
                ticket_data = ticket_data_dict.get(
                    new_document_signature,
                    {"original": all_matching_number_documents_dict[new_document_signature], "possible_duplicates": []},
                )
                ticket_data["possible_duplicates"].append(new_document)
                ticket_data_dict[new_document_signature] = ticket_data
                possible_duplicates_individuals_id_set.add(str(new_document.individual_id))
                continue

            if (
                new_document_signature in new_document_signatures_duplicated_in_batch
                and new_document_signature in already_processed_signatures
            ):
                new_document.status = Document.STATUS_NEED_INVESTIGATION
                ticket_data_dict[new_document_signature]["possible_duplicates"].append(new_document)
                possible_duplicates_individuals_id_set.add(str(new_document.individual_id))
                continue

            new_document.status = Document.STATUS_VALID
            already_processed_signatures.append(new_document_signature)

            if new_document_signature in new_document_signatures_duplicated_in_batch:
                ticket_data_dict[new_document_signature] = {
                    "original": new_document,
                    "possible_duplicates": [],
                }

        try:
            Document.objects.bulk_update(documents_to_dedup, ("status", "updated_at"))
        except IntegrityError:
            log.error(
                f"Hard Deduplication Documents bulk update error."
                f"All matching documents in DB: {all_matching_number_documents_signatures}"
                f"New documents to dedup: {new_document_signatures}"
                f"new_document_signatures_duplicated_in_batch: {new_document_signatures_duplicated_in_batch}"
            )
            raise

        PossibleDuplicateThrough = TicketNeedsAdjudicationDetails.possible_duplicates.through
        possible_duplicates_through_existing_list = (
            PossibleDuplicateThrough.objects.filter(individual__in=possible_duplicates_individuals_id_set)
            .order_by("ticketneedsadjudicationdetails")
            .values_list(
                "ticketneedsadjudicationdetails_id",
                "individual_id",
                "ticketneedsadjudicationdetails__golden_records_individual",
            )
        )

        possible_duplicates_through_dict = defaultdict(set)
        for ticked_details_id, individual_id, main_individual_id in possible_duplicates_through_existing_list:
            possible_duplicates_through_dict[str(ticked_details_id)].add(str(individual_id))
            possible_duplicates_through_dict[str(ticked_details_id)].add(str(main_individual_id))

        ticket_data_collected = []
        for ticket_data in ticket_data_dict.values():
            prepared_ticket = self._prepare_grievance_ticket_documents_deduplication(
                main_individual=ticket_data["original"].individual,
                business_area=ticket_data["original"].individual.business_area,
                registration_data_import=registration_data_import,
                possible_duplicates_individuals=[d.individual for d in ticket_data["possible_duplicates"]],
                possible_duplicates_through_dict=possible_duplicates_through_dict,
            )
            if prepared_ticket is None:
                continue
            ticket_data_collected.append(prepared_ticket)

        GrievanceTicket.objects.bulk_create([x.ticket for x in ticket_data_collected])
        TicketNeedsAdjudicationDetails.objects.bulk_create([x.ticket_details for x in ticket_data_collected])
        # makes flat list from list of lists models
        duplicates_models_to_create_flat = list(
            itertools.chain(*[x.possible_duplicates_throughs for x in ticket_data_collected])
        )
        PossibleDuplicateThrough.objects.bulk_create(duplicates_models_to_create_flat)

    def _generate_signature(self, document: Document) -> str:
        if document.type.valid_for_deduplication:
            return f"{document.type_id}--{document.document_number}--{document.country_id}"
        else:
            return f"{document.document_number}--{document.country_id}"

    def _prepare_grievance_ticket_documents_deduplication(
        self,
        main_individual: Individual,
        possible_duplicates_individuals: List[Individual],
        business_area: BusinessArea,
        registration_data_import: Optional[RegistrationDataImport],
        possible_duplicates_through_dict: Dict,
    ) -> Optional[TicketData]:
        from hct_mis_api.apps.grievance.models import (
            GrievanceTicket,
            TicketNeedsAdjudicationDetails,
        )

        new_duplicates_set = {str(main_individual.id), *[str(x.id) for x in possible_duplicates_individuals]}
        for duplicates_set in possible_duplicates_through_dict.values():
            if new_duplicates_set.issubset(duplicates_set):
                return None
        household = main_individual.household
        admin_level_2 = household.admin2 if household else None
        area = household.village if household else ""

        ticket = GrievanceTicket(
            category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
            business_area=business_area,
            admin2=admin_level_2,
            area=area,
            registration_data_import=registration_data_import,
        )
        ticket_details = TicketNeedsAdjudicationDetails(
            ticket=ticket,
            golden_records_individual=main_individual,
            is_multiple_duplicates_version=True,
            selected_individual=None,
        )
        PossibleDuplicateThrough = TicketNeedsAdjudicationDetails.possible_duplicates.through
        possible_duplicates_throughs = []
        for possible_duplicate_individual in set(possible_duplicates_individuals):
            possible_duplicates_throughs.append(
                PossibleDuplicateThrough(
                    individual=possible_duplicate_individual, ticketneedsadjudicationdetails=ticket_details
                )
            )
        return TicketData(ticket, ticket_details, possible_duplicates_throughs)
