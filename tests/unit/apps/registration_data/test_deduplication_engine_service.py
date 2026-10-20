import uuid

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    IndividualFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.registration_data.api.deduplication_engine import (
    SimilarityPair,
)
from hope.apps.registration_data.services.deduplication_engine import DeduplicationEngineService
from hope.models import BusinessArea

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


def test_store_results(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    individuals = IndividualFactory.create_batch(3, program=program, business_area=program.business_area)
    ind1, ind2, ind3 = sorted(individuals, key=lambda x: x.id)

    service = DeduplicationEngineService()
    similarity_pairs = [
        SimilarityPair(score=0.5, first=str(ind2.id), second=str(ind1.id), status_code="200"),
        SimilarityPair(score=0.5, first=str(ind1.id), second=str(ind2.id), status_code="200"),
        SimilarityPair(score=0.7, first=str(ind1.id), second=str(ind3.id), status_code="200"),
        SimilarityPair(score=0.8, first=str(ind3.id), second=str(ind2.id), status_code="200"),
        SimilarityPair(score=0.9, first=str(ind3.id), second=str(ind3.id), status_code="200"),
    ]

    service.store_biometric_similarity_pairs(program, similarity_pairs)

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
    service = DeduplicationEngineService()
    similarity_pairs = [
        SimilarityPair(score=0.0, status_code="404"),
    ]

    service.store_biometric_similarity_pairs(program, similarity_pairs)
    assert program.deduplication_engine_similarity_pairs.count() == 0


def test_store_results_1_individual(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    ind1 = IndividualFactory.create_batch(1, program=program, business_area=program.business_area)[0]
    service = DeduplicationEngineService()
    similarity_pairs = [
        SimilarityPair(score=0.0, first=str(ind1.id), status_code="429"),
    ]

    service.store_biometric_similarity_pairs(program, similarity_pairs)

    assert program.deduplication_engine_similarity_pairs.count() == 1
    assert program.deduplication_engine_similarity_pairs.filter(
        individual1=ind1, individual2=None, similarity_score=0.00
    ).exists()


def test_store_results_not_existing_individual(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    ind1 = IndividualFactory.create_batch(1, program=program, business_area=program.business_area)[0]
    service = DeduplicationEngineService()
    similarity_pairs = [
        SimilarityPair(score=70.0, first=str(ind1.id), second=str(uuid.uuid4()), status_code="429"),
    ]

    service.store_biometric_similarity_pairs(program, similarity_pairs)

    assert program.deduplication_engine_similarity_pairs.count() == 0
