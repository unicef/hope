from collections.abc import Callable
from decimal import Decimal
import functools
import uuid

from django.db import IntegrityError
import pytest

from extras.test_utils.factories import (
    BiographicDeduplicationEngineSimilarityPairFactory,
    BiometricDeduplicationEngineSimilarityPairFactory,
    IndividualFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.registration_data.api.deduplication_engine import (
    BiographicHDEFinding,
    BiometricHDEFinding,
    HDEFinding,
)
from hope.models import (
    BiographicDedupeSimilarityPair,
    BiometricDedupeSimilarityPair,
    Individual,
    Program,
    RegistrationDataImport,
)

pytestmark = pytest.mark.django_db

PAIR_MODELS = [BiometricDedupeSimilarityPair, BiographicDedupeSimilarityPair]
FINDING_CLASSES = {
    BiometricDedupeSimilarityPair: functools.partial(BiometricHDEFinding, status_code="200"),
    BiographicDedupeSimilarityPair: functools.partial(BiographicHDEFinding, proximity_to_score=0.0),
}


@pytest.fixture
def program() -> Program:
    return ProgramFactory()


@pytest.fixture
def individuals(program: Program) -> list[Individual]:
    created = [
        IndividualFactory(program=program, business_area=program.business_area, country_workspace_id="cw-a"),
        IndividualFactory(program=program, business_area=program.business_area, country_workspace_id="cw-b"),
    ]
    return sorted(created, key=lambda individual: str(individual.id))


@pytest.fixture
def removed_individual(program: Program) -> Individual:
    return IndividualFactory(program=program, business_area=program.business_area, is_removed=True)


@pytest.fixture
def withdrawn_individual(program: Program) -> Individual:
    return IndividualFactory(program=program, business_area=program.business_area, withdrawn=True)


@pytest.fixture
def live_individual_with_dead_twin(request: pytest.FixtureRequest, program: Program) -> Individual:
    live = IndividualFactory(
        id=uuid.UUID("00000000-0000-4000-8000-000000000001"),
        program=program,
        business_area=program.business_area,
        country_workspace_id="cw-twin",
    )
    IndividualFactory(
        id=uuid.UUID("ffffffff-ffff-4fff-8fff-ffffffffffff"),
        program=program,
        business_area=program.business_area,
        country_workspace_id="cw-twin",
        **{request.param: True},
    )
    return live


@pytest.fixture
def biometric_pair(individuals: list[Individual], program: Program) -> BiometricDedupeSimilarityPair:
    return BiometricDeduplicationEngineSimilarityPairFactory(
        program=program, individual1=individuals[0], individual2=individuals[1]
    )


@pytest.fixture
def biographic_pair(individuals: list[Individual], program: Program) -> BiographicDedupeSimilarityPair:
    return BiographicDeduplicationEngineSimilarityPairFactory(
        program=program, individual1=individuals[0], individual2=individuals[1]
    )


@pytest.fixture
def rdi(program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        program=program, business_area=program.business_area, status=RegistrationDataImport.IN_REVIEW
    )


@pytest.fixture
def rdi_individuals(program: Program, rdi: RegistrationDataImport) -> list[Individual]:
    created = PendingIndividualFactory.create_batch(
        2, program=program, business_area=program.business_area, registration_data_import=rdi
    )
    return sorted(created, key=lambda individual: str(individual.id))


@pytest.fixture
def batch_pairs_in_both_tables(
    program: Program, rdi_individuals: list[Individual]
) -> dict[type, BiometricDedupeSimilarityPair | BiographicDedupeSimilarityPair]:
    individual1, individual2 = rdi_individuals
    return {
        BiometricDedupeSimilarityPair: BiometricDeduplicationEngineSimilarityPairFactory(
            program=program, individual1=individual1, individual2=individual2
        ),
        BiographicDedupeSimilarityPair: BiographicDeduplicationEngineSimilarityPairFactory(
            program=program, individual1=individual1, individual2=individual2
        ),
    }


@pytest.fixture
def population_pairs_in_both_tables(
    program: Program, rdi_individuals: list[Individual]
) -> dict[type, BiometricDedupeSimilarityPair | BiographicDedupeSimilarityPair]:
    population_individual = IndividualFactory(program=program, business_area=program.business_area)
    individual1, individual2 = sorted([rdi_individuals[0], population_individual], key=lambda ind: str(ind.id))
    return {
        BiometricDedupeSimilarityPair: BiometricDeduplicationEngineSimilarityPairFactory(
            program=program, individual1=individual1, individual2=individual2
        ),
        BiographicDedupeSimilarityPair: BiographicDeduplicationEngineSimilarityPairFactory(
            program=program, individual1=individual1, individual2=individual2
        ),
    }


@pytest.fixture
def biographic_zero_score_batch_pair(
    program: Program, rdi_individuals: list[Individual]
) -> BiographicDedupeSimilarityPair:
    individual1, individual2 = rdi_individuals
    return BiographicDeduplicationEngineSimilarityPairFactory(
        program=program, individual1=individual1, individual2=individual2, similarity_score=Decimal(0)
    )


@pytest.fixture
def biographic_zero_score_population_pair(
    program: Program, rdi_individuals: list[Individual]
) -> BiographicDedupeSimilarityPair:
    population_individual = IndividualFactory(program=program, business_area=program.business_area)
    individual1, individual2 = sorted([rdi_individuals[0], population_individual], key=lambda ind: str(ind.id))
    return BiographicDeduplicationEngineSimilarityPairFactory(
        program=program, individual1=individual1, individual2=individual2, similarity_score=Decimal(0)
    )


@pytest.fixture
def pair(
    request: pytest.FixtureRequest, program: Program, individuals: list[Individual]
) -> BiometricDedupeSimilarityPair | BiographicDedupeSimilarityPair:
    return request.param(program=program, individual1=individuals[0], individual2=individuals[1])


@pytest.fixture
def finding_class(pair_model: type) -> Callable[..., HDEFinding]:
    return FINDING_CLASSES[pair_model]


@pytest.fixture
def reversed_order_findings(finding_class: Callable[..., HDEFinding], individuals: list[Individual]) -> list:
    lower, higher = individuals
    return [finding_class(score=0.5, first=str(higher.id), second=str(lower.id))]


@pytest.fixture
def ordered_findings(finding_class: Callable[..., HDEFinding], individuals: list[Individual]) -> list:
    lower, higher = individuals
    return [finding_class(score=0.5, first=str(lower.id), second=str(higher.id))]


@pytest.fixture
def country_workspace_id_findings(finding_class: Callable[..., HDEFinding], individuals: list[Individual]) -> list:
    lower, higher = individuals
    return [finding_class(score=0.5, first=higher.country_workspace_id, second=lower.country_workspace_id)]


@pytest.fixture
def dead_twin_findings(
    finding_class: Callable[..., HDEFinding],
    individuals: list[Individual],
    live_individual_with_dead_twin: Individual,
) -> list:
    return [
        finding_class(
            score=0.5,
            first=live_individual_with_dead_twin.country_workspace_id,
            second=individuals[0].country_workspace_id,
        )
    ]


@pytest.fixture
def unknown_individual_findings(finding_class: Callable[..., HDEFinding], individuals: list[Individual]) -> list:
    return [finding_class(score=0.5, first=str(individuals[0].id), second="00000000-0000-0000-0000-000000000000")]


@pytest.fixture
def removed_individual_findings(
    finding_class: Callable[..., HDEFinding], individuals: list[Individual], removed_individual: Individual
) -> list:
    return [finding_class(score=0.5, first=str(individuals[0].id), second=str(removed_individual.id))]


@pytest.fixture
def withdrawn_individual_findings(
    finding_class: Callable[..., HDEFinding], individuals: list[Individual], withdrawn_individual: Individual
) -> list:
    return [finding_class(score=0.5, first=str(individuals[0].id), second=str(withdrawn_individual.id))]


@pytest.fixture
def self_pair_findings(finding_class: Callable[..., HDEFinding], individuals: list[Individual]) -> list:
    return [finding_class(score=0.9, first=str(individuals[0].id), second=str(individuals[0].id))]


@pytest.fixture
def biometric_findings_with_fractional_score(individuals: list[Individual]) -> list[BiometricHDEFinding]:
    lower, higher = individuals
    return [BiometricHDEFinding(score=0.75, status_code="200", first=str(lower.id), second=str(higher.id))]


@pytest.fixture
def biographic_findings_with_raw_es_score(individuals: list[Individual]) -> list[BiographicHDEFinding]:
    lower, higher = individuals
    return [BiographicHDEFinding(score=12.34, first=str(lower.id), second=str(higher.id), proximity_to_score=-1.25)]


@pytest.mark.parametrize("pair_model", PAIR_MODELS)
def test_bulk_add_pairs_stores_lower_id_as_individual1_when_hde_sends_reversed_order(
    pair_model: type, program: Program, individuals: list[Individual], reversed_order_findings: list
) -> None:
    lower, higher = individuals

    pair_model.bulk_add_pairs(program, reversed_order_findings)

    pair = pair_model.objects.get()
    assert (pair.individual1_id, pair.individual2_id) == (lower.id, higher.id)


def test_biometric_bulk_add_pairs_scales_score_to_percent(
    program: Program, biometric_findings_with_fractional_score: list[BiometricHDEFinding]
) -> None:
    BiometricDedupeSimilarityPair.bulk_add_pairs(program, biometric_findings_with_fractional_score)

    assert BiometricDedupeSimilarityPair.objects.get().similarity_score == 75


def test_biographic_bulk_add_pairs_stores_raw_es_score_and_proximity_to_score(
    program: Program, biographic_findings_with_raw_es_score: list[BiographicHDEFinding]
) -> None:
    BiographicDedupeSimilarityPair.bulk_add_pairs(program, biographic_findings_with_raw_es_score)

    pair = BiographicDedupeSimilarityPair.objects.get()
    assert (pair.similarity_score, pair.proximity_to_score) == (Decimal("12.34"), Decimal("-1.25"))


def test_biometric_bulk_add_pairs_rejects_biographic_findings(
    program: Program, biographic_findings_with_raw_es_score: list[BiographicHDEFinding]
) -> None:
    with pytest.raises(TypeError, match="Expected BiometricHDEFinding, got BiographicHDEFinding"):
        BiometricDedupeSimilarityPair.bulk_add_pairs(program, biographic_findings_with_raw_es_score)


def test_biographic_bulk_add_pairs_rejects_biometric_findings(
    program: Program, biometric_findings_with_fractional_score: list[BiometricHDEFinding]
) -> None:
    with pytest.raises(TypeError, match="Expected BiographicHDEFinding, got BiometricHDEFinding"):
        BiographicDedupeSimilarityPair.bulk_add_pairs(program, biometric_findings_with_fractional_score)


@pytest.mark.parametrize("pair_model", PAIR_MODELS)
def test_bulk_add_pairs_resolves_country_workspace_ids(
    pair_model: type, program: Program, individuals: list[Individual], country_workspace_id_findings: list
) -> None:
    lower, higher = individuals

    pair_model.bulk_add_pairs(program, country_workspace_id_findings, id_field_name="country_workspace_id")

    pair = pair_model.objects.get()
    assert {pair.individual1_id, pair.individual2_id} == {lower.id, higher.id}


@pytest.mark.parametrize("live_individual_with_dead_twin", ["withdrawn", "is_removed"], indirect=True)
@pytest.mark.parametrize("pair_model", PAIR_MODELS)
def test_bulk_add_pairs_binds_live_individual_when_country_workspace_id_has_dead_twin(
    pair_model: type,
    program: Program,
    individuals: list[Individual],
    live_individual_with_dead_twin: Individual,
    dead_twin_findings: list,
) -> None:
    pair_model.bulk_add_pairs(program, dead_twin_findings, id_field_name="country_workspace_id")

    pair = pair_model.objects.get()
    assert {pair.individual1_id, pair.individual2_id} == {live_individual_with_dead_twin.id, individuals[0].id}


@pytest.mark.parametrize("pair_model", PAIR_MODELS)
def test_bulk_add_pairs_with_empty_findings_stores_nothing(pair_model: type, program: Program) -> None:
    pair_model.bulk_add_pairs(program, [])

    assert pair_model.objects.count() == 0


@pytest.mark.parametrize("pair_model", PAIR_MODELS)
@pytest.mark.parametrize(
    "findings_fixture",
    [
        "unknown_individual_findings",
        "removed_individual_findings",
        "withdrawn_individual_findings",
        "self_pair_findings",
    ],
)
def test_bulk_add_pairs_skips_finding_without_two_distinct_live_individuals(
    pair_model: type, program: Program, findings_fixture: str, request: pytest.FixtureRequest
) -> None:
    findings = request.getfixturevalue(findings_fixture)

    pair_model.bulk_add_pairs(program, findings)

    assert pair_model.objects.count() == 0


@pytest.mark.parametrize("pair_model", PAIR_MODELS)
def test_bulk_add_pairs_rerun_of_same_findings_creates_no_duplicates(
    pair_model: type, program: Program, ordered_findings: list
) -> None:
    pair_model.bulk_add_pairs(program, ordered_findings)

    pair_model.bulk_add_pairs(program, ordered_findings)

    assert pair_model.objects.count() == 1


def test_biographic_pair_with_individual1_greater_than_individual2_is_rejected(
    program: Program, individuals: list[Individual]
) -> None:
    lower, higher = individuals

    with pytest.raises(IntegrityError):
        BiographicDedupeSimilarityPair.objects.create(
            program=program, individual1=higher, individual2=lower, similarity_score=50, proximity_to_score=5
        )


@pytest.mark.parametrize(
    ("pair", "pair_type"),
    [
        (BiometricDeduplicationEngineSimilarityPairFactory, "biometric dedupe similarity pair"),
        (BiographicDeduplicationEngineSimilarityPairFactory, "biographic dedupe similarity pair"),
    ],
    indirect=["pair"],
)
def test_pair_str_shows_pair_type_program_and_both_individuals(
    pair: BiometricDedupeSimilarityPair | BiographicDedupeSimilarityPair,
    pair_type: str,
    program: Program,
    individuals: list[Individual],
) -> None:
    lower, higher = individuals

    assert str(pair) == f"[{pair_type}] {program} - {lower} / {higher}"


def test_same_individuals_pair_exists_in_biometric_and_biographic_tables(
    biometric_pair: BiometricDedupeSimilarityPair, biographic_pair: BiographicDedupeSimilarityPair
) -> None:
    assert (biometric_pair.individual1_id, biometric_pair.individual2_id) == (
        biographic_pair.individual1_id,
        biographic_pair.individual2_id,
    )


@pytest.mark.parametrize("pair_model", PAIR_MODELS)
def test_for_rdi_against_batch_returns_only_own_model_pairs_when_same_individuals_in_both_tables(
    pair_model: type,
    rdi: RegistrationDataImport,
    batch_pairs_in_both_tables: dict[type, BiometricDedupeSimilarityPair | BiographicDedupeSimilarityPair],
) -> None:
    result = pair_model.objects.for_rdi_against_batch(rdi)

    assert list(result) == [batch_pairs_in_both_tables[pair_model]]


@pytest.mark.parametrize("pair_model", PAIR_MODELS)
def test_for_rdi_against_population_returns_only_own_model_pairs_when_same_individuals_in_both_tables(
    pair_model: type,
    rdi: RegistrationDataImport,
    population_pairs_in_both_tables: dict[type, BiometricDedupeSimilarityPair | BiographicDedupeSimilarityPair],
) -> None:
    result = pair_model.objects.for_rdi_against_population(rdi)

    assert list(result) == [population_pairs_in_both_tables[pair_model]]


def test_biographic_for_rdi_against_batch_keeps_zero_score_pair(
    rdi: RegistrationDataImport, biographic_zero_score_batch_pair: BiographicDedupeSimilarityPair
) -> None:
    result = BiographicDedupeSimilarityPair.objects.for_rdi_against_batch(rdi)

    assert list(result) == [biographic_zero_score_batch_pair]


def test_biographic_for_rdi_against_population_keeps_zero_score_pair(
    rdi: RegistrationDataImport, biographic_zero_score_population_pair: BiographicDedupeSimilarityPair
) -> None:
    result = BiographicDedupeSimilarityPair.objects.for_rdi_against_population(rdi)

    assert list(result) == [biographic_zero_score_population_pair]
