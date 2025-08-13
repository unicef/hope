import dataclasses
import os
import uuid
from itertools import batched, repeat
from unittest import mock
from unittest.mock import patch, call
from constance.test import override_config

from django.test import TestCase

import pytest

from hct_mis_api.apps.registration_datahub.apis.deduplication_engine import (
    DeduplicationEngineAPI,
    DeduplicationImage,
    DeduplicationSet,
    IgnoredFilenamesPair,
)


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


class DeduplicationEngineApiTest(TestCase):
    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI._delete")
    def test_delete_deduplication_set(self, mock_delete: mock.Mock) -> None:
        api = DeduplicationEngineAPI()

        deduplication_set_id = str(uuid.uuid4())
        mock_delete.return_value = {}, 200

        api.delete_deduplication_set(deduplication_set_id)

        mock_delete.assert_called_once_with(f"deduplication_sets/{deduplication_set_id}/")

    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI._post")
    def test_create_deduplication_set(self, mock_post: mock.Mock) -> None:
        api = DeduplicationEngineAPI()

        deduplication_set = DeduplicationSet(
            reference_pk=str(uuid.uuid4()),
            notification_url="http://test.com",
        )
        mock_post.return_value = {}, 200

        api.create_deduplication_set(deduplication_set)
        mock_post.assert_called_once_with("deduplication_sets/", dataclasses.asdict(deduplication_set))

    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI._get")
    def test_get_deduplication_set(self, get_mock: mock.Mock) -> None:
        api = DeduplicationEngineAPI()
        deduplication_set_id = str(uuid.uuid4())
        get_mock.return_value = {}, 200

        api.get_deduplication_set(deduplication_set_id)

        get_mock.assert_called_once_with(f"deduplication_sets/{deduplication_set_id}/")

    @override_config(DEDUPLICATION_IMAGE_UPLOAD_BATCH_SIZE=1)
    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI._post")
    def test_bulk_upload_images(self, mock_post: mock.Mock) -> None:
        api = DeduplicationEngineAPI()
        deduplication_set_id = str(uuid.uuid4())
        images = [
            DeduplicationImage(
                reference_pk=str(uuid.uuid4()),
                filename=f"test{i}.jpg",
            )
            for i in range(2)
        ]
        batches = [list(batch) for batch in batched(images, 1)]

        mock_post.side_effect = zip(batches, repeat(200))

        assert api.bulk_upload_images(deduplication_set_id, images) == images

        mock_post.assert_has_calls(
            [
                call(
                    f"deduplication_sets/{deduplication_set_id}/images_bulk/",
                    [dataclasses.asdict(image) for image in batch],
                )
                for batch in batches
            ]
        )

    @patch("hope.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI._post")
    def test_bulk_upload_images_json_parsing_error(self, mock_post: mock.Mock) -> None:
        api = DeduplicationEngineAPI()
        deduplication_set_id = str(uuid.uuid4())
        images = [
            DeduplicationImage(
                reference_pk=str(uuid.uuid4()),
                filename="test.jpg",
            )
        ]
        mock_post.return_value = {}, 200
        assert api.bulk_upload_images(deduplication_set_id, images) == []

    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI._delete")
    def test_bulk_delete_images(self, mock_delete: mock.Mock) -> None:
        api = DeduplicationEngineAPI()
        deduplication_set_id = str(uuid.uuid4())
        mock_delete.return_value = {}, 200

        api.bulk_delete_images(deduplication_set_id)

        mock_delete.assert_called_once_with(f"deduplication_sets/{deduplication_set_id}/images_bulk/")

    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI._get")
    def test_get_duplicates(self, get_mock: mock.Mock) -> None:
        api = DeduplicationEngineAPI()
        deduplication_set_id = str(uuid.uuid4())
        get_mock.return_value = {}, 200

        api.get_duplicates(deduplication_set_id)

        get_mock.assert_called_once_with(f"deduplication_sets/{deduplication_set_id}/duplicates/")

    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI._post")
    def test_process_deduplication(self, post_mock: mock.Mock) -> None:
        api = DeduplicationEngineAPI()
        deduplication_set_id = str(uuid.uuid4())
        post_mock.return_value = {}, 200

        api.process_deduplication(deduplication_set_id)

        post_mock.assert_called_once_with(
            f"deduplication_sets/{deduplication_set_id}/process/",
            validate_response=False,
        )

    @patch("hct_mis_api.apps.registration_datahub.apis.deduplication_engine.DeduplicationEngineAPI._post")
    def test_report_false_positive_duplicate(self, post_mock: mock.Mock) -> None:
        api = DeduplicationEngineAPI()
        deduplication_set_id = str(uuid.uuid4())
        post_mock.return_value = {}, 200

        api.report_false_positive_duplicate(
            IgnoredFilenamesPair(first="123", second="456"),
            deduplication_set_id,
        )

        post_mock.assert_called_once_with(
            f"deduplication_sets/{deduplication_set_id}/ignored/filenames/",
            {
                "first": "123",
                "second": "456",
            },
        )
