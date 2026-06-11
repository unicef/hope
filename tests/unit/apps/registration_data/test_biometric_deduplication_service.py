from decimal import Decimal
import os
from unittest import mock
import uuid

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    IndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.household.const import DUPLICATE, NOT_PROCESSED
from hope.apps.registration_data.api.deduplication_engine import (
    SimilarityPair,
)
from hope.apps.registration_data.services.biometric_deduplication import BiometricDeduplicationService
from hope.models import BiometricDedupeSimilarityPair, RegistrationDataImport
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def mock_deduplication_engine_env_vars() -> None:
    with mock.patch.dict(
        os.environ,
        {
            "DEDUPLICATION_ENGINE_API_KEY": "TEST",
            "DEDUPLICATION_ENGINE_API_URL": "TEST",
        },
    ):
        yield


@pytest.fixture
def biometric_deduplication_context() -> dict[str, object]:
    business_area = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
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

    service = BiometricDeduplicationService()
    similarity_pairs = [
        SimilarityPair(score=0.5, first=str(ind2.id), second=str(ind1.id), status_code="200"),
        SimilarityPair(score=0.5, first=str(ind1.id), second=str(ind2.id), status_code="200"),
        SimilarityPair(score=0.7, first=str(ind1.id), second=str(ind3.id), status_code="200"),
        SimilarityPair(score=0.8, first=str(ind3.id), second=str(ind2.id), status_code="200"),
        SimilarityPair(score=0.9, first=str(ind3.id), second=str(ind3.id), status_code="200"),
    ]

    service.store_similarity_pairs(program, similarity_pairs)

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
    service = BiometricDeduplicationService()
    similarity_pairs = [
        SimilarityPair(score=0.0, status_code="404"),
    ]

    service.store_similarity_pairs(program, similarity_pairs)
    assert program.deduplication_engine_similarity_pairs.count() == 0


def test_store_results_1_individual(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    ind1 = IndividualFactory.create_batch(1, program=program, business_area=program.business_area)[0]
    service = BiometricDeduplicationService()
    similarity_pairs = [
        SimilarityPair(score=0.0, first=str(ind1.id), status_code="429"),
    ]

    service.store_similarity_pairs(program, similarity_pairs)

    assert program.deduplication_engine_similarity_pairs.count() == 1
    assert program.deduplication_engine_similarity_pairs.filter(
        individual1=ind1, individual2=None, similarity_score=0.00
    ).exists()


def test_store_results_not_existing_individual(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    ind1 = IndividualFactory.create_batch(1, program=program, business_area=program.business_area)[0]
    service = BiometricDeduplicationService()
    similarity_pairs = [
        SimilarityPair(score=70.0, first=str(ind1.id), second=str(uuid.uuid4()), status_code="429"),
    ]

    service.store_similarity_pairs(program, similarity_pairs)

    assert program.deduplication_engine_similarity_pairs.count() == 0


def test_bulk_add_pairs_country_workspace_id_translates_cw_ids_to_uuids(
    biometric_deduplication_context: dict[str, object],
) -> None:
    program = biometric_deduplication_context["program"]
    ind1 = IndividualFactory(program=program, business_area=program.business_area, country_workspace_id="CW-001")
    ind2 = IndividualFactory(program=program, business_area=program.business_area, country_workspace_id="CW-002")
    similarity_pairs = [
        SimilarityPair(score=0.7, first="CW-001", second="CW-002", status_code="200"),
    ]

    BiometricDedupeSimilarityPair.bulk_add_pairs(program, similarity_pairs, id_field_name="country_workspace_id")

    lower, higher = sorted([str(ind1.id), str(ind2.id)])
    assert program.deduplication_engine_similarity_pairs.count() == 1
    pair = program.deduplication_engine_similarity_pairs.get()
    assert str(pair.individual1_id) == lower
    assert str(pair.individual2_id) == higher
    assert pair.similarity_score == Decimal("70.00")
    assert pair.status_code == "200"


def test_bulk_add_pairs_country_workspace_id_skips_unknown_cw_id(
    biometric_deduplication_context: dict[str, object],
) -> None:
    program = biometric_deduplication_context["program"]
    IndividualFactory(program=program, business_area=program.business_area, country_workspace_id="CW-001")
    similarity_pairs = [
        SimilarityPair(score=0.7, first="CW-001", second="CW-DOES-NOT-EXIST", status_code="200"),
    ]

    BiometricDedupeSimilarityPair.bulk_add_pairs(program, similarity_pairs, id_field_name="country_workspace_id")

    assert program.deduplication_engine_similarity_pairs.count() == 0


def test_bulk_add_pairs_country_workspace_id_skips_self_pair(
    biometric_deduplication_context: dict[str, object],
) -> None:
    program = biometric_deduplication_context["program"]
    IndividualFactory(program=program, business_area=program.business_area, country_workspace_id="CW-001")
    similarity_pairs = [
        SimilarityPair(score=0.95, first="CW-001", second="CW-001", status_code="200"),
    ]

    BiometricDedupeSimilarityPair.bulk_add_pairs(program, similarity_pairs, id_field_name="country_workspace_id")

    assert program.deduplication_engine_similarity_pairs.count() == 0


def test_bulk_add_pairs_empty_input_short_circuits(
    biometric_deduplication_context: dict[str, object],
) -> None:
    program = biometric_deduplication_context["program"]

    BiometricDedupeSimilarityPair.bulk_add_pairs(program, [], id_field_name="country_workspace_id")

    assert program.deduplication_engine_similarity_pairs.count() == 0


def test_update_rdis_deduplication_statistics(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    user = biometric_deduplication_context["user"]
    rdi1 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        status=RegistrationDataImport.IN_REVIEW,
        dedup_engine_batch_duplicates=5,
        dedup_engine_golden_record_duplicates=6,
    )
    rdi2 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        status=RegistrationDataImport.IN_REVIEW,
    )

    individuals = IndividualFactory.create_batch(2, program=program, business_area=program.business_area)
    ind1, ind2 = sorted(individuals, key=lambda x: x.id)

    ind1.registration_data_import = rdi1
    ind2.registration_data_import = rdi2

    ind1.save()
    ind2.save()

    ind1.rdi_merge_status = MergeStatusModel.PENDING
    ind1.save()

    service = BiometricDeduplicationService()
    similarity_pairs = [
        SimilarityPair(score=0.7, first=str(ind1.id), second=str(ind2.id), status_code="200"),
    ]
    service.store_similarity_pairs(program, similarity_pairs)

    service.update_rdis_deduplication_statistics(program, exclude_rdi=rdi2)

    rdi1.refresh_from_db()
    assert rdi1.dedup_engine_batch_duplicates == 5
    assert rdi1.dedup_engine_golden_record_duplicates == 1
    ind1.refresh_from_db()
    assert ind1.biometric_deduplication_golden_record_results == [
        {
            "id": str(ind2.id),
            "unicef_id": str(ind2.unicef_id),
            "full_name": str(ind2.full_name),
            "similarity_score": 70.0,
            "age": ind2.age,
            "location": None,
        },
    ]
    assert ind1.biometric_deduplication_golden_record_status == DUPLICATE
    assert ind1.biometric_deduplication_batch_status == NOT_PROCESSED

    similarity_pairs = [
        SimilarityPair(score=0.0, first=str(ind1.id), second=None, status_code="412"),
    ]
    BiometricDedupeSimilarityPair.objects.all().delete()
    service.store_similarity_pairs(program, similarity_pairs)
    service.update_rdis_deduplication_statistics(program, exclude_rdi=rdi2)

    rdi1.refresh_from_db()
    assert rdi1.dedup_engine_batch_duplicates == 5
    assert rdi1.dedup_engine_golden_record_duplicates == 1
    ind1.refresh_from_db()
    assert ind1.biometric_deduplication_golden_record_results == []
    assert ind1.biometric_deduplication_golden_record_status == DUPLICATE
    assert ind1.biometric_deduplication_batch_status == NOT_PROCESSED
