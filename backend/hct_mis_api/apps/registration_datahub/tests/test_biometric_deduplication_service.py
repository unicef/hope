import os
import uuid
from decimal import Decimal
from unittest import mock
from unittest.mock import patch

from django.test import TestCase

import pytest

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import IndividualFactory
from hct_mis_api.apps.payment.api.dataclasses import SimilarityPair
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.apis.deduplication_engine import (
    DeduplicationEngineAPI,
    DeduplicationImage,
    DeduplicationSet,
)
from hct_mis_api.apps.registration_datahub.services.biometric_deduplication import (
    BiometricDeduplicationService,
)


@pytest.fixture(autouse=True)
def mock_deduplication_engine_env_vars() -> None:
    with mock.patch.dict(os.environ, {"DEDUPLICATION_ENGINE_API_KEY": "TEST", "DEDUPLICATION_ENGINE_API_URL": "TEST"}):
        yield


class BiometricDeduplicationServiceTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.program = ProgramFactory.create(biometric_deduplication_enabled=True)

    @patch(
        "hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI.create_deduplication_set"
    )
    def test_create_deduplication_set(self, mock_create_deduplication_set: mock.Mock) -> None:
        service = BiometricDeduplicationService()

        service.create_deduplication_set(self.program)

        self.assertIsNotNone(self.program.deduplication_set_id)
        mock_create_deduplication_set.assert_called_once_with(
            DeduplicationSet(
                reference_pk=str(self.program.deduplication_set_id),
                notification_url="",
            )
        )

    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI.bulk_upload_images")
    def test_upload_individuals_success(self, mock_bulk_upload_images: mock.Mock) -> None:
        self.program.deduplication_set_id = uuid.uuid4()
        self.program.save()
        rdi = RegistrationDataImportFactory(
            program=self.program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING
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

    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI.bulk_upload_images")
    def test_upload_individuals_failure(self, mock_bulk_upload_images: mock.Mock) -> None:
        mock_bulk_upload_images.side_effect = DeduplicationEngineAPI.DeduplicationEngineAPIException
        rdi = RegistrationDataImportFactory(
            program=self.program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING
        )
        IndividualFactory(registration_data_import=rdi, photo="some_photo.jpg")

        service = BiometricDeduplicationService()
        service.upload_individuals(str(self.program.deduplication_set_id), rdi)

        rdi.refresh_from_db()
        assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_UPLOAD_ERROR

    @patch(
        "hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI.process_deduplication"
    )
    def test_process_deduplication_set(self, mock_process_deduplication: mock.Mock) -> None:
        self.program.deduplication_set_id = uuid.uuid4()
        self.program.save()
        rdi = RegistrationDataImportFactory(
            program=self.program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING
        )
        service = BiometricDeduplicationService()

        mock_process_deduplication.return_value = ({}, 200)
        service.process_deduplication_set(str(self.program.deduplication_set_id), RegistrationDataImport.objects.all())
        mock_process_deduplication.assert_called_once_with(str(self.program.deduplication_set_id))
        rdi.refresh_from_db()
        self.assertEqual(rdi.deduplication_engine_status, RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS)

        mock_process_deduplication.return_value = ({}, 409)
        with self.assertRaises(BiometricDeduplicationService.BiometricDeduplicationServiceException):
            service.process_deduplication_set(
                str(self.program.deduplication_set_id), RegistrationDataImport.objects.all()
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

        mock_delete_deduplication_set.assert_called_once_with(str(self.program.deduplication_set_id))
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
            program=self.program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING
        )
        rdi_2 = RegistrationDataImportFactory(
            program=self.program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS
        )
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
            BiometricDeduplicationService.BiometricDeduplicationServiceException, "Failed to upload images for all RDIs"
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
            SimilarityPair(similarity_score=0.5, first=ind2.id, second=ind1.id),
            SimilarityPair(similarity_score=0.5, first=ind1.id, second=ind2.id),
            SimilarityPair(
                similarity_score=0.7,
                first=ind1.id,
                second=ind3.id,
            ),
            SimilarityPair(similarity_score=0.8, first=ind3.id, second=ind2.id),
            SimilarityPair(
                similarity_score=0.9,
                first=ind3.id,
                second=ind3.id,
            ),
        ]

        service.store_results(str(self.program.deduplication_set_id), similarity_pairs)

        assert self.program.deduplication_engine_similarity_pairs.count() == 3
        assert self.program.deduplication_engine_similarity_pairs.filter(
            individual1=ind1, individual2=ind2, similarity_score=0.5
        ).exists()
        assert self.program.deduplication_engine_similarity_pairs.filter(
            individual1=ind1, individual2=ind3, similarity_score=0.7
        ).exists()
        assert self.program.deduplication_engine_similarity_pairs.filter(
            individual1=ind2, individual2=ind3, similarity_score=0.8
        ).exists()

    def test_get_duplicates_for_rdi(self) -> None:
        self.program.deduplication_set_id = uuid.uuid4()
        self.program.business_area.biometric_deduplication_threshold = 0.6
        self.program.business_area.save()
        self.program.save()

        individuals = IndividualFactory.create_batch(3)
        rdi = RegistrationDataImportFactory(
            program=self.program, deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING
        )
        ind1, ind2, ind3 = sorted(individuals, key=lambda x: x.id)
        rdi.individuals.add(ind1, ind2, ind3)

        service = BiometricDeduplicationService()
        similarity_pairs = [
            SimilarityPair(similarity_score=0.5, first=ind1.id, second=ind2.id),
            SimilarityPair(
                similarity_score=0.7,
                first=ind1.id,
                second=ind3.id,
            ),
            SimilarityPair(similarity_score=0.8, first=ind2.id, second=ind3.id),
            SimilarityPair(
                similarity_score=0.9,
                first=ind1.id,
                second=ind3.id,
            ),
        ]
        service.store_results(str(self.program.deduplication_set_id), similarity_pairs)

        duplicates = service.get_duplicates_for_rdi(rdi)

        assert len(duplicates) == 2
        assert list(
            duplicates.order_by("similarity_score").values("individual1", "individual2", "similarity_score")
        ) == [
            {"individual1": ind1.id, "individual2": ind3.id, "similarity_score": Decimal("0.7")},
            {"individual1": ind2.id, "individual2": ind3.id, "similarity_score": Decimal("0.8")},
        ]
