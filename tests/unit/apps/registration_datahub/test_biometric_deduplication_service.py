import os
import uuid
from decimal import Decimal
from unittest import mock
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

import pytest

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import (
    IndividualFactory,
    PendingIndividualFactory,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.apis.deduplication_engine import (
    DeduplicationEngineAPI,
    DeduplicationImage,
    DeduplicationSet,
    DeduplicationSetConfig,
    DeduplicationSetData,
    IgnoredFilenamesPair,
    SimilarityPair,
)
from hct_mis_api.apps.registration_datahub.services.biometric_deduplication import (
    BiometricDeduplicationService,
)
from hct_mis_api.apps.utils.models import MergeStatusModel


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


class BiometricDeduplicationServiceTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.program = ProgramFactory.create(biometric_deduplication_enabled=True)

    @patch(
        "hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI.create_deduplication_set"
    )
    def test_create_deduplication_set(self, mock_create_deduplication_set: mock.Mock) -> None:
        service = BiometricDeduplicationService()

        new_uuid = str(uuid.uuid4())
        mock_create_deduplication_set.return_value = {"id": new_uuid}

        service.create_deduplication_set(self.program)

        self.program.refresh_from_db()
        self.assertEqual(str(self.program.deduplication_set_id), new_uuid)
        mock_create_deduplication_set.assert_called_once_with(
            DeduplicationSet(
                reference_pk=str(self.program.id),
                notification_url=f"https://{settings.DOMAIN_NAME}/api/rest/{self.program.business_area.slug}/programs/{str(self.program.id)}/registration-data/webhookdeduplication/",
                config=DeduplicationSetConfig(
                    face_distance_threshold=1 - (self.program.business_area.biometric_deduplication_threshold / 100)
                ),
            )
        )

    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI.get_duplicates")
    def test_get_deduplication_set_results(self, mock_get_duplicates: mock.Mock) -> None:
        service = BiometricDeduplicationService()
        deduplication_set_id = str(uuid.uuid4())

        service.get_deduplication_set_results(deduplication_set_id)

        mock_get_duplicates.assert_called_once_with(deduplication_set_id)

    @patch(
        "hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI.get_deduplication_set"
    )
    def test_get_deduplication_set(self, mock_get_deduplication_set: mock.Mock) -> None:
        service = BiometricDeduplicationService()
        deduplication_set_id = str(uuid.uuid4())

        mock_get_deduplication_set.return_value = dict(state="Clean", error=None)

        data = service.get_deduplication_set(deduplication_set_id)
        self.assertEqual(data, DeduplicationSetData(state="Clean"))

        mock_get_deduplication_set.assert_called_once_with(deduplication_set_id)

    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI.bulk_upload_images")
    def test_upload_individuals_success(self, mock_bulk_upload_images: mock.Mock) -> None:
        self.program.deduplication_set_id = uuid.uuid4()
        self.program.save()

        rdi = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING,
        )
        individual = IndividualFactory(registration_data_import=rdi, photo="some_photo.jpg")

        service = BiometricDeduplicationService()
        service.upload_individuals(str(self.program.deduplication_set_id), rdi)
        mock_bulk_upload_images.assert_called_once_with(
            str(self.program.deduplication_set_id),
            [DeduplicationImage(reference_pk=str(individual.id), filename="some_photo.jpg")],
        )

        rdi.refresh_from_db()
        assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_UPLOADED

        rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_ERROR
        rdi.save()
        service.upload_individuals(str(self.program.deduplication_set_id), rdi)
        rdi.refresh_from_db()
        assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_UPLOADED

    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI.bulk_upload_images")
    def test_upload_individuals_failure(self, mock_bulk_upload_images: mock.Mock) -> None:
        mock_bulk_upload_images.side_effect = DeduplicationEngineAPI.DeduplicationEngineAPIException
        rdi = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING,
        )
        IndividualFactory(registration_data_import=rdi, photo="some_photo.jpg")

        service = BiometricDeduplicationService()
        service.upload_individuals(str(self.program.deduplication_set_id), rdi)

        rdi.refresh_from_db()
        assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_UPLOAD_ERROR

    def test_upload_individuals_no_individuals(self) -> None:
        rdi = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING,
        )
        IndividualFactory(registration_data_import=rdi, photo="some_photo.jpg", withdrawn=True)

        service = BiometricDeduplicationService()
        service.upload_individuals(str(self.program.deduplication_set_id), rdi)

        rdi.refresh_from_db()
        assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_FINISHED

    @patch(
        "hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI.process_deduplication"
    )
    def test_process_deduplication_set(self, mock_process_deduplication: mock.Mock) -> None:
        self.program.deduplication_set_id = uuid.uuid4()
        self.program.save()
        rdi = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING,
        )
        service = BiometricDeduplicationService()

        mock_process_deduplication.return_value = ({}, 200)
        service.process_deduplication_set(str(self.program.deduplication_set_id), RegistrationDataImport.objects.all())
        mock_process_deduplication.assert_called_once_with(str(self.program.deduplication_set_id))
        rdi.refresh_from_db()
        self.assertEqual(
            rdi.deduplication_engine_status,
            RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS,
        )

        mock_process_deduplication.return_value = ({}, 409)
        with self.assertRaises(BiometricDeduplicationService.BiometricDeduplicationServiceException):
            service.process_deduplication_set(
                str(self.program.deduplication_set_id),
                RegistrationDataImport.objects.all(),
            )

        mock_process_deduplication.return_value = ({}, 400)
        service.process_deduplication_set(str(self.program.deduplication_set_id), RegistrationDataImport.objects.all())
        rdi.refresh_from_db()
        self.assertEqual(rdi.deduplication_engine_status, RegistrationDataImport.DEDUP_ENGINE_ERROR)

    @patch(
        "hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI.delete_deduplication_set"
    )
    def test_delete_deduplication_set(self, mock_delete_deduplication_set: mock.Mock) -> None:
        service = BiometricDeduplicationService()

        service.delete_deduplication_set(self.program)
        mock_delete_deduplication_set.assert_not_called()

        deduplication_set_id = uuid.uuid4()
        self.program.deduplication_set_id = deduplication_set_id
        self.program.save()
        service.delete_deduplication_set(self.program)
        mock_delete_deduplication_set.assert_called_once_with(str(deduplication_set_id))
        self.program.refresh_from_db()
        self.assertIsNone(self.program.deduplication_set_id)

    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI.bulk_upload_images")
    @patch(
        "hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI.process_deduplication"
    )
    def test_upload_and_process_deduplication_set(
        self, mock_process_deduplication: mock.Mock, mock_bulk_upload_images: mock.Mock
    ) -> None:
        mock_bulk_upload_images.return_value = ({}, 200)
        mock_process_deduplication.return_value = ({}, 200)
        service = BiometricDeduplicationService()

        # Test when biometric deduplication is not enabled
        self.program.biometric_deduplication_enabled = False
        self.program.save()

        with self.assertRaisesMessage(
            BiometricDeduplicationService.BiometricDeduplicationServiceException,
            "Biometric deduplication is not enabled for this program",
        ):
            service.upload_and_process_deduplication_set(self.program)

        # Test RDIs in progress
        self.program.biometric_deduplication_enabled = True
        self.program.save()

        rdi_1 = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING,
        )
        rdi_2 = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS,
        )
        IndividualFactory(registration_data_import=rdi_1, photo="some_photo1.jpg")
        PendingIndividualFactory(registration_data_import=rdi_2, photo="some_photo2.jpg")

        service.create_deduplication_set = mock.MagicMock()
        with self.assertRaisesMessage(
            BiometricDeduplicationService.BiometricDeduplicationServiceException,
            "Deduplication is already in progress for some RDIs",
        ):
            service.upload_and_process_deduplication_set(self.program)
            service.create_deduplication_set.assert_called_once_with(self.program)

        # Test when rdi images upload fails
        self.program.deduplication_set_id = uuid.uuid4()
        self.program.save()
        rdi_2.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_PENDING
        rdi_2.save()

        mock_bulk_upload_images.side_effect = DeduplicationEngineAPI.DeduplicationEngineAPIException
        with self.assertRaisesMessage(
            BiometricDeduplicationService.BiometricDeduplicationServiceException,
            "Failed to upload images for all RDIs",
        ):
            service.upload_and_process_deduplication_set(self.program)
            assert mock_bulk_upload_images.call_count == 2
            assert rdi_1.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_ERROR
            assert rdi_1.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_ERROR

        # Test when all rdi images are uploaded successfully
        mock_bulk_upload_images.reset_mock()
        mock_process_deduplication.reset_mock()
        mock_bulk_upload_images.side_effect = None

        rdi_1.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_PENDING
        rdi_1.save()
        rdi_2.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_PENDING
        rdi_2.save()
        service.upload_and_process_deduplication_set(self.program)

        assert mock_bulk_upload_images.call_count == 2
        assert mock_process_deduplication.call_count == 1
        rdi_1.refresh_from_db()
        rdi_2.refresh_from_db()
        assert rdi_1.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS
        assert rdi_2.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS

    def test_store_results(self) -> None:
        self.program.deduplication_set_id = uuid.uuid4()
        self.program.save()

        individuals = IndividualFactory.create_batch(3)
        ind1, ind2, ind3 = sorted(individuals, key=lambda x: x.id)

        service = BiometricDeduplicationService()
        similarity_pairs = [
            SimilarityPair(score=0.5, first=ind2.id, second=ind1.id),
            SimilarityPair(score=0.5, first=ind1.id, second=ind2.id),
            SimilarityPair(
                score=0.7,
                first=ind1.id,
                second=ind3.id,
            ),
            SimilarityPair(score=0.8, first=ind3.id, second=ind2.id),
            SimilarityPair(
                score=0.9,
                first=ind3.id,
                second=ind3.id,
            ),
        ]

        service.store_similarity_pairs(str(self.program.deduplication_set_id), similarity_pairs)

        assert self.program.deduplication_engine_similarity_pairs.count() == 3
        assert self.program.deduplication_engine_similarity_pairs.filter(
            individual1=ind1, individual2=ind2, similarity_score=50.00
        ).exists()
        assert self.program.deduplication_engine_similarity_pairs.filter(
            individual1=ind1, individual2=ind3, similarity_score=70.00
        ).exists()
        assert self.program.deduplication_engine_similarity_pairs.filter(
            individual1=ind2, individual2=ind3, similarity_score=80.00
        ).exists()

    def test_mark_rdis_as(self) -> None:
        service = BiometricDeduplicationService()

        self.program.deduplication_set_id = uuid.uuid4()
        self.program.save()
        rdi = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS,
        )

        service.mark_rdis_as_processing(str(self.program.deduplication_set_id))
        rdi.refresh_from_db()
        self.assertEqual(
            rdi.deduplication_engine_status,
            RegistrationDataImport.DEDUP_ENGINE_PROCESSING,
        )

        service.mark_rdis_as_deduplicated(str(self.program.deduplication_set_id))
        rdi.refresh_from_db()
        self.assertEqual(
            rdi.deduplication_engine_status,
            RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        )

        rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_PROCESSING
        rdi.save()

        service.mark_rdis_as_deduplication_error(str(self.program.deduplication_set_id))
        rdi.refresh_from_db()
        self.assertEqual(rdi.deduplication_engine_status, RegistrationDataImport.DEDUP_ENGINE_ERROR)

    def test_get_duplicates_for_rdi_against_population(self) -> None:
        self.program.deduplication_set_id = uuid.uuid4()
        self.program.business_area.biometric_deduplication_threshold = 0.6
        self.program.business_area.save()
        self.program.save()

        rdi1 = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        )
        rdi2 = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        )
        rdi3 = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        )
        individuals = IndividualFactory.create_batch(6, program=self.program)
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
            SimilarityPair(score=0.9, first=ind1.id, second=ind2.id),  # within rdi1
            SimilarityPair(score=0.7, first=ind1.id, second=ind3.id),  # across rdi1 and rdi2
            SimilarityPair(score=0.8, first=ind1.id, second=ind5.id),  # across rdi1 and population
            SimilarityPair(score=0.9, first=ind6.id, second=ind2.id),  # across rdi1 and population
            SimilarityPair(score=0.9, first=ind3.id, second=ind4.id),  # within rdi2
            SimilarityPair(score=0.7, first=ind4.id, second=ind5.id),  # across rdi2 and population
            SimilarityPair(score=0.8, first=ind5.id, second=ind6.id),  # within population
        ]
        service.store_similarity_pairs(str(self.program.deduplication_set_id), similarity_pairs)

        duplicates = service.get_duplicates_for_rdi_against_population(rdi1)

        assert len(duplicates) == 2
        assert list(
            duplicates.order_by("similarity_score").values("individual1", "individual2", "similarity_score")
        ) == [
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

        duplicate_individuals_count = service.get_duplicate_individuals_for_rdi_against_population_count(rdi1)
        assert duplicate_individuals_count == 2

    def test_get_duplicates_for_merged_rdi_against_population(self) -> None:
        self.program.deduplication_set_id = uuid.uuid4()
        self.program.business_area.biometric_deduplication_threshold = 0.6
        self.program.business_area.save()
        self.program.save()

        rdi1 = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        )
        rdi2 = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        )
        rdi3 = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        )
        individuals = IndividualFactory.create_batch(6, program=self.program)
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

        for ind in [ind3, ind4]:
            ind.rdi_merge_status = MergeStatusModel.PENDING
            ind.save()

        service = BiometricDeduplicationService()
        similarity_pairs = [
            SimilarityPair(score=0.7, first=ind1.id, second=ind2.id),  # within merged rdi1
            SimilarityPair(score=0.7, first=ind1.id, second=ind3.id),  # across merged rdi1 and pending rdi2
            SimilarityPair(score=0.8, first=ind1.id, second=ind5.id),  # across merged rdi1 and population
            SimilarityPair(score=0.9, first=ind2.id, second=ind6.id),  # across merged rdi1 and population
            SimilarityPair(score=0.9, first=ind3.id, second=ind4.id),  # within pending rdi2
            SimilarityPair(score=0.7, first=ind4.id, second=ind5.id),  # across pending rdi2 and population
            SimilarityPair(score=0.8, first=ind5.id, second=ind6.id),  # within population
        ]
        service.store_similarity_pairs(str(self.program.deduplication_set_id), similarity_pairs)

        duplicates = service.get_duplicates_for_merged_rdi_against_population(rdi2)

        assert len(duplicates) == 3
        assert list(
            duplicates.order_by("similarity_score").values("individual1", "individual2", "similarity_score")
        ) == [
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

    def test_get_duplicates_for_rdi_against_batch(self) -> None:
        self.program.deduplication_set_id = uuid.uuid4()
        self.program.business_area.biometric_deduplication_threshold = 0.6
        self.program.business_area.save()
        self.program.save()

        rdi1 = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        )
        rdi2 = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        )
        rdi3 = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        )
        individuals = IndividualFactory.create_batch(6, program=self.program)
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
            SimilarityPair(score=0.9, first=ind1.id, second=ind2.id),  # within rdi1
            SimilarityPair(score=0.7, first=ind1.id, second=ind3.id),  # across rdi1 and rdi2
            SimilarityPair(score=0.8, first=ind1.id, second=ind5.id),  # across rdi1 and population
            SimilarityPair(score=0.9, first=ind2.id, second=ind6.id),  # across rdi1 and population
            SimilarityPair(score=0.9, first=ind3.id, second=ind4.id),  # within rdi2
            SimilarityPair(score=0.7, first=ind4.id, second=ind5.id),  # across rdi2 and population
            SimilarityPair(score=0.8, first=ind5.id, second=ind6.id),  # within population
        ]
        service.store_similarity_pairs(str(self.program.deduplication_set_id), similarity_pairs)

        duplicates = service.get_duplicates_for_rdi_against_batch(rdi1)

        assert len(duplicates) == 1
        assert list(
            duplicates.order_by("similarity_score").values("individual1", "individual2", "similarity_score")
        ) == [
            {
                "individual1": ind1.id,
                "individual2": ind2.id,
                "similarity_score": Decimal("90.00"),
            },
        ]
        duplicate_individuals_count = service.get_duplicate_individuals_for_rdi_against_batch_count(rdi1)
        assert duplicate_individuals_count == 2

    @patch(
        "hct_mis_api.apps.grievance.services.needs_adjudication_ticket_services.create_needs_adjudication_tickets_for_biometrics"
    )
    def test_create_grievance_tickets_for_duplicates(
        self, create_needs_adjudication_tickets_for_biometrics_mock: mock.Mock
    ) -> None:
        rdi1 = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
        )

        service = BiometricDeduplicationService()
        service.get_duplicates_for_merged_rdi_against_population = mock.MagicMock()
        service.get_duplicates_for_merged_rdi_against_population.return_value = []

        service.create_grievance_tickets_for_duplicates(rdi1)
        create_needs_adjudication_tickets_for_biometrics_mock.assert_called_once_with([], rdi1)

    def test_fetch_biometric_deduplication_results_and_process_success(self) -> None:
        deduplication_set_id = str(uuid.uuid4())
        service = BiometricDeduplicationService()

        service.get_deduplication_set = mock.Mock(return_value=DeduplicationSetData(state="Clean"))

        results_data = [
            {
                "first": {"reference_pk": "1"},
                "second": {"reference_pk": "2"},
                "score": 0.9,
            },
            {
                "first": {"reference_pk": "3"},
                "second": {"reference_pk": "4"},
                "score": 0.8,
            },
        ]
        service.get_deduplication_set_results = mock.Mock(return_value=results_data)
        service.store_similarity_pairs = mock.Mock()
        service.store_rdis_deduplication_statistics = mock.Mock()
        service.mark_rdis_as_deduplicated = mock.Mock()

        service.fetch_biometric_deduplication_results_and_process(deduplication_set_id)

        service.get_deduplication_set.assert_called_once_with(deduplication_set_id)
        service.get_deduplication_set_results.assert_called_once_with(deduplication_set_id)
        service.store_similarity_pairs.assert_called_once_with(
            deduplication_set_id,
            [
                SimilarityPair(
                    score=item["score"],
                    first=item["first"]["reference_pk"],  # type: ignore
                    second=item["second"]["reference_pk"],  # type: ignore
                )
                for item in results_data
            ],
        )

    def test_fetch_biometric_deduplication_results_and_process_fail(self) -> None:
        deduplication_set_id = str(uuid.uuid4())
        service = BiometricDeduplicationService()

        service.get_deduplication_set = mock.Mock(return_value=DeduplicationSetData(state="Error"))
        service.mark_rdis_as_deduplication_error = mock.Mock()

        service.fetch_biometric_deduplication_results_and_process(deduplication_set_id)

        service.get_deduplication_set.assert_called_once_with(deduplication_set_id)
        service.mark_rdis_as_deduplication_error.assert_called_once_with(deduplication_set_id)

    def test_store_rdis_deduplication_statistics(self) -> None:
        deduplication_set_id = str(uuid.uuid4())
        self.program.deduplication_set_id = deduplication_set_id
        self.program.save()

        service = BiometricDeduplicationService()

        rdi1 = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PROCESSING,
        )

        service.get_duplicate_individuals_for_rdi_against_batch_count = mock.Mock(return_value=8)
        service.get_duplicate_individuals_for_rdi_against_population_count = mock.Mock(return_value=9)

        service.store_rdis_deduplication_statistics(deduplication_set_id)

        service.get_duplicate_individuals_for_rdi_against_batch_count.assert_called_once_with(rdi1)
        service.get_duplicate_individuals_for_rdi_against_population_count.assert_called_once_with(rdi1)

        rdi1.refresh_from_db()
        assert rdi1.dedup_engine_batch_duplicates == 8
        assert rdi1.dedup_engine_golden_record_duplicates == 9

    def test_update_rdis_deduplication_statistics(self) -> None:
        deduplication_set_id = str(uuid.uuid4())
        self.program.deduplication_set_id = deduplication_set_id
        self.program.save()

        service = BiometricDeduplicationService()

        rdi1 = RegistrationDataImportFactory(
            program=self.program,
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
            status=RegistrationDataImport.IN_REVIEW,
        )

        service.get_duplicate_individuals_for_rdi_against_batch_count = mock.Mock(return_value=8)
        service.get_duplicate_individuals_for_rdi_against_population_count = mock.Mock(return_value=9)

        service.update_rdis_deduplication_statistics(self.program.id)

        service.get_duplicate_individuals_for_rdi_against_batch_count.assert_called_once_with(rdi1)
        service.get_duplicate_individuals_for_rdi_against_population_count.assert_called_once_with(rdi1)

        rdi1.refresh_from_db()
        assert rdi1.dedup_engine_batch_duplicates == 8
        assert rdi1.dedup_engine_golden_record_duplicates == 9

    @patch(
        "hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI.report_false_positive_duplicate"
    )
    def test_report_false_positive_duplicate(self, mock_report_false_positive_duplicate: mock.Mock) -> None:
        service = BiometricDeduplicationService()
        deduplication_set_id = uuid.uuid4()

        service.report_false_positive_duplicate("123", "456", str(deduplication_set_id))
        mock_report_false_positive_duplicate.assert_called_once_with(
            IgnoredFilenamesPair(first="123", second="456"),
            str(deduplication_set_id),
        )
