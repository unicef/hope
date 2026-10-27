from unittest import mock
from unittest.mock import patch

import pytest

from hope.apps.registration_data.api.deduplication_engine import (
    DeduplicationEngineAPI,
)

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def mock_deduplication_engine_env_vars(settings) -> None:
    settings.DEDUPLICATION_ENGINE_API_KEY = "TEST"
    settings.DEDUPLICATION_ENGINE_API_URL = "TEST/"


@pytest.fixture
def get_mock() -> mock.Mock:
    with patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._get") as m:
        yield m


@pytest.fixture
def post_mock() -> mock.Mock:
    with patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI._post") as m:
        yield m


@pytest.fixture
def biometric_findings_page_first() -> tuple[dict, int]:
    return (
        {
            "next": "https://dedupe.api/deduplication_sets/PROG-1/biometric_findings/?page=2",
            "results": [{"score": 0.9}, {"score": 0.8}],
        },
        200,
    )


@pytest.fixture
def biographic_findings_page_first() -> tuple[dict, int]:
    return (
        {
            "next": "https://dedupe.api/deduplication_sets/PROG-1/biographic_findings/?page=2",
            "results": [{"score": 0.9}, {"score": 0.8}],
        },
        200,
    )


@pytest.fixture
def findings_page_last() -> tuple[dict, int]:
    return ({"next": None, "results": [{"score": 0.7}]}, 200)


@pytest.fixture
def empty_findings_page() -> tuple[dict, int]:
    return ({"next": None, "results": []}, 200)


@pytest.fixture
def biographic_finding() -> dict:
    return {
        "first": {"reference_pk": "1"},
        "second": {"reference_pk": "2"},
        "score": 12.3,
        "status_code": "200",
        "config": {},
        "updated_at": "2026-04-29T00:00:00Z",
        "proximity_to_score": 2.3,
    }


@pytest.fixture
def biographic_findings_single_page(biographic_finding: dict) -> tuple[dict, int]:
    return ({"count": 1, "next": None, "previous": None, "results": [biographic_finding]}, 200)


def test_get_rdi_biometric_findings_single_page(get_mock: mock.Mock) -> None:
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

    results = list(api.get_rdi_biometric_findings("PROG-1"))

    assert results == [finding]
    get_mock.assert_called_once_with("TEST/deduplication_sets/PROG-1/biometric_findings/", None)


def test_get_rdi_biometric_findings_auto_paginates(
    get_mock: mock.Mock,
    biometric_findings_page_first: tuple[dict, int],
    findings_page_last: tuple[dict, int],
) -> None:
    api = DeduplicationEngineAPI()
    get_mock.side_effect = [biometric_findings_page_first, findings_page_last]

    results = list(api.get_rdi_biometric_findings("PROG-1"))

    assert results == [{"score": 0.9}, {"score": 0.8}, {"score": 0.7}]
    assert get_mock.call_count == 2
    get_mock.assert_any_call("TEST/deduplication_sets/PROG-1/biometric_findings/", None)
    get_mock.assert_any_call("https://dedupe.api/deduplication_sets/PROG-1/biometric_findings/?page=2", None)


def test_get_rdi_biometric_findings_with_filters(get_mock: mock.Mock) -> None:
    api = DeduplicationEngineAPI()
    get_mock.return_value = ({"next": None, "results": []}, 200)

    list(
        api.get_rdi_biometric_findings(
            "PROG-1",
            status_code="200",
            updated_after="2026-04-01T00:00:00Z",
            updated_before="2026-04-29T00:00:00Z",
        )
    )

    get_mock.assert_called_once_with(
        "TEST/deduplication_sets/PROG-1/biometric_findings/",
        "status_code=200&updated_after=2026-04-01T00%3A00%3A00Z&updated_before=2026-04-29T00%3A00%3A00Z",
    )


def test_get_rdi_biographic_findings_single_page(
    get_mock: mock.Mock,
    biographic_finding: dict,
    biographic_findings_single_page: tuple[dict, int],
) -> None:
    api = DeduplicationEngineAPI()
    get_mock.return_value = biographic_findings_single_page

    results = list(api.get_rdi_biographic_findings("PROG-1"))

    assert results == [biographic_finding]
    get_mock.assert_called_once_with("TEST/deduplication_sets/PROG-1/biographic_findings/", None)


def test_get_rdi_biographic_findings_auto_paginates(
    get_mock: mock.Mock,
    biographic_findings_page_first: tuple[dict, int],
    findings_page_last: tuple[dict, int],
) -> None:
    api = DeduplicationEngineAPI()
    get_mock.side_effect = [biographic_findings_page_first, findings_page_last]

    results = list(api.get_rdi_biographic_findings("PROG-1"))

    assert results == [{"score": 0.9}, {"score": 0.8}, {"score": 0.7}]
    assert get_mock.call_count == 2
    get_mock.assert_any_call("TEST/deduplication_sets/PROG-1/biographic_findings/", None)
    get_mock.assert_any_call("https://dedupe.api/deduplication_sets/PROG-1/biographic_findings/?page=2", None)


def test_get_rdi_biographic_findings_with_filters(get_mock: mock.Mock, empty_findings_page: tuple[dict, int]) -> None:
    api = DeduplicationEngineAPI()
    get_mock.return_value = empty_findings_page

    list(
        api.get_rdi_biographic_findings(
            "PROG-1",
            updated_after="2026-04-01T00:00:00Z",
            updated_before="2026-04-29T00:00:00Z",
        )
    )

    get_mock.assert_called_once_with(
        "TEST/deduplication_sets/PROG-1/biographic_findings/",
        "updated_after=2026-04-01T00%3A00%3A00Z&updated_before=2026-04-29T00%3A00%3A00Z",
    )
