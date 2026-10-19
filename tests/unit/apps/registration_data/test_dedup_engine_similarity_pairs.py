from decimal import Decimal

from django.db import IntegrityError
import pytest

from extras.test_utils.factories import (
    BiographicDeduplicationEngineSimilarityPairFactory,
    BiometricDeduplicationEngineSimilarityPairFactory,
    IndividualFactory,
    ProgramFactory,
)
from hope.apps.registration_data.api.deduplication_engine import SimilarityPair
from hope.models import BiographicDedupeSimilarityPair, BiometricDedupeSimilarityPair, Individual, Program

pytestmark = pytest.mark.django_db

PAIR_MODELS = [BiometricDedupeSimilarityPair, BiographicDedupeSimilarityPair]


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
def pair(
    request: pytest.FixtureRequest, program: Program, individuals: list[Individual]
) -> BiometricDedupeSimilarityPair | BiographicDedupeSimilarityPair:
    return request.param(program=program, individual1=individuals[0], individual2=individuals[1])


@pytest.mark.parametrize("pair_model", PAIR_MODELS)
def test_bulk_add_pairs_stores_lower_id_as_individual1_when_hde_sends_reversed_order(
    pair_model: type, program: Program, individuals: list[Individual]
) -> None:
    lower, higher = individuals
    findings = [SimilarityPair(score=0.5, status_code="200", first=str(higher.id), second=str(lower.id))]

    pair_model.bulk_add_pairs(program, findings)

    pair = pair_model.objects.get()
    assert (pair.individual1_id, pair.individual2_id) == (lower.id, higher.id)


def test_biometric_bulk_add_pairs_scales_score_to_percent(program: Program, individuals: list[Individual]) -> None:
    lower, higher = individuals
    findings = [SimilarityPair(score=0.75, status_code="200", first=str(lower.id), second=str(higher.id))]

    BiometricDedupeSimilarityPair.bulk_add_pairs(program, findings)

    assert BiometricDedupeSimilarityPair.objects.get().similarity_score == 75


def test_biographic_bulk_add_pairs_stores_raw_es_score(program: Program, individuals: list[Individual]) -> None:
    lower, higher = individuals
    findings = [SimilarityPair(score=12.34, status_code="200", first=str(lower.id), second=str(higher.id))]

    BiographicDedupeSimilarityPair.bulk_add_pairs(program, findings)

    assert BiographicDedupeSimilarityPair.objects.get().similarity_score == Decimal("12.34")


@pytest.mark.parametrize("pair_model", PAIR_MODELS)
def test_bulk_add_pairs_resolves_country_workspace_ids(
    pair_model: type, program: Program, individuals: list[Individual]
) -> None:
    lower, higher = individuals
    findings = [SimilarityPair(score=0.5, status_code="200", first="cw-b", second="cw-a")]

    pair_model.bulk_add_pairs(program, findings, id_field_name="country_workspace_id")

    pair = pair_model.objects.get()
    assert {pair.individual1_id, pair.individual2_id} == {lower.id, higher.id}


@pytest.mark.parametrize("pair_model", PAIR_MODELS)
def test_bulk_add_pairs_skips_unknown_individual(
    pair_model: type, program: Program, individuals: list[Individual]
) -> None:
    findings = [
        SimilarityPair(
            score=0.5, status_code="200", first=str(individuals[0].id), second="00000000-0000-0000-0000-000000000000"
        )
    ]

    pair_model.bulk_add_pairs(program, findings)

    assert pair_model.objects.count() == 0


@pytest.mark.parametrize("pair_model", PAIR_MODELS)
def test_bulk_add_pairs_skips_removed_individual(
    pair_model: type, program: Program, individuals: list[Individual], removed_individual: Individual
) -> None:
    findings = [
        SimilarityPair(score=0.5, status_code="200", first=str(individuals[0].id), second=str(removed_individual.id))
    ]

    pair_model.bulk_add_pairs(program, findings)

    assert pair_model.objects.count() == 0


@pytest.mark.parametrize("pair_model", PAIR_MODELS)
def test_bulk_add_pairs_skips_withdrawn_individual(
    pair_model: type, program: Program, individuals: list[Individual], withdrawn_individual: Individual
) -> None:
    findings = [
        SimilarityPair(score=0.5, status_code="200", first=str(individuals[0].id), second=str(withdrawn_individual.id))
    ]

    pair_model.bulk_add_pairs(program, findings)

    assert pair_model.objects.count() == 0


@pytest.mark.parametrize("pair_model", PAIR_MODELS)
def test_bulk_add_pairs_skips_self_pair(pair_model: type, program: Program, individuals: list[Individual]) -> None:
    findings = [
        SimilarityPair(score=0.9, status_code="200", first=str(individuals[0].id), second=str(individuals[0].id))
    ]

    pair_model.bulk_add_pairs(program, findings)

    assert pair_model.objects.count() == 0


@pytest.mark.parametrize("pair_model", PAIR_MODELS)
def test_bulk_add_pairs_rerun_of_same_findings_creates_no_duplicates(
    pair_model: type, program: Program, individuals: list[Individual]
) -> None:
    lower, higher = individuals
    findings = [SimilarityPair(score=0.5, status_code="200", first=str(lower.id), second=str(higher.id))]
    pair_model.bulk_add_pairs(program, findings)

    pair_model.bulk_add_pairs(program, findings)

    assert pair_model.objects.count() == 1


def test_biographic_bulk_add_pairs_stores_pair_without_proximity_to_score(
    program: Program, individuals: list[Individual]
) -> None:
    lower, higher = individuals
    findings = [SimilarityPair(score=0.5, status_code="200", first=str(lower.id), second=str(higher.id))]

    BiographicDedupeSimilarityPair.bulk_add_pairs(program, findings)

    assert BiographicDedupeSimilarityPair.objects.get().proximity_to_score is None


def test_biographic_pair_with_individual1_greater_than_individual2_is_rejected(
    program: Program, individuals: list[Individual]
) -> None:
    lower, higher = individuals

    with pytest.raises(IntegrityError):
        BiographicDedupeSimilarityPair.objects.create(
            program=program, individual1=higher, individual2=lower, similarity_score=50, status_code="200"
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
