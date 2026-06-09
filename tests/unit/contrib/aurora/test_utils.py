from typing import Any
from unittest.mock import MagicMock

from constance.test import override_config
from django.utils import timezone
import pytest

from extras.test_utils.factories import RecordFactory
from hope.contrib.aurora.models import Organization, Project, Record, Registration
from hope.contrib.aurora.utils import fetch_metadata, fetch_records, get_metadata

pytestmark = pytest.mark.django_db


def _mock_responses(*data: Any) -> list:
    responses = []
    for item in data:
        if isinstance(item, Exception):
            mock_resp = MagicMock()
            mock_resp.json.side_effect = item
        else:
            mock_resp = MagicMock()
            mock_resp.json.return_value = item
        responses.append(mock_resp)
    return responses


@pytest.fixture
def mock_aurora_client(mocker: Any) -> Any:
    session_instance = MagicMock()
    mocker.patch("hope.contrib.aurora.utils.requests.Session", return_value=session_instance)
    return session_instance


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_metadata_persists_full_hierarchy(mock_aurora_client: Any) -> None:
    schema = {
        "organization": "https://aurora.test/api/orgs/",
        "record": "https://aurora.test/api/records/",
    }
    orgs_page = {
        "results": [
            {
                "id": 1,
                "name": "Org A",
                "slug": "org-a",
                "projects": "https://aurora.test/api/orgs/1/projects/",
            }
        ]
    }
    projects_page = {
        "results": [
            {
                "id": 10,
                "name": "Project A",
                "registrations": "https://aurora.test/api/projects/10/registrations/",
            }
        ]
    }
    registrations_list = [
        {
            "id": 100,
            "name": "Registration A",
            "slug": "reg-a",
            "metadata": "https://aurora.test/api/registrations/100/metadata/",
        }
    ]
    metadata_dict = {"definition": ["field-a", "field-b"]}
    mock_aurora_client.get.side_effect = _mock_responses(
        schema, orgs_page, projects_page, registrations_list, metadata_dict
    )

    result = fetch_metadata("test-token")

    assert len(result) == 1
    assert result[0]["id"] == 1
    assert Organization.objects.filter(source_id=1, slug="org-a").exists()
    assert Project.objects.filter(source_id=10, name="Project A").exists()
    registration = Registration.objects.get(source_id=100)
    assert registration.slug == "reg-a"
    assert registration.metadata == metadata_dict


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_metadata_logs_when_no_codec_available(mock_aurora_client: Any, mocker: Any) -> None:
    schema = {
        "organization": "https://aurora.test/api/orgs/",
        "record": "https://aurora.test/api/records/",
    }
    orgs_page = {
        "results": [
            {
                "id": 2,
                "name": "Org B",
                "slug": "org-b",
                "projects": "https://aurora.test/api/orgs/2/projects/",
            }
        ]
    }
    projects_page = {
        "results": [
            {
                "id": 20,
                "name": "Project B",
                "registrations": "https://aurora.test/api/projects/20/registrations/",
            }
        ]
    }
    registrations_list = [
        {
            "id": 200,
            "name": "Registration B",
            "slug": "reg-b",
            "metadata": "https://aurora.test/api/registrations/200/metadata/",
        }
    ]
    mock_aurora_client.get.side_effect = _mock_responses(
        schema, orgs_page, projects_page, registrations_list, ValueError("unsupported codec")
    )
    mock_logger = mocker.patch("hope.contrib.aurora.utils.logger")

    fetch_metadata("test-token")

    registration = Registration.objects.get(source_id=200)
    assert registration.metadata == {}
    mock_logger.exception.assert_called_once()


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_get_metadata_returns_record_metadata(mock_aurora_client: Any) -> None:
    schema = {"record": "https://aurora.test/api/records/"}
    metadata_dict = {"definition": [1, 2, 3]}
    mock_aurora_client.get.side_effect = _mock_responses(schema, metadata_dict)

    result = get_metadata("test-token")

    assert result == metadata_dict
    assert mock_aurora_client.get.call_count == 2
    second_call_url = mock_aurora_client.get.call_args_list[1].args[0]
    assert second_call_url.startswith(schema["record"] + "metadata/?")


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_records_creates_new_records(mock_aurora_client: Any) -> None:
    schema = {"record": "https://aurora.test/api/records/"}
    page = {
        "results": [
            {
                "id": 42,
                "registration": 7,
                "timestamp": timezone.now(),
                "status": Record.STATUS_TO_IMPORT,
                "data": {"foo": "bar"},
                "should_be_filtered_out": "drop",
            }
        ]
    }
    mock_aurora_client.get.side_effect = _mock_responses(schema, page)

    result = fetch_records("test-token", overwrite=False, registration=7)

    assert result == {"pages": 1, "records": 1, "created": 1, "updated": 0}
    record = Record.objects.get(source_id=42)
    assert record.registration == 7
    assert record.data == {"foo": "bar"}
    fetched_url = mock_aurora_client.get.call_args_list[1].args[0]
    assert fetched_url == "https://aurora.test/api/records/?registration=7"


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_metadata_missing_organization_key_returns_empty(mock_aurora_client: Any) -> None:
    schema = {"record": "https://aurora.test/api/records/"}  # no "organization" key
    mock_aurora_client.get.side_effect = _mock_responses(schema)

    result = fetch_metadata("test-token")

    assert result == []
    assert Organization.objects.count() == 0


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_metadata_skips_non_dict_org(mock_aurora_client: Any) -> None:
    schema = {"organization": "https://aurora.test/api/orgs/"}
    orgs_page = {"results": ["not-a-dict"]}
    mock_aurora_client.get.side_effect = _mock_responses(schema, orgs_page)

    result = fetch_metadata("test-token")

    assert result == []


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_metadata_skips_org_missing_id(mock_aurora_client: Any) -> None:
    schema = {"organization": "https://aurora.test/api/orgs/"}
    orgs_page = {"results": [{"name": "No ID Org", "slug": "no-id"}]}  # missing "id" and "projects"
    mock_aurora_client.get.side_effect = _mock_responses(schema, orgs_page)

    result = fetch_metadata("test-token")

    assert result == []
    assert Organization.objects.count() == 0


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_metadata_projects_fetch_error_returns_empty_projects(mock_aurora_client: Any, mocker: Any) -> None:
    schema = {"organization": "https://aurora.test/api/orgs/"}
    orgs_page = {
        "results": [{"id": 3, "name": "Org C", "slug": "org-c", "projects": "https://aurora.test/api/orgs/3/projects/"}]
    }
    mock_session = mock_aurora_client
    mock_session.get.side_effect = [
        MagicMock(json=MagicMock(return_value=schema), raise_for_status=MagicMock()),
        MagicMock(json=MagicMock(return_value=orgs_page), raise_for_status=MagicMock()),
        MagicMock(raise_for_status=MagicMock(side_effect=__import__("requests").RequestException("timeout"))),
    ]

    result = fetch_metadata("test-token")

    assert len(result) == 1
    assert result[0]["projects"] == []


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_metadata_skips_non_dict_project(mock_aurora_client: Any) -> None:
    schema = {"organization": "https://aurora.test/api/orgs/"}
    orgs_page = {
        "results": [{"id": 4, "name": "Org D", "slug": "org-d", "projects": "https://aurora.test/api/orgs/4/projects/"}]
    }
    projects_page = {"results": ["not-a-dict"]}
    mock_aurora_client.get.side_effect = _mock_responses(schema, orgs_page, projects_page)

    result = fetch_metadata("test-token")

    assert result[0]["projects"] == []


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_metadata_skips_project_missing_id(mock_aurora_client: Any) -> None:
    schema = {"organization": "https://aurora.test/api/orgs/"}
    orgs_page = {
        "results": [{"id": 5, "name": "Org E", "slug": "org-e", "projects": "https://aurora.test/api/orgs/5/projects/"}]
    }
    projects_page = {"results": [{"name": "No ID Project"}]}  # missing "id" and "registrations"
    mock_aurora_client.get.side_effect = _mock_responses(schema, orgs_page, projects_page)

    result = fetch_metadata("test-token")

    assert result[0]["projects"] == []
    assert Project.objects.count() == 0


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_metadata_registrations_fetch_error_returns_empty_registrations(mock_aurora_client: Any) -> None:
    import requests as _requests

    schema = {"organization": "https://aurora.test/api/orgs/"}
    orgs_page = {
        "results": [{"id": 6, "name": "Org F", "slug": "org-f", "projects": "https://aurora.test/api/orgs/6/projects/"}]
    }
    projects_page = {
        "results": [{"id": 60, "name": "Project F", "registrations": "https://aurora.test/api/projects/60/regs/"}]
    }
    m_regs = MagicMock()
    m_regs.raise_for_status.side_effect = _requests.RequestException("timeout")
    mock_aurora_client.get.side_effect = [
        *_mock_responses(schema, orgs_page, projects_page),
        m_regs,
    ]

    result = fetch_metadata("test-token")

    assert result[0]["projects"][0]["registrations"] == []


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_metadata_skips_non_dict_registration(mock_aurora_client: Any) -> None:
    schema = {"organization": "https://aurora.test/api/orgs/"}
    orgs_page = {
        "results": [{"id": 7, "name": "Org G", "slug": "org-g", "projects": "https://aurora.test/api/orgs/7/projects/"}]
    }
    projects_page = {
        "results": [{"id": 70, "name": "Project G", "registrations": "https://aurora.test/api/projects/70/regs/"}]
    }
    regs = ["not-a-dict"]
    mock_aurora_client.get.side_effect = _mock_responses(schema, orgs_page, projects_page, regs)

    result = fetch_metadata("test-token")

    assert result[0]["projects"][0]["registrations"] == []


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_metadata_skips_registration_missing_id(mock_aurora_client: Any) -> None:
    schema = {"organization": "https://aurora.test/api/orgs/"}
    orgs_page = {
        "results": [{"id": 8, "name": "Org H", "slug": "org-h", "projects": "https://aurora.test/api/orgs/8/projects/"}]
    }
    projects_page = {
        "results": [{"id": 80, "name": "Project H", "registrations": "https://aurora.test/api/projects/80/regs/"}]
    }
    regs = [{"name": "No ID Reg", "slug": "no-id"}]  # missing "id"
    mock_aurora_client.get.side_effect = _mock_responses(schema, orgs_page, projects_page, regs)

    result = fetch_metadata("test-token")

    assert result[0]["projects"][0]["registrations"] == []
    assert Registration.objects.count() == 0


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_get_metadata_missing_record_key_returns_empty(mock_aurora_client: Any) -> None:
    schema = {"organization": "https://aurora.test/api/orgs/"}  # no "record" key
    mock_aurora_client.get.side_effect = _mock_responses(schema)

    result = get_metadata("test-token")

    assert result == {}


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_records_missing_record_key_returns_zeros(mock_aurora_client: Any) -> None:
    schema = {"organization": "https://aurora.test/api/orgs/"}  # no "record" key
    mock_aurora_client.get.side_effect = _mock_responses(schema)

    result = fetch_records("test-token")

    assert result == {"pages": 0, "records": 0, "created": 0, "updated": 0}


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_records_skips_record_missing_id(mock_aurora_client: Any) -> None:
    schema = {"record": "https://aurora.test/api/records/"}
    page = {"results": [{"registration": 1, "status": "TO_IMPORT"}]}  # no "id"
    mock_aurora_client.get.side_effect = _mock_responses(schema, page)

    result = fetch_records("test-token")

    assert result["records"] == 0
    assert result["created"] == 0
    assert Record.objects.count() == 0


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_fetch_records_skips_existing_records(mock_aurora_client: Any) -> None:
    existing = RecordFactory(source_id=99)
    schema = {"record": "https://aurora.test/api/records/"}
    page = {
        "results": [
            {
                "id": 99,
                "registration": existing.registration,
                "timestamp": timezone.now(),
                "status": Record.STATUS_TO_IMPORT,
            }
        ]
    }
    mock_aurora_client.get.side_effect = _mock_responses(schema, page)

    result = fetch_records("test-token", overwrite=False, registration=existing.registration)

    assert result == {"pages": 1, "records": 1, "created": 0, "updated": 0}
    assert Record.objects.filter(source_id=99).count() == 1
