import os
from unittest import mock
from unittest.mock import patch

import pytest

from hope.apps.registration_data.api.deduplication_engine import (
    BiometricDeduplicationEngineAPI,
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


@pytest.fixture
def get_mock() -> mock.Mock:
    with patch("hope.apps.registration_data.api.deduplication_engine.BiometricDeduplicationEngineAPI._get") as m:
        yield m


@pytest.fixture
def post_mock() -> mock.Mock:
    with patch("hope.apps.registration_data.api.deduplication_engine.BiometricDeduplicationEngineAPI._post") as m:
        yield m


@pytest.fixture
def findings_page_first() -> tuple[dict, int]:
    return (
        {
            "next": "https://dedupe.api/deduplication_sets/PROG-1/findings/?page=2",
            "results": [{"score": 0.9}, {"score": 0.8}],
        },
        200,
    )


@pytest.fixture
def findings_page_last() -> tuple[dict, int]:
    return ({"next": None, "results": [{"score": 0.7}]}, 200)


def test_get_group_findings_single_page(get_mock: mock.Mock) -> None:
    api = BiometricDeduplicationEngineAPI()
    finding = {
        "first": {"reference_pk": "1"},
        "second": {"reference_pk": "2"},
        "score": 0.9,
        "status_code": "200",
        "config": {},
        "updated_at": "2026-04-29T00:00:00Z",
    }
    get_mock.return_value = ({"count": 1, "next": None, "previous": None, "results": [finding]}, 200)

    results = list(api.get_rdi_findings("PROG-1"))

    assert results == [finding]
    get_mock.assert_called_once_with("TEST/deduplication_sets/PROG-1/findings/", None)


def test_get_group_findings_auto_paginates(
    get_mock: mock.Mock,
    findings_page_first: tuple[dict, int],
    findings_page_last: tuple[dict, int],
) -> None:
    api = BiometricDeduplicationEngineAPI()
    get_mock.side_effect = [findings_page_first, findings_page_last]

    results = list(api.get_rdi_findings("PROG-1"))

    assert results == [{"score": 0.9}, {"score": 0.8}, {"score": 0.7}]
    assert get_mock.call_count == 2
    get_mock.assert_any_call("TEST/deduplication_sets/PROG-1/findings/", None)
    get_mock.assert_any_call("https://dedupe.api/deduplication_sets/PROG-1/findings/?page=2", None)


def test_get_group_findings_with_filters(get_mock: mock.Mock) -> None:
    api = BiometricDeduplicationEngineAPI()
    get_mock.return_value = ({"next": None, "results": []}, 200)

    list(
        api.get_rdi_findings(
            "PROG-1",
            status_code="200",
            updated_after="2026-04-01T00:00:00Z",
            updated_before="2026-04-29T00:00:00Z",
        )
    )

    get_mock.assert_called_once_with(
        "TEST/deduplication_sets/PROG-1/findings/",
        "status_code=200&updated_after=2026-04-01T00%3A00%3A00Z&updated_before=2026-04-29T00%3A00%3A00Z",
    )
