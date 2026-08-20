"""Tests for DeduplicateTask extracted helper methods."""

from collections import defaultdict
from unittest.mock import MagicMock, patch
import uuid

from psycopg2._psycopg import IntegrityError
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    IndividualFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.household.const import (
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    NEEDS_ADJUDICATION,
    NOT_PROCESSED,
    UNIQUE_IN_BATCH,
)
from hope.apps.registration_data.tasks.deduplicate import (
    DeduplicateTask,
    DeduplicationResult,
    HardDocumentDeduplication,
)
from hope.models import (
    BusinessArea,
    Document,
    Individual,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def task(business_area: BusinessArea, program: Program) -> DeduplicateTask:
    return DeduplicateTask(business_area.slug, str(program.id))


@pytest.fixture
def rdi(program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        status=RegistrationDataImport.DEDUPLICATION,
    )


@pytest.fixture
def pending_household_for_finalize(rdi, business_area):
    return PendingHouseholdFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=business_area,
    )


@pytest.fixture
def pending_individuals_for_finalize(rdi, business_area, pending_household_for_finalize):
    return [
        PendingIndividualFactory(
            registration_data_import=rdi,
            program=rdi.program,
            business_area=business_area,
            household=pending_household_for_finalize,
        )
        for _ in range(2)
    ]


@pytest.fixture
def pending_individual_with_alt_phone(rdi, business_area):
    return PendingIndividualFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=business_area,
        household=None,
        phone_no="123-123-123",
        phone_no_alternative="+48 609 456 789",
    )


@pytest.fixture
def individual_without_household(business_area, program):
    return IndividualFactory(
        business_area=business_area,
        program=program,
        household=None,
    )


@pytest.fixture
def ignore_withdraw_business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Ukraine", slug="ukraine", deduplication_ignore_withdraw=True)


@pytest.fixture
def ignore_withdraw_program(ignore_withdraw_business_area) -> Program:
    return ProgramFactory(business_area=ignore_withdraw_business_area)


@pytest.fixture
def ignore_withdraw_task(ignore_withdraw_business_area, ignore_withdraw_program) -> DeduplicateTask:
    return DeduplicateTask(ignore_withdraw_business_area.slug, str(ignore_withdraw_program.id))


@pytest.fixture
def withdrawn_individual(ignore_withdraw_business_area, ignore_withdraw_program):
    return IndividualFactory(
        business_area=ignore_withdraw_business_area,
        program=ignore_withdraw_program,
        household=None,
        withdrawn=True,
    )


@pytest.fixture
def searched_individual(ignore_withdraw_business_area, ignore_withdraw_program):
    return IndividualFactory(
        business_area=ignore_withdraw_business_area,
        program=ignore_withdraw_program,
        household=None,
    )


@pytest.fixture
def strict_business_area() -> BusinessArea:
    return BusinessAreaFactory(
        name="Somalia",
        slug="somalia",
        deduplication_duplicate_score=14.0,
        deduplication_possible_duplicate_score=11.0,
        deduplication_batch_duplicates_percentage=100,
        deduplication_batch_duplicates_allowed=0,
        deduplication_golden_record_duplicates_percentage=100,
        deduplication_golden_record_duplicates_allowed=0,
    )


@pytest.fixture
def strict_program(strict_business_area) -> Program:
    return ProgramFactory(business_area=strict_business_area)


@pytest.fixture
def strict_task(strict_business_area, strict_program) -> DeduplicateTask:
    return DeduplicateTask(strict_business_area.slug, str(strict_program.id))


@pytest.fixture
def strict_rdi(strict_program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        program=strict_program,
        business_area=strict_program.business_area,
        status=RegistrationDataImport.DEDUPLICATION,
    )


@pytest.fixture
def strict_pending_individuals(strict_rdi, strict_business_area):
    return [
        PendingIndividualFactory(
            registration_data_import=strict_rdi,
            program=strict_rdi.program,
            business_area=strict_business_area,
            household=None,
        )
        for _ in range(2)
    ]


# --- _check_duplicates_threshold ---


def test_check_max_duplicates_returns_none_when_below(task):
    assert task._check_max_duplicates(3, 10, "batch") is None


def test_check_max_duplicates_returns_error_when_exceeded(task):
    result = task._check_max_duplicates(10, 5, "batch")
    assert "exceed the maximum allowed (5)" in result


def test_check_duplicates_percentage_returns_none_when_below(task):
    assert task._check_duplicates_percentage(3, 5, 100, 10.0, "batch") is None


def test_check_duplicates_percentage_returns_none_when_single_individual(task):
    assert task._check_duplicates_percentage(8, 5, 1, 10.0, "batch") is None


def test_check_duplicates_percentage_returns_error_when_exceeded(task):
    result = task._check_duplicates_percentage(8, 5, 100, 10.0, "population")
    assert "The percentage of records (10.0%)" in result


# --- _set_deduplication_batch_status ---


def test_set_deduplication_batch_status_duplicates(task):
    result = MagicMock()
    result.results_data = {"duplicates": [{"some": "data"}]}
    pending = MagicMock()
    task._set_deduplication_batch_status(result, pending)
    assert pending.deduplication_batch_status == DUPLICATE_IN_BATCH


def test_set_deduplication_batch_status_unique(task):
    result = MagicMock()
    result.results_data = {"duplicates": []}
    pending = MagicMock()
    task._set_deduplication_batch_status(result, pending)
    assert pending.deduplication_batch_status == UNIQUE_IN_BATCH


# --- _set_error_message_and_status ---


def test_set_error_message_and_status(task, rdi):
    task._set_error_message_and_status(rdi, "Some error occurred")
    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.DEDUPLICATION_FAILED
    assert rdi.error_message == "Some error occurred"


# --- _finalize_successful_deduplication ---


def test_finalize_successful_deduplication(task, rdi, pending_household_for_finalize, pending_individuals_for_finalize):
    task._finalize_successful_deduplication(
        rdi,
        duplicates_in_batch=set(),
        possible_duplicates_in_batch=set(),
        duplicates_in_population=set(),
        possible_duplicates_in_population=set(),
    )
    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.IN_REVIEW
    assert rdi.error_message == ""


# --- HardDocumentDeduplication._build_document_signatures ---


def test_build_document_signatures_empty():
    dedup = HardDocumentDeduplication()
    documents_numbers, new_sigs, per_individual_dict, duplicated = dedup._build_document_signatures([])

    assert documents_numbers == []
    assert new_sigs == []
    assert dict(per_individual_dict) == {}
    assert duplicated == []


def test_build_document_signatures_single_doc():
    dedup = HardDocumentDeduplication()
    individual_id = uuid.uuid4()

    expected_sig = "passport--DOC-001--AFG"
    doc = MagicMock()
    doc.document_number = "DOC-001"
    doc.individual_id = individual_id
    doc.dedup_signature = expected_sig

    documents_numbers, new_sigs, per_individual_dict, duplicated = dedup._build_document_signatures([doc])

    assert documents_numbers == ["DOC-001"]
    assert new_sigs == [expected_sig]
    assert per_individual_dict[str(individual_id)] == [expected_sig]
    assert duplicated == []


def test_build_document_signatures_duplicates():
    dedup = HardDocumentDeduplication()
    individual_id_1 = uuid.uuid4()
    individual_id_2 = uuid.uuid4()

    expected_sig = "passport--DOC-001--AFG"
    doc1 = MagicMock()
    doc1.document_number = "DOC-001"
    doc1.individual_id = individual_id_1
    doc1.dedup_signature = expected_sig

    doc2 = MagicMock()
    doc2.document_number = "DOC-001"
    doc2.individual_id = individual_id_2
    doc2.dedup_signature = expected_sig

    documents_numbers, new_sigs, per_individual_dict, duplicated = dedup._build_document_signatures([doc1, doc2])

    assert documents_numbers == ["DOC-001", "DOC-001"]
    assert new_sigs == [expected_sig, expected_sig]
    assert per_individual_dict[str(individual_id_1)] == [expected_sig]
    assert per_individual_dict[str(individual_id_2)] == [expected_sig]
    assert duplicated == [expected_sig, expected_sig]


# --- HardDocumentDeduplication._get_existing_duplicates_through ---


@pytest.fixture
def grievance_individual_1(rdi, business_area):
    return PendingIndividualFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=business_area,
    )


@pytest.fixture
def grievance_individual_2(rdi, business_area):
    return PendingIndividualFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=business_area,
    )


@pytest.fixture
def ticket_with_possible_duplicate(grievance_individual_1, grievance_individual_2, business_area, rdi):
    from extras.test_utils.factories import GrievanceTicketFactory, TicketNeedsAdjudicationDetailsFactory
    from hope.apps.grievance.models import GrievanceTicket

    ticket = GrievanceTicketFactory(
        business_area=business_area,
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
    )
    ticket.programs.add(rdi.program)
    details = TicketNeedsAdjudicationDetailsFactory(
        ticket=ticket,
        golden_records_individual=grievance_individual_1,
    )
    details.possible_duplicates.add(grievance_individual_2)
    return details


def test_get_existing_duplicates_through_returns_dict(
    task, ticket_with_possible_duplicate, grievance_individual_1, grievance_individual_2
):
    result = HardDocumentDeduplication()._get_existing_duplicates_through({grievance_individual_2.id})
    assert len(result) == 1
    details_id = str(ticket_with_possible_duplicate.id)
    assert str(grievance_individual_2.id) in result[details_id]
    assert str(grievance_individual_1.id) in result[details_id]


def test_get_existing_duplicates_through_empty_set(task):
    result = HardDocumentDeduplication()._get_existing_duplicates_through(set())
    assert result == {}


# --- HardDocumentDeduplication._create_deduplication_tickets ---


@pytest.fixture
def grievance_household(rdi, business_area):
    return PendingHouseholdFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=business_area,
    )


@pytest.fixture
def grievance_individual_with_household_1(rdi, business_area, grievance_household):
    return PendingIndividualFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=business_area,
        household=grievance_household,
    )


@pytest.fixture
def grievance_individual_with_household_2(rdi, business_area, grievance_household):
    return PendingIndividualFactory(
        registration_data_import=rdi,
        program=rdi.program,
        business_area=business_area,
        household=grievance_household,
    )


def test_create_deduplication_tickets_creates_ticket(
    task, rdi, grievance_individual_with_household_1, grievance_individual_with_household_2
):
    from hope.apps.grievance.models import GrievanceTicket, TicketNeedsAdjudicationDetails

    doc1 = MagicMock()
    doc1.individual = grievance_individual_with_household_1
    doc2 = MagicMock()
    doc2.individual = grievance_individual_with_household_2
    ticket_data_dict = {
        "sig1": {"original": doc1, "possible_duplicates": [doc2]},
    }
    dedup = HardDocumentDeduplication()
    dedup._create_deduplication_tickets(ticket_data_dict, {}, rdi)
    assert GrievanceTicket.objects.filter(
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
    ).exists()
    assert TicketNeedsAdjudicationDetails.objects.filter(
        golden_records_individual=grievance_individual_with_household_1,
    ).exists()


def test_create_deduplication_tickets_skips_when_prepared_ticket_is_none(
    task, rdi, grievance_individual_with_household_1, grievance_individual_with_household_2
):
    from unittest.mock import patch as mock_patch

    from hope.apps.grievance.models import GrievanceTicket

    doc1 = MagicMock()
    doc1.individual = grievance_individual_with_household_1
    doc2 = MagicMock()
    doc2.individual = grievance_individual_with_household_2
    ticket_data_dict = {
        "sig1": {"original": doc1, "possible_duplicates": [doc2]},
    }
    dedup = HardDocumentDeduplication()
    with mock_patch.object(dedup, "_prepare_grievance_ticket_documents_deduplication", return_value=None):
        dedup._create_deduplication_tickets(ticket_data_dict, {}, rdi)
    assert not GrievanceTicket.objects.filter(
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
    ).exists()


# --- _prepare_fields ---


def test_prepare_fields_converts_alternative_phone_to_raw_input(task, pending_individual_with_alt_phone):
    fields = task._prepare_fields(
        pending_individual_with_alt_phone,
        (
            "given_name",
            "full_name",
            "middle_name",
            "family_name",
            "phone_no",
            "phone_no_alternative",
            "relationship",
            "sex",
            "birth_date",
        ),
        {"identities": ("number", "partner.name")},
    )
    assert fields["phone_no"] == "123-123-123"
    assert fields["phone_no_alternative"] == "+48 609 456 789"


# --- _prepare_query_dict ---


def test_prepare_query_dict_skips_none_field_values(task):
    individual_fields = {
        "given_name": "Test",
        "family_name": "Testowski",
        "full_name": "Test Testowski",
        "birth_date": None,
        "sex": "MALE",
    }
    query_dict = task._prepare_query_dict(str(uuid.uuid4()), individual_fields, 10.0)
    should_queries = query_dict["query"]["bool"]["should"]
    assert len(should_queries) == 2
    assert should_queries[1] == {"match": {"sex": {"query": "MALE", "boost": 1, "operator": "OR"}}}


def test_prepare_query_dict_skips_fields_without_meta(task):
    individual_fields = {
        "given_name": "Test",
        "family_name": "Testowski",
        "full_name": "Test Testowski",
        "unicef_id": "IND-123",
        "sex": "MALE",
    }
    query_dict = task._prepare_query_dict(str(uuid.uuid4()), individual_fields, 10.0)
    should_queries = query_dict["query"]["bool"]["should"]
    assert len(should_queries) == 2
    assert should_queries[1] == {"match": {"sex": {"query": "MALE", "boost": 1, "operator": "OR"}}}


# --- _prepare_queries_for_names_from_fields ---


def test_prepare_queries_for_names_returns_empty_when_all_names_missing(task):
    fields = {"given_name": None, "family_name": None, "full_name": None}
    assert task._prepare_queries_for_names_from_fields(fields) == []


# --- _prepare_identities_queries_from_fields ---


def test_prepare_identities_queries_builds_query_for_complete_identity(task):
    queries = task._prepare_identities_queries_from_fields([{"number": "DOC-123", "partner": "UNHCR"}])
    assert queries == [
        {
            "bool": {
                "must": [
                    {"match": {"identities.number": {"query": "DOC-123"}}},
                    {"match": {"identities.partner": {"query": "UNHCR"}}},
                ],
                "boost": 4,
            },
        }
    ]


def test_prepare_identities_queries_skips_identity_without_partner(task):
    assert task._prepare_identities_queries_from_fields([{"number": "DOC-123", "partner": None}]) == []


# --- _get_deduplicate_result ---


def test_get_deduplicate_result_skips_withdrawn_hits(ignore_withdraw_task, withdrawn_individual, searched_individual):
    hit = MagicMock()
    hit.id = withdrawn_individual.id
    hit.meta.score = 20.0
    document = MagicMock()
    document.search.return_value.params.return_value.update_from_dict.return_value.execute.return_value = [hit]

    result = ignore_withdraw_task._get_deduplicate_result({}, 14.0, document, searched_individual)

    assert result.duplicates == []
    assert result.possible_duplicates == []
    assert result.results_data == {"duplicates": [], "possible_duplicates": []}


def test_get_deduplicate_result_ignores_low_score_hit_for_other_document(task, individual_without_household):
    hit = MagicMock()
    hit.id = uuid.uuid4()
    hit.meta.score = 5.0
    document = MagicMock()
    document.search.return_value.params.return_value.update_from_dict.return_value.execute.return_value = [hit]

    result = task._get_deduplicate_result({}, 14.0, document, individual_without_household)

    assert result.duplicates == []
    assert result.possible_duplicates == []
    assert result.results_data == {"duplicates": [], "possible_duplicates": []}


# --- deduplicate_individuals_from_other_source ---


def test_deduplicate_individuals_from_other_source_marks_possible_duplicates(task, individual_without_household):
    dedup_result = DeduplicationResult(
        duplicates=[],
        possible_duplicates=[str(uuid.uuid4())],
        original_individuals_ids_duplicates=[],
        original_individuals_ids_possible_duplicates=[],
        results_data={"duplicates": [], "possible_duplicates": []},
    )
    individuals = Individual.objects.filter(id=individual_without_household.id)
    with (
        patch("hope.apps.registration_data.tasks.deduplicate.ensure_index_ready"),
        patch.object(task, "_deduplicate_single_individual", return_value=dedup_result),
    ):
        task.deduplicate_individuals_from_other_source(individuals)

    individual_without_household.refresh_from_db()
    assert individual_without_household.deduplication_golden_record_status == NEEDS_ADJUDICATION


# --- deduplicate_pending_individuals error paths ---


def test_deduplicate_pending_individuals_batch_error_marks_unchecked_as_not_processed(
    strict_task, strict_rdi, strict_pending_individuals
):
    batch_result = DeduplicationResult(
        duplicates=[str(uuid.uuid4())],
        possible_duplicates=[],
        original_individuals_ids_duplicates=[str(uuid.uuid4())],
        original_individuals_ids_possible_duplicates=[],
        results_data={"duplicates": [{"score": 15.0}], "possible_duplicates": []},
    )
    with (
        patch("hope.apps.registration_data.tasks.deduplicate.populate_index"),
        patch("hope.apps.registration_data.tasks.deduplicate.ensure_index_ready"),
        patch("hope.apps.registration_data.tasks.deduplicate.remove_elasticsearch_documents_by_matching_ids"),
        patch.object(strict_task, "_deduplicate_single_pending_individual", return_value=batch_result),
    ):
        strict_task.deduplicate_pending_individuals(strict_rdi)

    strict_rdi.refresh_from_db()
    assert strict_rdi.status == RegistrationDataImport.DEDUPLICATION_FAILED
    assert "batch" in strict_rdi.error_message
    assert "exceed the maximum allowed (0)" in strict_rdi.error_message
    assert PendingIndividual.objects.filter(deduplication_batch_status=NOT_PROCESSED).count() == 1
    assert PendingIndividual.objects.filter(deduplication_golden_record_status=NOT_PROCESSED).count() == 1
    assert PendingIndividual.objects.filter(deduplication_batch_status=DUPLICATE_IN_BATCH).count() == 1


def test_deduplicate_pending_individuals_population_error_sets_deduplication_failed(
    strict_task, strict_rdi, strict_pending_individuals
):
    batch_result = DeduplicationResult(
        duplicates=[],
        possible_duplicates=[],
        original_individuals_ids_duplicates=[],
        original_individuals_ids_possible_duplicates=[],
        results_data={"duplicates": [], "possible_duplicates": []},
    )
    population_result = DeduplicationResult(
        duplicates=[str(uuid.uuid4())],
        possible_duplicates=[],
        original_individuals_ids_duplicates=[str(uuid.uuid4())],
        original_individuals_ids_possible_duplicates=[],
        results_data={"duplicates": [{"score": 15.0}], "possible_duplicates": []},
    )
    with (
        patch("hope.apps.registration_data.tasks.deduplicate.populate_index"),
        patch("hope.apps.registration_data.tasks.deduplicate.ensure_index_ready"),
        patch("hope.apps.registration_data.tasks.deduplicate.remove_elasticsearch_documents_by_matching_ids"),
        patch.object(strict_task, "_deduplicate_single_pending_individual", return_value=batch_result),
        patch.object(strict_task, "_deduplicate_single_individual", return_value=population_result),
    ):
        strict_task.deduplicate_pending_individuals(strict_rdi)

    strict_rdi.refresh_from_db()
    assert strict_rdi.status == RegistrationDataImport.DEDUPLICATION_FAILED
    assert "population" in strict_rdi.error_message
    assert "exceed the maximum allowed (0)" in strict_rdi.error_message
    assert PendingIndividual.objects.filter(deduplication_golden_record_status=DUPLICATE).count() == 1


# --- HardDocumentDeduplication.deduplicate ---


def test_hard_document_deduplication_raises_on_bulk_update_integrity_error(program):
    with (
        patch.object(Document.objects, "bulk_update", side_effect=IntegrityError("bulk update failed")),
        pytest.raises(IntegrityError, match="bulk update failed"),
    ):
        HardDocumentDeduplication().deduplicate(Document.objects.none(), program=program)


# --- HardDocumentDeduplication._deduplication_documents ---


def test_deduplication_documents_invalidates_batch_duplicate_of_same_individual():
    individual_id = uuid.uuid4()
    signature = "passport--DOC-001--AFG"

    doc1 = MagicMock()
    doc1.document_number = "DOC-001"
    doc1.individual_id = individual_id
    doc1.type.valid_for_deduplication = True
    doc1.type_id = "passport"
    doc1.country_id = "AFG"
    doc1.dedup_signature = signature

    doc2 = MagicMock()
    doc2.document_number = "DOC-001"
    doc2.individual_id = individual_id
    doc2.type.valid_for_deduplication = True
    doc2.type_id = "passport"
    doc2.country_id = "AFG"
    doc2.dedup_signature = signature

    per_individual_dict = defaultdict(list)
    per_individual_dict[str(individual_id)] = [signature, signature]

    HardDocumentDeduplication()._deduplication_documents(
        {},
        set(),
        set(),
        [doc1, doc2],
        new_document_signatures_duplicated_in_batch=[signature, signature],
        new_document_signatures_in_batch_per_individual_dict=per_individual_dict,
        new_documents=MagicMock(),
        possible_duplicates_individuals_id_set=set(),
        ticket_data_dict={},
    )

    assert doc1.status == Document.STATUS_INVALID
    assert doc2.status == Document.STATUS_VALID


# --- deduplicate_individuals_against_population ---


def test_deduplicate_individuals_against_population_marks_duplicates(task, individual_without_household):
    dedup_result = DeduplicationResult(
        duplicates=[str(individual_without_household.id)],
        possible_duplicates=[],
        original_individuals_ids_duplicates=[],
        original_individuals_ids_possible_duplicates=[],
        results_data={
            "duplicates": [{"id": str(individual_without_household.id), "score": 15.0}],
            "possible_duplicates": [],
        },
    )
    individuals = Individual.objects.filter(id=individual_without_household.id)
    with (
        patch("hope.apps.registration_data.tasks.deduplicate.ensure_index_ready"),
        patch.object(task, "_deduplicate_single_individual", return_value=dedup_result),
    ):
        task.deduplicate_individuals_against_population(individuals)

    individual_without_household.refresh_from_db()
    assert individual_without_household.deduplication_golden_record_status == DUPLICATE
    assert individual_without_household.deduplication_golden_record_results == dedup_result.results_data


def test_deduplicate_individuals_against_population_marks_possible_duplicates(task, individual_without_household):
    dedup_result = DeduplicationResult(
        duplicates=[],
        possible_duplicates=[str(individual_without_household.id)],
        original_individuals_ids_duplicates=[],
        original_individuals_ids_possible_duplicates=[],
        results_data={
            "duplicates": [],
            "possible_duplicates": [{"id": str(individual_without_household.id), "score": 12.0}],
        },
    )
    individuals = Individual.objects.filter(id=individual_without_household.id)
    with (
        patch("hope.apps.registration_data.tasks.deduplicate.ensure_index_ready"),
        patch.object(task, "_deduplicate_single_individual", return_value=dedup_result),
    ):
        task.deduplicate_individuals_against_population(individuals)

    individual_without_household.refresh_from_db()
    assert individual_without_household.deduplication_golden_record_status == NEEDS_ADJUDICATION
