import os
import uuid
from unittest import mock
from unittest.mock import patch

from django.test import TestCase

import pytest

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import IndividualFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.apis.deduplication_engine import (
    DeduplicationEngineAPI,
    DeduplicationImage,
    DeduplicationImageSet,
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
                name=self.program.name,
                reference_id=str(self.program.deduplication_set_id),
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
            DeduplicationImageSet(data=[DeduplicationImage(id=str(individual.id), image_url="some_photo.jpg")]),
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

    # def test_create_duplicates(self):
    #     service = BiometricDeduplicationService()
    #     similarity_pairs = [SimilarityPair(similarity_score='0.9', first_individual=None, second_individual=None)]
    #
    #     service.create_duplicates("test_set_id", similarity_pairs)
    #
    #     mock_bulk_add_duplicates.assert_called_once_with("test_set_id", similarity_pairs)
