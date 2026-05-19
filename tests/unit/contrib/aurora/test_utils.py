from typing import Any
from unittest.mock import MagicMock

from constance.test import override_config
from coreapi.exceptions import NoCodecAvailable
from django.utils import timezone
import pytest

from extras.test_utils.factories import RecordFactory
from hope.contrib.aurora.models import Organization, Project, Record, Registration
from hope.contrib.aurora.utils import fetch_metadata, fetch_records, get_metadata

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def mock_aurora_client(mocker: Any) -> Any:
    client_class = mocker.patch("hope.contrib.aurora.utils.coreapi.Client")
    client_instance = MagicMock()
    client_class.return_value = client_instance
    return client_instance


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
    mock_aurora_client.get.side_effect = [
        schema,
        orgs_page,
        projects_page,
        registrations_list,
        metadata_dict,
    ]

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
    mock_aurora_client.get.side_effect = [
        schema,
        orgs_page,
        projects_page,
        registrations_list,
        NoCodecAvailable("unsupported codec"),
    ]
    mock_logger = mocker.patch("hope.contrib.aurora.utils.logger")

    fetch_metadata("test-token")

    registration = Registration.objects.get(source_id=200)
    assert registration.metadata == {}
    mock_logger.exception.assert_called_once()


@override_config(AURORA_SERVER="https://aurora.test/api/")
def test_get_metadata_returns_record_metadata(mock_aurora_client: Any) -> None:
    schema = {"record": "https://aurora.test/api/records/"}
    metadata_dict = {"definition": [1, 2, 3]}
    mock_aurora_client.get.side_effect = [schema, metadata_dict]

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
    mock_aurora_client.get.side_effect = [schema, page]

    result = fetch_records("test-token", overwrite=False, registration=7)

    assert result == {"pages": 1, "records": 1, "created": 1, "updated": 0}
    record = Record.objects.get(source_id=42)
    assert record.registration == 7
    assert record.data == {"foo": "bar"}
    fetched_url = mock_aurora_client.get.call_args_list[1].args[0]
    assert fetched_url == "https://aurora.test/api/records/?registration=7"


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
    mock_aurora_client.get.side_effect = [schema, page]

    result = fetch_records("test-token", overwrite=False, registration=existing.registration)

    assert result == {"pages": 1, "records": 1, "created": 0, "updated": 0}
    assert Record.objects.filter(source_id=99).count() == 1
