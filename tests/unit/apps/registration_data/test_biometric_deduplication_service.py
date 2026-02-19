from decimal import Decimal
import os
from unittest import mock
from unittest.mock import patch
import uuid

from django.conf import settings
from flags.models import FlagState
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    IndividualFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.household.const import DUPLICATE, DUPLICATE_IN_BATCH, NOT_PROCESSED, UNIQUE
from hope.apps.registration_data.api.deduplication_engine import (
    DeduplicationEngineAPI,
    DeduplicationImage,
    DeduplicationSet,
    DeduplicationSetData,
    IgnoredFilenamesPair,
    SimilarityPair,
)
from hope.apps.registration_data.services.biometric_deduplication import BiometricDeduplicationService
from hope.models import DeduplicationEngineSimilarityPair, RegistrationDataImport
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
    FlagState.objects.get_or_create(
        name="BIOMETRIC_DEDUPLICATION_REPORT_INDIVIDUALS_STATUS",
        condition="boolean",
        value="True",
        required=False,
    )
    return {
        "business_area": business_area,
        "user": user,
        "program": program,
    }


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.create_deduplication_set")
def test_create_deduplication_set(
    mock_create_deduplication_set: mock.Mock, biometric_deduplication_context: dict[str, object]
) -> None:
    program = biometric_deduplication_context["program"]
    service = BiometricDeduplicationService()

    service.create_deduplication_set(program)

    program.refresh_from_db()
    notification_url = (
        f"https://{settings.DOMAIN_NAME}/api/rest/business-areas/"
        f"{program.business_area.slug}/programs/{program.slug}/"
        "registration-data-imports/webhookdeduplication/"
    )
    mock_create_deduplication_set.assert_called_once_with(
        DeduplicationSet(
            reference_pk=str(program.slug),
            notification_url=notification_url,
        )
    )


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_duplicates")
def test_get_deduplication_set_results(
    mock_get_duplicates: mock.Mock, biometric_deduplication_context: dict[str, object]
) -> None:
    program = biometric_deduplication_context["program"]
    service = BiometricDeduplicationService()
    service.get_deduplication_set_results(program, ["1", "2"])
    mock_get_duplicates.assert_called_once_with(program, ["1", "2"])


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.get_deduplication_set")
def test_get_deduplication_set(
    mock_get_deduplication_set: mock.Mock, biometric_deduplication_context: dict[str, object]
) -> None:
    program = biometric_deduplication_context["program"]
    service = BiometricDeduplicationService()

    mock_get_deduplication_set.return_value = {"state": "Ready"}

    data = service.get_deduplication_set(program)
    assert data == DeduplicationSetData(state="Ready", error="")

    mock_get_deduplication_set.assert_called_once_with(program)


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.bulk_upload_images")
def test_upload_individuals_success(
    mock_bulk_upload_images: mock.Mock, biometric_deduplication_context: dict[str, object]
) -> None:
    program = biometric_deduplication_context["program"]
    user = biometric_deduplication_context["user"]
    rdi = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING,
    )
    individual = IndividualFactory(
        registration_data_import=rdi,
        program=program,
        business_area=program.business_area,
        photo="some_photo.jpg",
    )

    service = BiometricDeduplicationService()
    service.upload_individuals(program, rdi)
    mock_bulk_upload_images.assert_called_once_with(
        program,
        [DeduplicationImage(reference_pk=str(individual.id), filename="some_photo.jpg")],
    )

    rdi.refresh_from_db()
    assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_UPLOADED

    rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_ERROR
    rdi.save()
    service.upload_individuals(program, rdi)
    rdi.refresh_from_db()
    assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_UPLOADED


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.bulk_upload_images")
def test_upload_individuals_failure(
    mock_bulk_upload_images: mock.Mock, biometric_deduplication_context: dict[str, object]
) -> None:
    program = biometric_deduplication_context["program"]
    user = biometric_deduplication_context["user"]
    mock_bulk_upload_images.side_effect = DeduplicationEngineAPI.DeduplicationEngineAPIError
    rdi = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING,
    )
    IndividualFactory(
        registration_data_import=rdi,
        program=program,
        business_area=program.business_area,
        photo="some_photo.jpg",
    )

    service = BiometricDeduplicationService()
    service.upload_individuals(program, rdi)

    rdi.refresh_from_db()
    assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_UPLOAD_ERROR


def test_upload_individuals_no_individuals(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    user = biometric_deduplication_context["user"]
    rdi = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING,
    )
    IndividualFactory(
        registration_data_import=rdi,
        program=program,
        business_area=program.business_area,
        photo="some_photo.jpg",
        withdrawn=True,
    )

    service = BiometricDeduplicationService()
    service.upload_individuals(program, rdi)

    rdi.refresh_from_db()
    assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_FINISHED


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.process_deduplication")
def test_process_deduplication_set(
    mock_process_deduplication: mock.Mock, biometric_deduplication_context: dict[str, object]
) -> None:
    program = biometric_deduplication_context["program"]
    user = biometric_deduplication_context["user"]
    rdi = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING,
    )
    service = BiometricDeduplicationService()

    mock_process_deduplication.return_value = ({}, 200)
    service.process_deduplication_set(program, RegistrationDataImport.objects.all())
    mock_process_deduplication.assert_called_once_with(program)
    rdi.refresh_from_db()
    assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS

    mock_process_deduplication.return_value = ({}, 400)
    service.process_deduplication_set(program, RegistrationDataImport.objects.all())
    rdi.refresh_from_db()
    assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_ERROR

    rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS
    rdi.save()
    mock_process_deduplication.side_effect = DeduplicationEngineAPI.DeduplicationEngineAPIError
    service.process_deduplication_set(program, RegistrationDataImport.objects.all())
    rdi.refresh_from_db()
    assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_ERROR


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.delete_deduplication_set")
def test_delete_deduplication_set(
    mock_delete_deduplication_set: mock.Mock, biometric_deduplication_context: dict[str, object]
) -> None:
    program = biometric_deduplication_context["program"]
    service = BiometricDeduplicationService()
    service.delete_deduplication_set(program)
    mock_delete_deduplication_set.assert_called_once_with(program.slug)


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.bulk_upload_images")
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.process_deduplication")
def test_upload_and_process_deduplication_set(
    mock_process_deduplication: mock.Mock,
    mock_bulk_upload_images: mock.Mock,
    biometric_deduplication_context: dict[str, object],
) -> None:
    program = biometric_deduplication_context["program"]
    user = biometric_deduplication_context["user"]
    mock_bulk_upload_images.return_value = ({}, 200)
    mock_process_deduplication.return_value = ({}, 200)
    service = BiometricDeduplicationService()

    service.upload_and_process_deduplication_set(program)

    rdi_1 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING,
        status=RegistrationDataImport.IN_REVIEW,
    )
    rdi_2 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING,
        status=RegistrationDataImport.IN_REVIEW,
    )
    IndividualFactory(
        registration_data_import=rdi_1,
        program=program,
        business_area=program.business_area,
        photo="some_photo1.jpg",
    )
    PendingIndividualFactory(
        registration_data_import=rdi_2,
        program=program,
        business_area=program.business_area,
        photo="some_photo2.jpg",
    )

    service.create_deduplication_set = mock.MagicMock()

    mock_bulk_upload_images.side_effect = DeduplicationEngineAPI.DeduplicationEngineAPIError
    service.upload_and_process_deduplication_set(program)
    assert mock_bulk_upload_images.call_count == 2
    rdi_1.refresh_from_db()
    rdi_2.refresh_from_db()
    assert rdi_1.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_UPLOAD_ERROR
    assert rdi_2.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_UPLOAD_ERROR

    mock_bulk_upload_images.reset_mock()
    mock_process_deduplication.reset_mock()
    mock_bulk_upload_images.side_effect = None

    rdi_1.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_PENDING
    rdi_1.save()
    rdi_2.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_PENDING
    rdi_2.save()
    service.upload_and_process_deduplication_set(program)

    assert mock_bulk_upload_images.call_count == 2
    assert mock_process_deduplication.call_count == 1
    rdi_1.refresh_from_db()
    rdi_2.refresh_from_db()
    assert rdi_1.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS
    assert rdi_2.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS


def test_store_results(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    individuals = IndividualFactory.create_batch(3, program=program, business_area=program.business_area)
    ind1, ind2, ind3 = sorted(individuals, key=lambda x: x.id)

    service = BiometricDeduplicationService()
    similarity_pairs = [
        SimilarityPair(score=0.5, first=ind2.id, second=ind1.id, status_code="200"),
        SimilarityPair(score=0.5, first=ind1.id, second=ind2.id, status_code="200"),
        SimilarityPair(score=0.7, first=ind1.id, second=ind3.id, status_code="200"),
        SimilarityPair(score=0.8, first=ind3.id, second=ind2.id, status_code="200"),
        SimilarityPair(score=0.9, first=ind3.id, second=ind3.id, status_code="200"),
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

    service.store_similarity_pairs(program.slug, similarity_pairs)
    assert program.deduplication_engine_similarity_pairs.count() == 0


def test_store_results_1_individual(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    ind1 = IndividualFactory.create_batch(1, program=program, business_area=program.business_area)[0]
    service = BiometricDeduplicationService()
    similarity_pairs = [
        SimilarityPair(score=0.0, first=ind1.id, status_code="429"),
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
        SimilarityPair(score=70.0, first=ind1.id, second=str(uuid.uuid4()), status_code="429"),
    ]

    service.store_similarity_pairs(program, similarity_pairs)

    assert program.deduplication_engine_similarity_pairs.count() == 0


def test_mark_rdis_as(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    user = biometric_deduplication_context["user"]
    service = BiometricDeduplicationService()
    rdi = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS,
    )

    service.mark_rdis_as_deduplicated(program)
    rdi.refresh_from_db()
    assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_FINISHED

    rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS
    rdi.save()
    service.mark_rdis_as_error(program)
    rdi.refresh_from_db()
    assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_ERROR


def test_get_duplicates_for_rdi_against_population(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    user = biometric_deduplication_context["user"]
    rdi1 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
    )
    rdi2 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
    )
    rdi3 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
    )
    individuals = IndividualFactory.create_batch(6, program=program, business_area=program.business_area)
    ind1, ind2, ind3, ind4, ind5, ind6 = sorted(individuals, key=lambda x: x.id)

    ind1.registration_data_import = rdi1
    ind2.registration_data_import = rdi1
    ind3.registration_data_import = rdi2
    ind4.registration_data_import = rdi2
    ind5.registration_data_import = rdi3
    ind6.registration_data_import = rdi3
    ind1.save()
    ind2.save()
    ind3.save()
    ind4.save()
    ind5.save()
    ind6.save()

    for ind in [ind1, ind2, ind3, ind4]:
        ind.rdi_merge_status = MergeStatusModel.PENDING
        ind.save()

    service = BiometricDeduplicationService()
    similarity_pairs = [
        SimilarityPair(score=0.9, first=ind1.id, second=ind2.id, status_code="200"),
        SimilarityPair(score=0.7, first=ind1.id, second=ind3.id, status_code="200"),
        SimilarityPair(score=0.8, first=ind1.id, second=ind5.id, status_code="200"),
        SimilarityPair(score=0.9, first=ind6.id, second=ind2.id, status_code="200"),
        SimilarityPair(score=0.9, first=ind3.id, second=ind4.id, status_code="200"),
        SimilarityPair(score=0.7, first=ind4.id, second=ind5.id, status_code="200"),
        SimilarityPair(score=0.8, first=ind5.id, second=ind6.id, status_code="200"),
    ]
    service.store_similarity_pairs(program, similarity_pairs)

    duplicates = service.get_duplicates_for_rdi_against_population(rdi1, rdi_merged=False)
    assert len(duplicates) == 2
    assert list(duplicates.order_by("similarity_score").values("individual1", "individual2", "similarity_score")) == [
        {
            "individual1": ind1.id,
            "individual2": ind5.id,
            "similarity_score": Decimal("80.00"),
        },
        {
            "individual1": ind2.id,
            "individual2": ind6.id,
            "similarity_score": Decimal("90.00"),
        },
    ]


def test_get_duplicates_for_merged_rdi_against_population(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    user = biometric_deduplication_context["user"]
    rdi1 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
    )
    rdi2 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
    )
    rdi3 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
    )
    individuals = IndividualFactory.create_batch(6, program=program, business_area=program.business_area)
    ind1, ind2, ind3, ind4, ind5, ind6 = sorted(individuals, key=lambda x: x.id)

    ind1.registration_data_import = rdi1
    ind2.registration_data_import = rdi1
    ind3.registration_data_import = rdi2
    ind4.registration_data_import = rdi2
    ind5.registration_data_import = rdi3
    ind6.registration_data_import = rdi3
    ind1.save()
    ind2.save()
    ind3.save()
    ind4.save()
    ind5.save()
    ind6.save()

    service = BiometricDeduplicationService()
    similarity_pairs = [
        SimilarityPair(score=0.7, first=ind1.id, second=ind2.id, status_code="200"),
        SimilarityPair(score=0.7, first=ind1.id, second=ind3.id, status_code="200"),
        SimilarityPair(score=0.8, first=ind1.id, second=ind5.id, status_code="200"),
        SimilarityPair(score=0.9, first=ind2.id, second=ind6.id, status_code="200"),
        SimilarityPair(score=0.9, first=ind3.id, second=ind4.id, status_code="200"),
        SimilarityPair(score=0.7, first=ind4.id, second=ind5.id, status_code="200"),
        SimilarityPair(score=0.8, first=ind5.id, second=ind6.id, status_code="200"),
    ]
    service.store_similarity_pairs(program, similarity_pairs)

    duplicates = service.get_duplicates_for_rdi_against_population(rdi2, rdi_merged=True)

    assert len(duplicates) == 3
    assert list(duplicates.order_by("similarity_score").values("individual1", "individual2", "similarity_score")) == [
        {
            "individual1": ind1.id,
            "individual2": ind3.id,
            "similarity_score": Decimal("70.00"),
        },
        {
            "individual1": ind4.id,
            "individual2": ind5.id,
            "similarity_score": Decimal("70.00"),
        },
        {
            "individual1": ind3.id,
            "individual2": ind4.id,
            "similarity_score": Decimal("90.00"),
        },
    ]


def test_get_duplicates_for_rdi_against_batch(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    user = biometric_deduplication_context["user"]
    program.business_area.biometric_deduplication_threshold = 0.6
    program.business_area.save()
    program.save()

    rdi1 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
    )
    rdi2 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
    )
    rdi3 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
    )
    individuals = IndividualFactory.create_batch(6, program=program, business_area=program.business_area)
    ind1, ind2, ind3, ind4, ind5, ind6 = sorted(individuals, key=lambda x: x.id)

    ind1.registration_data_import = rdi1
    ind2.registration_data_import = rdi1
    ind3.registration_data_import = rdi2
    ind4.registration_data_import = rdi2
    ind5.registration_data_import = rdi3
    ind6.registration_data_import = rdi3
    ind1.save()
    ind2.save()
    ind3.save()
    ind4.save()
    ind5.save()
    ind6.save()

    for ind in [ind1, ind2, ind3, ind4]:
        ind.rdi_merge_status = MergeStatusModel.PENDING
        ind.save()

    service = BiometricDeduplicationService()
    similarity_pairs = [
        SimilarityPair(score=0.9, first=ind1.id, second=ind2.id, status_code="200"),
        SimilarityPair(score=0.7, first=ind1.id, second=ind3.id, status_code="200"),
        SimilarityPair(score=0.8, first=ind1.id, second=ind5.id, status_code="200"),
        SimilarityPair(score=0.9, first=ind2.id, second=ind6.id, status_code="200"),
        SimilarityPair(score=0.9, first=ind3.id, second=ind4.id, status_code="200"),
        SimilarityPair(score=0.7, first=ind4.id, second=ind5.id, status_code="200"),
        SimilarityPair(score=0.8, first=ind5.id, second=ind6.id, status_code="200"),
    ]
    service.store_similarity_pairs(program, similarity_pairs)

    duplicates = service.get_duplicates_for_rdi_against_batch(rdi1)

    assert len(duplicates) == 1
    assert list(duplicates.order_by("similarity_score").values("individual1", "individual2", "similarity_score")) == [
        {
            "individual1": ind1.id,
            "individual2": ind2.id,
            "similarity_score": Decimal("90.00"),
        },
    ]


@patch(
    "hope.apps.grievance.services.needs_adjudication_ticket_services.create_needs_adjudication_tickets_for_biometrics"
)
def test_create_grievance_tickets_for_duplicates(
    create_needs_adjudication_tickets_for_biometrics_mock: mock.Mock,
    biometric_deduplication_context: dict[str, object],
) -> None:
    program = biometric_deduplication_context["program"]
    user = biometric_deduplication_context["user"]
    rdi1 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
    )

    service = BiometricDeduplicationService()
    service.get_duplicates_for_rdi_against_population = mock.MagicMock()
    service.get_duplicates_for_rdi_against_population.return_value = []

    service.create_grievance_tickets_for_duplicates(rdi1)
    create_needs_adjudication_tickets_for_biometrics_mock.assert_called_once_with([], rdi1)


def test_fetch_biometric_deduplication_results_and_process_success(
    biometric_deduplication_context: dict[str, object],
) -> None:
    program = biometric_deduplication_context["program"]
    service = BiometricDeduplicationService()

    service.get_deduplication_set = mock.Mock(return_value=DeduplicationSetData(state="Ready"))

    results_data = [
        {
            "first": {"reference_pk": "1"},
            "second": {"reference_pk": "2"},
            "score": 0.9,
            "status_code": "200",
        },
        {
            "first": {"reference_pk": "3"},
            "second": {"reference_pk": "4"},
            "score": 0.8,
            "status_code": "200",
        },
    ]
    service.get_deduplication_set_results = mock.Mock(return_value=results_data)
    service.store_similarity_pairs = mock.Mock()
    service.store_rdis_deduplication_statistics = mock.Mock()
    service.mark_rdis_as_deduplicated = mock.Mock()

    service.fetch_biometric_deduplication_results_and_process(program)

    service.get_deduplication_set.assert_called_once_with(program.slug)
    service.get_deduplication_set_results.assert_called_once_with(program.slug, [])
    service.store_similarity_pairs.assert_called_once_with(
        program,
        [
            SimilarityPair(
                score=item["score"],
                status_code=item["status_code"],
                first=item["first"]["reference_pk"],
                second=item["second"]["reference_pk"],
            )
            for item in results_data
        ],
    )


def test_fetch_biometric_deduplication_results_and_process_error(
    biometric_deduplication_context: dict[str, object],
) -> None:
    program = biometric_deduplication_context["program"]
    service = BiometricDeduplicationService()

    service.get_deduplication_set = mock.Mock(return_value=DeduplicationSetData(state="Ready"))
    service.mark_rdis_as_error = mock.Mock()
    service.get_deduplication_set_results = mock.Mock(side_effect=Exception)

    service.fetch_biometric_deduplication_results_and_process(program)

    service.get_deduplication_set.assert_called_once_with(program.slug)
    service.mark_rdis_as_error.assert_called_once_with(program)


def test_fetch_biometric_deduplication_results_and_process_dedup_engine_error(
    biometric_deduplication_context: dict[str, object],
) -> None:
    program = biometric_deduplication_context["program"]
    service = BiometricDeduplicationService()

    service.get_deduplication_set = mock.Mock(return_value=DeduplicationSetData(state="Failed", error="Dedup Error"))
    service.mark_rdis_as_error = mock.Mock()

    service.fetch_biometric_deduplication_results_and_process(program)

    service.get_deduplication_set.assert_called_once_with(program.slug)
    service.mark_rdis_as_error.assert_called_once_with(program)


def test_store_rdis_deduplication_statistics(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    user = biometric_deduplication_context["user"]
    rdi1 = RegistrationDataImportFactory(
        status=RegistrationDataImport.IN_REVIEW,
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS,
    )
    rdi2 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
    )

    individuals = IndividualFactory.create_batch(5, program=program, business_area=program.business_area)
    ind1, ind2, ind3, ind4, ind5 = sorted(individuals, key=lambda x: x.id)

    ind1.registration_data_import = rdi1
    ind2.registration_data_import = rdi1
    ind3.registration_data_import = rdi1
    ind4.registration_data_import = rdi2
    ind5.registration_data_import = rdi2

    ind1.save()
    ind2.save()
    ind3.save()
    ind4.save()
    ind5.save()

    for ind in [ind1, ind2, ind3]:
        ind.rdi_merge_status = MergeStatusModel.PENDING
        ind.save()

    service = BiometricDeduplicationService()
    similarity_pairs = [
        SimilarityPair(score=0.7, first=ind1.id, second=ind2.id, status_code="200"),
        SimilarityPair(score=0.8, first=ind1.id, second=ind3.id, status_code="200"),
        SimilarityPair(score=0.85, first=ind1.id, second=ind4.id, status_code="200"),
        SimilarityPair(score=0.8, first=ind2.id, second=ind4.id, status_code="200"),
        SimilarityPair(score=0.9, first=ind2.id, second=ind5.id, status_code="200"),
    ]
    service.store_similarity_pairs(program, similarity_pairs)

    service.store_rdis_deduplication_statistics(program)

    rdi1.refresh_from_db()
    assert rdi1.dedup_engine_batch_duplicates == 3
    assert rdi1.dedup_engine_golden_record_duplicates == 2
    ind1.refresh_from_db()
    assert ind1.biometric_deduplication_golden_record_results == [
        {
            "id": str(ind4.id),
            "unicef_id": str(ind4.unicef_id),
            "full_name": str(ind4.full_name),
            "similarity_score": 85.0,
            "age": ind4.age,
            "location": None,
        },
    ]
    assert ind1.biometric_deduplication_golden_record_status == DUPLICATE
    assert ind1.biometric_deduplication_batch_results == [
        {
            "id": str(ind2.id),
            "unicef_id": str(ind2.unicef_id),
            "full_name": str(ind2.full_name),
            "similarity_score": 70.0,
            "age": ind2.age,
            "location": None,
        },
        {
            "id": str(ind3.id),
            "unicef_id": str(ind3.unicef_id),
            "full_name": str(ind3.full_name),
            "similarity_score": 80.0,
            "age": ind3.age,
            "location": None,
        },
    ]
    assert ind1.biometric_deduplication_batch_status == DUPLICATE_IN_BATCH

    ind2.refresh_from_db()
    assert ind2.biometric_deduplication_golden_record_results == [
        {
            "id": str(ind4.id),
            "unicef_id": str(ind4.unicef_id),
            "full_name": str(ind4.full_name),
            "similarity_score": 80.0,
            "age": ind4.age,
            "location": None,
        },
        {
            "id": str(ind5.id),
            "unicef_id": str(ind5.unicef_id),
            "full_name": str(ind5.full_name),
            "similarity_score": 90.0,
            "age": ind5.age,
            "location": None,
        },
    ]
    assert ind2.biometric_deduplication_golden_record_status == DUPLICATE

    assert ind2.biometric_deduplication_batch_results == [
        {
            "id": str(ind1.id),
            "unicef_id": str(ind1.unicef_id),
            "full_name": str(ind1.full_name),
            "similarity_score": 70.0,
            "age": ind1.age,
            "location": None,
        },
    ]
    assert ind2.biometric_deduplication_batch_status == DUPLICATE_IN_BATCH

    ind3.refresh_from_db()
    assert ind3.biometric_deduplication_batch_results == [
        {
            "id": str(ind1.id),
            "unicef_id": str(ind1.unicef_id),
            "full_name": str(ind1.full_name),
            "similarity_score": 80.0,
            "age": ind1.age,
            "location": None,
        },
    ]
    assert ind2.biometric_deduplication_batch_status == DUPLICATE_IN_BATCH
    assert ind3.biometric_deduplication_golden_record_results == []
    assert ind3.biometric_deduplication_golden_record_status == UNIQUE


def test_update_rdis_deduplication_statistics(biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    user = biometric_deduplication_context["user"]
    rdi1 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        status=RegistrationDataImport.IN_REVIEW,
        dedup_engine_batch_duplicates=5,
        dedup_engine_golden_record_duplicates=6,
    )
    rdi2 = RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        imported_by=user,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
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
        SimilarityPair(score=0.7, first=ind1.id, second=ind2.id, status_code="200"),
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
        SimilarityPair(score=0.0, first=ind1.id, second=None, status_code="412"),
    ]
    DeduplicationEngineSimilarityPair.objects.all().delete()
    service.store_similarity_pairs(program, similarity_pairs)
    service.update_rdis_deduplication_statistics(program, exclude_rdi=rdi2)

    rdi1.refresh_from_db()
    assert rdi1.dedup_engine_batch_duplicates == 5
    assert rdi1.dedup_engine_golden_record_duplicates == 1
    ind1.refresh_from_db()
    assert ind1.biometric_deduplication_golden_record_results == []
    assert ind1.biometric_deduplication_golden_record_status == DUPLICATE
    assert ind1.biometric_deduplication_batch_status == NOT_PROCESSED


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.report_false_positive_duplicate")
def test_report_false_positive_duplicate(
    mock_report_false_positive_duplicate: mock.Mock, biometric_deduplication_context: dict[str, object]
) -> None:
    program = biometric_deduplication_context["program"]
    service = BiometricDeduplicationService()

    service.report_false_positive_duplicate("123", "456", program)
    mock_report_false_positive_duplicate.assert_called_once_with(
        IgnoredFilenamesPair(first="123", second="456"),
        program,
    )


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.report_individuals_status")
def test_report_withdrawn(mock_report_withdrawn: mock.Mock, biometric_deduplication_context: dict[str, object]) -> None:
    program = biometric_deduplication_context["program"]
    service = BiometricDeduplicationService()
    service.report_individuals_status(program.slug, ["abc"], "refused")
    mock_report_withdrawn.assert_called_once_with(
        str(program.slug),
        {"action": "refused", "targets": ["abc"]},
    )
