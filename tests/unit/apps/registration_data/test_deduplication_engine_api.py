import dataclasses
from itertools import batched, repeat
import os
from unittest import mock
from unittest.mock import call, patch
import uuid

from constance.test import override_config
import pytest

from hope.apps.registration_data.api.deduplication_engine import (
    DeduplicationEngineAPI,
    DeduplicationImage,
    DeduplicationSet,
    IgnoredFilenamesPair,
)

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def mock_deduplication_engine_env_vars() -> None:
    with mock.patch.dict(
        os.environ,
        {
            "DEDUPLICATION_ENGINE_API_KEY": "TEST",
            "DEDUPLICATION_ENGINE_API_URL": "TEST/",
        },
    ):
        yield


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._delete")
def test_delete_deduplication_set(mock_delete: mock.Mock) -> None:
    api = DeduplicationEngineAPI()

    mock_delete.return_value = {}, 200

    api.delete_deduplication_set("slug")

    mock_delete.assert_called_once_with("TEST/deduplication_sets/slug/")


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._post")
def test_create_deduplication_set(mock_post: mock.Mock) -> None:
    api = DeduplicationEngineAPI()

    deduplication_set = DeduplicationSet(
        reference_pk=str(uuid.uuid4()),
        notification_url="http://test.com",
    )
    mock_post.return_value = {}, 200

    api.create_deduplication_set(deduplication_set)
    mock_post.assert_called_once_with("TEST/deduplication_sets/", dataclasses.asdict(deduplication_set))


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._get")
def test_get_deduplication_set(get_mock: mock.Mock) -> None:
    api = DeduplicationEngineAPI()
    get_mock.return_value = {}, 200

    api.get_deduplication_set("slug")

    get_mock.assert_called_once_with("TEST/deduplication_sets/slug/")


@override_config(DEDUPLICATION_IMAGE_UPLOAD_BATCH_SIZE=1)
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._post")
def test_bulk_upload_images(mock_post: mock.Mock) -> None:
    api = DeduplicationEngineAPI()
    images = [
        DeduplicationImage(
            reference_pk=str(uuid.uuid4()),
            filename=f"test{i}.jpg",
        )
        for i in range(2)
    ]
    batches = [list(batch) for batch in batched(images, 1, strict=False)]

    mock_post.side_effect = zip(batches, repeat(200))

    assert api.bulk_upload_images("slug", images) == images

    mock_post.assert_has_calls(
        [
            call(
                "TEST/deduplication_sets/slug/images_bulk/",
                [dataclasses.asdict(image) for image in batch],
            )
            for batch in batches
        ]
    )


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._post")
def test_bulk_upload_images_json_parsing_error(mock_post: mock.Mock) -> None:
    api = DeduplicationEngineAPI()
    images = [
        DeduplicationImage(
            reference_pk=str(uuid.uuid4()),
            filename="test.jpg",
        )
    ]
    mock_post.return_value = {}, 200
    assert api.bulk_upload_images("slug", images) == []


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._delete")
def test_bulk_delete_images(mock_delete: mock.Mock) -> None:
    api = DeduplicationEngineAPI()
    mock_delete.return_value = {}, 200

    api.bulk_delete_images("slug")

    mock_delete.assert_called_once_with("TEST/deduplication_sets/slug/images_bulk/")


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._get")
def test_get_duplicates(get_mock: mock.Mock) -> None:
    api = DeduplicationEngineAPI()
    get_mock.return_value = {"results": []}, 200

    api.get_duplicates("slug", [])
    get_mock.assert_called_once_with("TEST/deduplication_sets/slug/duplicates/", "reference_pk=")


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._get")
def test_get_duplicates_paginated(get_mock: mock.Mock) -> None:
    api = DeduplicationEngineAPI()

    page1 = (
        {"next": "https://dedupe.api/deduplication_sets/x/duplicates/?page=2", "results": [{"id": 1}, {"id": 2}]},
        200,
    )
    page2 = ({"next": None, "results": [{"id": 3}, {"id": 4}]}, 200)

    get_mock.side_effect = [page1, page2]

    results = api.get_duplicates("slug", ["1,2,3,4"])
    assert results == [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]

    get_mock.assert_any_call("TEST/deduplication_sets/slug/duplicates/", "reference_pk=1,2,3,4")
    get_mock.assert_any_call("https://dedupe.api/deduplication_sets/x/duplicates/?page=2", None)
    assert get_mock.call_count == 2


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._post")
def test_process_deduplication(post_mock: mock.Mock) -> None:
    api = DeduplicationEngineAPI()
    post_mock.return_value = {}, 200

    api.process_deduplication("slug")

    post_mock.assert_called_once_with(
        "TEST/deduplication_sets/slug/process/",
        validate_response=False,
    )


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._post")
def test_report_false_positive_duplicate(post_mock: mock.Mock) -> None:
    api = DeduplicationEngineAPI()
    post_mock.return_value = {}, 200

    api.report_false_positive_duplicate(
        IgnoredFilenamesPair(first="123", second="456"),
        "slug",
    )

    post_mock.assert_called_once_with(
        "TEST/deduplication_sets/slug/ignored/filenames/",
        {
            "first": "123",
            "second": "456",
        },
    )


@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._post")
def test_report_refused_individuals(post_mock: mock.Mock) -> None:
    api = DeduplicationEngineAPI()
    post_mock.return_value = {}, 200

    api.report_individuals_status(
        "slug",
        {
            "action": "approved",
            "targets": ["abc", "def", "ghi"],
        },
    )

    post_mock.assert_called_once_with(
        "TEST/deduplication_sets/slug/approve_or_reject/",
        {
            "action": "approved",
            "targets": ["abc", "def", "ghi"],
        },
    )


@pytest.fixture
def get_mock() -> mock.Mock:
    with patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._get") as m:
        yield m


@pytest.fixture
def post_mock() -> mock.Mock:
    with patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._post") as m:
        yield m


@pytest.fixture
def findings_page_first() -> tuple[dict, int]:
    return (
        {
            "next": "https://dedupe.api/deduplication_set_groups/PROG-1/findings/?page=2",
            "results": [{"score": 0.9}, {"score": 0.8}],
        },
        200,
    )


@pytest.fixture
def findings_page_last() -> tuple[dict, int]:
    return ({"next": None, "results": [{"score": 0.7}]}, 200)


def test_get_group_findings_single_page(get_mock: mock.Mock) -> None:
    api = DeduplicationEngineAPI()
    finding = {
        "first": {"reference_pk": "1"},
        "second": {"reference_pk": "2"},
        "score": 0.9,
        "status_code": "200",
        "config": {},
        "updated_at": "2026-04-29T00:00:00Z",
    }
    get_mock.return_value = ({"count": 1, "next": None, "previous": None, "results": [finding]}, 200)

    results = list(api.get_group_findings("PROG-1"))

    assert results == [finding]
    get_mock.assert_called_once_with("TEST/deduplication_set_groups/PROG-1/findings/", None)


def test_get_group_findings_auto_paginates(
    get_mock: mock.Mock,
    findings_page_first: tuple[dict, int],
    findings_page_last: tuple[dict, int],
) -> None:
    api = DeduplicationEngineAPI()
    get_mock.side_effect = [findings_page_first, findings_page_last]

    results = list(api.get_group_findings("PROG-1"))

    assert results == [{"score": 0.9}, {"score": 0.8}, {"score": 0.7}]
    assert get_mock.call_count == 2
    get_mock.assert_any_call("TEST/deduplication_set_groups/PROG-1/findings/", None)
    get_mock.assert_any_call("https://dedupe.api/deduplication_set_groups/PROG-1/findings/?page=2", None)


def test_get_group_findings_with_filters(get_mock: mock.Mock) -> None:
    api = DeduplicationEngineAPI()
    get_mock.return_value = ({"next": None, "results": []}, 200)

    list(
        api.get_group_findings(
            "PROG-1",
            individual_reference_pks=["1", "2", "3"],
            status_code="200",
            updated_after="2026-04-01T00:00:00Z",
            updated_before="2026-04-29T00:00:00Z",
        )
    )

    get_mock.assert_called_once_with(
        "TEST/deduplication_set_groups/PROG-1/findings/",
        "reference_pk=1,2,3&status_code=200&updated_after=2026-04-01T00%3A00%3A00Z&updated_before=2026-04-29T00%3A00%3A00Z",
    )


def test_approve_group(post_mock: mock.Mock) -> None:
    api = DeduplicationEngineAPI()
    post_mock.return_value = {}, 200

    response, status_code = api.approve_group("PROG-1")

    assert status_code == 200
    post_mock.assert_called_once_with("TEST/deduplication_set_groups/PROG-1/approve/")
