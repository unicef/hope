from decimal import Decimal
import uuid

import pytest

from extras.test_utils.factories import (
    BiographicDeduplicationEngineSimilarityPairFactory,
    BiometricDeduplicationEngineSimilarityPairFactory,
    BusinessAreaFactory,
    IndividualFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.const import (
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    UNIQUE,
)
from hope.apps.registration_data.api.deduplication_engine import (
    BiographicHDEFinding,
    BiometricHDEFinding,
)
from hope.apps.registration_data.services.deduplication_engine import (
    BiographicDeduplicationEngineService,
    BiometricDeduplicationEngineService,
)
from hope.models import (
    BiographicDedupeSimilarityPair,
    BiometricDedupeSimilarityPair,
    BusinessArea,
    Individual,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def mock_deduplication_engine_env_vars(settings) -> None:
    settings.DEDUPLICATION_ENGINE_API_KEY = "TEST"
    settings.DEDUPLICATION_ENGINE_API_URL = "TEST"


@pytest.fixture
def biometric_deduplication_context() -> dict[str, object]:
    business_area = BusinessAreaFactory(
        slug="afghanistan", name="Afghanistan", ingest_source=BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY
    )
    user = UserFactory()
    program = ProgramFactory(
        business_area=business_area,
        biometric_deduplication_enabled=True,
    )
    return {
        "business_area": business_area,
        "user": user,
        "program": program,
    }


@pytest.fixture
def biographic_program() -> Program:
    return ProgramFactory()


@pytest.fixture
def biographic_individuals(biographic_program: Program) -> list[Individual]:
    created = [
        IndividualFactory(
            program=biographic_program,
            business_area=biographic_program.business_area,
            country_workspace_id="CW-001",
        ),
        IndividualFactory(
            program=biographic_program,
            business_area=biographic_program.business_area,
            country_workspace_id="CW-002",
        ),
    ]
    return sorted(created, key=lambda individual: str(individual.id))


@pytest.fixture
def biometric_persisted_findings() -> list[dict]:
    return [
        {
            "first": {"reference_pk": "CW-001"},
            "second": {"reference_pk": "CW-002"},
            "score": 0.95,
            "status_code": "200",
        },
        {"first": {"reference_pk": "CW-003"}, "second": {"reference_pk": "CW-004"}, "score": 0.0, "status_code": "412"},
    ]


@pytest.fixture
def biographic_findings() -> list[dict]:
    return [
        {
            "first": {"reference_pk": "CW-001"},
            "second": {"reference_pk": "CW-002"},
            "score": 12.5,
            "proximity_to_score": 2.5,
        },
        {
            "first": {"reference_pk": "CW-003"},
            "second": {"reference_pk": "CW-004"},
            "score": 8.0,
            "proximity_to_score": -2.0,
        },
    ]


@pytest.fixture
def biometric_finding_with_status_code(status_code: str) -> list[dict]:
    return [
        {
            "first": {"reference_pk": "CW-001"},
            "second": {"reference_pk": "CW-002"},
            "score": 0.0,
            "status_code": status_code,
        }
    ]


@pytest.fixture
def biometric_finding_with_both_reference_pks_empty() -> list[dict]:
    return [
        {
            "first": {"reference_pk": None},
            "second": {"reference_pk": ""},
            "score": 0.5,
            "status_code": "200",
        }
    ]


@pytest.fixture
def biographic_finding_with_both_reference_pks_empty() -> list[dict]:
    return [
        {
            "first": {"reference_pk": None},
            "second": {"reference_pk": ""},
            "score": 12.5,
            "proximity_to_score": 2.5,
        }
    ]


@pytest.fixture
def biometric_finding_with_empty_second_reference_pk() -> list[dict]:
    return [
        {
            "first": {"reference_pk": "CW-001"},
            "second": {"reference_pk": ""},
            "score": 0.5,
            "status_code": "200",
        }
    ]


@pytest.fixture
def biographic_finding_with_empty_second_reference_pk() -> list[dict]:
    return [
        {
            "first": {"reference_pk": "CW-001"},
            "second": {"reference_pk": ""},
            "score": 12.5,
            "proximity_to_score": 2.5,
        }
    ]


@pytest.fixture
def biographic_findings_for_individuals(biographic_individuals: list[Individual]) -> list[BiographicHDEFinding]:
    lower, higher = biographic_individuals
    return [
        BiographicHDEFinding(
            score=12.5,
            first=higher.country_workspace_id,
            second=lower.country_workspace_id,
            proximity_to_score=2.5,
        )
    ]


@pytest.fixture
def biometric_program() -> Program:
    return ProgramFactory()


@pytest.fixture
def biometric_rdi(biometric_program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        program=biometric_program,
        business_area=biometric_program.business_area,
        status=RegistrationDataImport.IN_REVIEW,
    )


@pytest.fixture
def biometric_rdi_individuals(biometric_program: Program, biometric_rdi: RegistrationDataImport) -> list[Individual]:
    created = PendingIndividualFactory.create_batch(
        2,
        program=biometric_program,
        business_area=biometric_program.business_area,
        registration_data_import=biometric_rdi,
    )
    return sorted(created, key=lambda individual: str(individual.id))


@pytest.fixture
def biometric_zero_score_batch_pair(
    biometric_program: Program, biometric_rdi_individuals: list[Individual]
) -> BiometricDedupeSimilarityPair:
    individual1, individual2 = biometric_rdi_individuals
    return BiometricDeduplicationEngineSimilarityPairFactory(
        program=biometric_program, individual1=individual1, individual2=individual2, similarity_score=Decimal(0)
    )


@pytest.fixture
def biometric_zero_score_population_pair(
    biometric_program: Program, biometric_rdi_individuals: list[Individual]
) -> BiometricDedupeSimilarityPair:
    population_individual = IndividualFactory(program=biometric_program, business_area=biometric_program.business_area)
    individual1, individual2 = sorted(
        [biometric_rdi_individuals[0], population_individual], key=lambda ind: str(ind.id)
    )
    return BiometricDeduplicationEngineSimilarityPairFactory(
        program=biometric_program, individual1=individual1, individual2=individual2, similarity_score=Decimal(0)
    )


def test_biometric_get_duplicates_for_rdi_against_batch_drops_zero_score_pair(
    biometric_rdi: RegistrationDataImport, biometric_zero_score_batch_pair: BiometricDedupeSimilarityPair
) -> None:
    result = BiometricDeduplicationEngineService().get_duplicates_for_rdi_against_batch(biometric_rdi)

    assert list(result) == []


def test_biometric_get_duplicates_for_rdi_against_population_drops_zero_score_pair_by_default(
    biometric_rdi: RegistrationDataImport, biometric_zero_score_population_pair: BiometricDedupeSimilarityPair
) -> None:
    result = BiometricDeduplicationEngineService().get_duplicates_for_rdi_against_population(biometric_rdi)

    assert list(result) == []


def test_store_results(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    individuals = IndividualFactory.create_batch(3, program=program, business_area=program.business_area)
    ind1, ind2, ind3 = sorted(individuals, key=lambda x: x.id)

    service = BiometricDeduplicationEngineService()
    hde_findings = [
        BiometricHDEFinding(score=0.5, first=str(ind2.id), second=str(ind1.id), status_code="200"),
        BiometricHDEFinding(score=0.5, first=str(ind1.id), second=str(ind2.id), status_code="200"),
        BiometricHDEFinding(score=0.7, first=str(ind1.id), second=str(ind3.id), status_code="200"),
        BiometricHDEFinding(score=0.8, first=str(ind3.id), second=str(ind2.id), status_code="200"),
        BiometricHDEFinding(score=0.9, first=str(ind3.id), second=str(ind3.id), status_code="200"),
    ]

    service.store_biometric_similarity_pairs(program, hde_findings)

    assert program.deduplication_engine_similarity_pairs.count() == 3
    assert program.deduplication_engine_similarity_pairs.filter(
        individual1=ind1, individual2=ind2, similarity_score=50.00
    ).exists()
    assert program.deduplication_engine_similarity_pairs.filter(
        individual1=ind1, individual2=ind3, similarity_score=70.00
    ).exists()
    assert program.deduplication_engine_similarity_pairs.filter(
        individual1=ind2, individual2=ind3, similarity_score=80.00
    ).exists()


def test_store_results_no_individuals(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    service = BiometricDeduplicationEngineService()
    hde_findings = [
        BiometricHDEFinding(score=0.0, status_code="404"),
    ]

    service.store_biometric_similarity_pairs(program, hde_findings)
    assert program.deduplication_engine_similarity_pairs.count() == 0


def test_store_results_1_individual(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    ind1 = IndividualFactory.create_batch(1, program=program, business_area=program.business_area)[0]
    service = BiometricDeduplicationEngineService()
    hde_findings = [
        BiometricHDEFinding(score=0.0, first=str(ind1.id), status_code="429"),
    ]

    service.store_biometric_similarity_pairs(program, hde_findings)

    assert program.deduplication_engine_similarity_pairs.count() == 1
    assert program.deduplication_engine_similarity_pairs.filter(
        individual1=ind1, individual2=None, similarity_score=0.00
    ).exists()


def test_store_results_not_existing_individual(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    ind1 = IndividualFactory.create_batch(1, program=program, business_area=program.business_area)[0]
    service = BiometricDeduplicationEngineService()
    hde_findings = [
        BiometricHDEFinding(score=70.0, first=str(ind1.id), second=str(uuid.uuid4()), status_code="429"),
    ]

    service.store_biometric_similarity_pairs(program, hde_findings)

    assert program.deduplication_engine_similarity_pairs.count() == 0


def test_biometric_parse_findings_keeps_persisted_status_codes(biometric_persisted_findings: list[dict]) -> None:
    pairs = BiometricDeduplicationEngineService().parse_findings(biometric_persisted_findings)

    assert pairs == [
        BiometricHDEFinding(score=0.95, status_code="200", first="CW-001", second="CW-002"),
        BiometricHDEFinding(score=0.0, status_code="412", first="CW-003", second="CW-004"),
    ]


def test_biographic_parse_findings_keeps_every_finding(biographic_findings: list[dict]) -> None:
    pairs = BiographicDeduplicationEngineService().parse_findings(biographic_findings)

    assert pairs == [
        BiographicHDEFinding(score=12.5, first="CW-001", second="CW-002", proximity_to_score=2.5),
        BiographicHDEFinding(score=8.0, first="CW-003", second="CW-004", proximity_to_score=-2.0),
    ]


@pytest.mark.parametrize("status_code", ["404", "500"])
def test_biometric_parse_findings_drops_non_persisted_status_code(
    status_code: str, biometric_finding_with_status_code: list[dict]
) -> None:
    assert BiometricDeduplicationEngineService().parse_findings(biometric_finding_with_status_code) == []


def test_biometric_parse_findings_drops_finding_with_both_reference_pks_empty(
    biometric_finding_with_both_reference_pks_empty: list[dict],
) -> None:
    assert BiometricDeduplicationEngineService().parse_findings(biometric_finding_with_both_reference_pks_empty) == []


def test_biographic_parse_findings_drops_finding_with_both_reference_pks_empty(
    biographic_finding_with_both_reference_pks_empty: list[dict],
) -> None:
    assert BiographicDeduplicationEngineService().parse_findings(biographic_finding_with_both_reference_pks_empty) == []


def test_biometric_parse_findings_normalises_empty_reference_pk_to_none(
    biometric_finding_with_empty_second_reference_pk: list[dict],
) -> None:
    pairs = BiometricDeduplicationEngineService().parse_findings(biometric_finding_with_empty_second_reference_pk)

    assert pairs == [BiometricHDEFinding(score=0.5, status_code="200", first="CW-001", second=None)]


def test_biographic_parse_findings_normalises_empty_reference_pk_to_none(
    biographic_finding_with_empty_second_reference_pk: list[dict],
) -> None:
    pairs = BiographicDeduplicationEngineService().parse_findings(biographic_finding_with_empty_second_reference_pk)

    assert pairs == [BiographicHDEFinding(score=12.5, first="CW-001", second=None, proximity_to_score=2.5)]


@pytest.mark.parametrize("service_class", [BiometricDeduplicationEngineService, BiographicDeduplicationEngineService])
def test_parse_findings_empty_input(service_class: type) -> None:
    assert service_class().parse_findings([]) == []


def test_store_biographic_similarity_pairs_persists_raw_score_and_proximity_to_score(
    biographic_program: Program,
    biographic_individuals: list[Individual],
    biographic_findings_for_individuals: list[BiographicHDEFinding],
) -> None:
    lower, higher = biographic_individuals

    BiographicDeduplicationEngineService().store_biographic_similarity_pairs(
        biographic_program, biographic_findings_for_individuals
    )

    pair = BiographicDedupeSimilarityPair.objects.get()
    assert (pair.individual1_id, pair.individual2_id, pair.similarity_score, pair.proximity_to_score) == (
        lower.id,
        higher.id,
        Decimal("12.50"),
        Decimal("2.50"),
    )


@pytest.fixture
def stats_program() -> Program:
    return ProgramFactory()


@pytest.fixture
def stats_rdi(stats_program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        program=stats_program,
        business_area=stats_program.business_area,
        status=RegistrationDataImport.IN_REVIEW,
    )


@pytest.fixture
def stats_rdi_individuals(stats_program: Program, stats_rdi: RegistrationDataImport) -> list[PendingIndividual]:
    created = PendingIndividualFactory.create_batch(
        2,
        program=stats_program,
        business_area=stats_program.business_area,
        registration_data_import=stats_rdi,
    )
    return sorted(created, key=lambda individual: str(individual.id))


@pytest.fixture
def stats_population_individual(stats_program: Program) -> Individual:
    return IndividualFactory(program=stats_program, business_area=stats_program.business_area)


@pytest.fixture
def stats_population_pair(
    stats_program: Program,
    stats_rdi_individuals: list[PendingIndividual],
    stats_population_individual: Individual,
) -> BiographicDedupeSimilarityPair:
    return BiographicDeduplicationEngineSimilarityPairFactory(
        program=stats_program,
        individual1=stats_rdi_individuals[0],
        individual2=stats_population_individual,
        similarity_score=Decimal("12.50"),
        proximity_to_score=Decimal("2.50"),
    )


@pytest.fixture
def stats_batch_pair(
    stats_program: Program, stats_rdi_individuals: list[PendingIndividual]
) -> BiographicDedupeSimilarityPair:
    return BiographicDeduplicationEngineSimilarityPairFactory(
        program=stats_program,
        individual1=stats_rdi_individuals[0],
        individual2=stats_rdi_individuals[1],
        similarity_score=Decimal("9.00"),
        proximity_to_score=Decimal("-1.00"),
    )


@pytest.fixture
def stats_population_pairs_for_every_rdi_individual(
    request: pytest.FixtureRequest, stats_program: Program, stats_rdi: RegistrationDataImport
) -> list[BiographicDedupeSimilarityPair]:
    rdi_individuals = PendingIndividualFactory.create_batch(
        request.param,
        program=stats_program,
        business_area=stats_program.business_area,
        registration_data_import=stats_rdi,
    )
    return [
        BiographicDeduplicationEngineSimilarityPairFactory(
            program=stats_program,
            individual1=rdi_individual,
            individual2=IndividualFactory(program=stats_program, business_area=stats_program.business_area),
        )
        for rdi_individual in rdi_individuals
    ]


def test_store_biographic_deduplication_statistics_without_pairs_counts_every_rdi_individual_as_unique(
    stats_rdi: RegistrationDataImport, stats_rdi_individuals: list[PendingIndividual]
) -> None:
    BiographicDeduplicationEngineService().store_biographic_deduplication_statistics(stats_rdi)

    stats_rdi.refresh_from_db()
    assert (
        stats_rdi.golden_record_duplicates,
        stats_rdi.golden_record_unique,
        stats_rdi.batch_duplicates,
        stats_rdi.batch_unique,
    ) == (0, 2, 0, 2)


def test_store_biographic_deduplication_statistics_marks_rdi_individual_with_population_pair_as_duplicate(
    stats_rdi: RegistrationDataImport,
    stats_rdi_individuals: list[PendingIndividual],
    stats_population_individual: Individual,
    stats_population_pair: BiographicDedupeSimilarityPair,
) -> None:
    BiographicDeduplicationEngineService().store_biographic_deduplication_statistics(stats_rdi)

    individual = PendingIndividual.objects.get(id=stats_rdi_individuals[0].id)
    assert individual.deduplication_golden_record_status == DUPLICATE
    assert individual.deduplication_golden_record_results["duplicates"][0]["hit_id"] == str(
        stats_population_individual.id
    )


def test_store_biographic_deduplication_statistics_keeps_rdi_individual_without_population_pair_unique(
    stats_rdi: RegistrationDataImport,
    stats_rdi_individuals: list[PendingIndividual],
    stats_population_pair: BiographicDedupeSimilarityPair,
) -> None:
    BiographicDeduplicationEngineService().store_biographic_deduplication_statistics(stats_rdi)

    individual = PendingIndividual.objects.get(id=stats_rdi_individuals[1].id)
    assert individual.deduplication_golden_record_status == UNIQUE
    assert individual.deduplication_golden_record_results["duplicates"] == []


def test_store_biographic_deduplication_statistics_marks_population_individual_as_duplicate(
    stats_rdi: RegistrationDataImport,
    stats_population_individual: Individual,
    stats_population_pair: BiographicDedupeSimilarityPair,
) -> None:
    BiographicDeduplicationEngineService().store_biographic_deduplication_statistics(stats_rdi)

    stats_population_individual.refresh_from_db()
    assert stats_population_individual.deduplication_golden_record_status == DUPLICATE


def test_store_biographic_deduplication_statistics_marks_both_sides_of_batch_pair_as_duplicate_in_batch(
    stats_rdi: RegistrationDataImport,
    stats_rdi_individuals: list[PendingIndividual],
    stats_batch_pair: BiographicDedupeSimilarityPair,
) -> None:
    BiographicDeduplicationEngineService().store_biographic_deduplication_statistics(stats_rdi)

    first, second = (PendingIndividual.objects.get(id=individual.id) for individual in stats_rdi_individuals)
    assert (first.deduplication_batch_status, second.deduplication_batch_status) == (
        DUPLICATE_IN_BATCH,
        DUPLICATE_IN_BATCH,
    )
    assert (
        first.deduplication_batch_results["duplicates"][0]["hit_id"],
        second.deduplication_batch_results["duplicates"][0]["hit_id"],
    ) == (str(second.id), str(first.id))


def test_store_biographic_deduplication_statistics_adds_score_summary_to_results(
    stats_rdi: RegistrationDataImport,
    stats_rdi_individuals: list[PendingIndividual],
    stats_population_pair: BiographicDedupeSimilarityPair,
) -> None:
    BiographicDeduplicationEngineService().store_biographic_deduplication_statistics(stats_rdi)

    individual = PendingIndividual.objects.get(id=stats_rdi_individuals[0].id)
    assert individual.deduplication_golden_record_results["score"] == {"max": 12.5, "min": 12.5, "qty": 1}


def test_store_biographic_deduplication_statistics_counts_rdi_individuals_per_status(
    stats_rdi: RegistrationDataImport,
    stats_population_pair: BiographicDedupeSimilarityPair,
    stats_batch_pair: BiographicDedupeSimilarityPair,
) -> None:
    BiographicDeduplicationEngineService().store_biographic_deduplication_statistics(stats_rdi)

    stats_rdi.refresh_from_db()
    assert (
        stats_rdi.golden_record_duplicates,
        stats_rdi.golden_record_unique,
        stats_rdi.batch_duplicates,
        stats_rdi.batch_unique,
    ) == (1, 1, 2, 0)


@pytest.mark.parametrize("stats_population_pairs_for_every_rdi_individual", [1, 3], indirect=True)
def test_store_biographic_deduplication_statistics_query_count_does_not_grow_with_pairs(
    stats_rdi: RegistrationDataImport,
    stats_population_pairs_for_every_rdi_individual: list[BiographicDedupeSimilarityPair],
    django_assert_num_queries,
) -> None:
    with django_assert_num_queries(12):
        BiographicDeduplicationEngineService().store_biographic_deduplication_statistics(stats_rdi)


@pytest.fixture
def tickets_program() -> Program:
    return ProgramFactory()


@pytest.fixture
def tickets_merged_rdi(tickets_program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        program=tickets_program,
        business_area=tickets_program.business_area,
        status=RegistrationDataImport.MERGED,
    )


@pytest.fixture
def tickets_merged_rdi_individual(tickets_program: Program, tickets_merged_rdi: RegistrationDataImport) -> Individual:
    return IndividualFactory(
        program=tickets_program,
        business_area=tickets_program.business_area,
        registration_data_import=tickets_merged_rdi,
    )


@pytest.fixture
def tickets_zero_score_population_pair(
    tickets_program: Program, tickets_merged_rdi_individual: Individual
) -> BiographicDedupeSimilarityPair:
    return BiographicDeduplicationEngineSimilarityPairFactory(
        program=tickets_program,
        individual1=tickets_merged_rdi_individual,
        individual2=IndividualFactory(program=tickets_program, business_area=tickets_program.business_area),
        similarity_score=Decimal(0),
    )


@pytest.fixture
def tickets_pair_outside_rdi(tickets_program: Program) -> BiographicDedupeSimilarityPair:
    return BiographicDeduplicationEngineSimilarityPairFactory(
        program=tickets_program,
        individual1=IndividualFactory(program=tickets_program, business_area=tickets_program.business_area),
        individual2=IndividualFactory(program=tickets_program, business_area=tickets_program.business_area),
    )


def test_create_grievance_tickets_for_biographic_duplicates_creates_ticket_for_zero_score_pair(
    tickets_merged_rdi: RegistrationDataImport,
    tickets_merged_rdi_individual: Individual,
    tickets_zero_score_population_pair: BiographicDedupeSimilarityPair,
) -> None:
    BiographicDeduplicationEngineService().create_grievance_tickets_for_biographic_duplicates(tickets_merged_rdi)

    ticket = GrievanceTicket.objects.get()
    assert ticket.ticket_details.golden_records_individual == tickets_merged_rdi_individual


def test_create_grievance_tickets_for_biographic_duplicates_ignores_pairs_outside_rdi(
    tickets_merged_rdi: RegistrationDataImport,
    tickets_pair_outside_rdi: BiographicDedupeSimilarityPair,
) -> None:
    BiographicDeduplicationEngineService().create_grievance_tickets_for_biographic_duplicates(tickets_merged_rdi)

    assert not GrievanceTicket.objects.exists()
