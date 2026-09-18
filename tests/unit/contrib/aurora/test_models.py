import json

import pytest

from extras.test_utils.factories import RecordFactory
from hope.contrib.aurora.models import Record

pytestmark = pytest.mark.django_db


@pytest.fixture
def record_with_storage() -> Record:
    return RecordFactory(storage=json.dumps({"household": [{"size": 3}]}).encode(), files=None)


@pytest.fixture
def record_with_files_and_fields() -> Record:
    return RecordFactory(
        storage=None,
        files=json.dumps({"household": {"photo": "base64-data"}}).encode(),
        fields={"household": {"size": 3}},
    )


@pytest.fixture
def record_without_files() -> Record:
    return RecordFactory(storage=None, files=None, fields={"household": {"size": 3}})


def test_get_data_decodes_storage_read_from_db(record_with_storage: Record) -> None:
    record = Record.objects.get(pk=record_with_storage.pk)

    data = record.get_data()

    assert data == {"household": [{"size": 3}]}


def test_get_data_merges_files_read_from_db_with_fields(record_with_files_and_fields: Record) -> None:
    record = Record.objects.get(pk=record_with_files_and_fields.pk)

    data = record.get_data()

    assert data == {"household": {"photo": "base64-data", "size": 3}}


def test_get_data_returns_fields_when_files_empty(record_without_files: Record) -> None:
    record = Record.objects.get(pk=record_without_files.pk)

    data = record.get_data()

    assert data == {"household": {"size": 3}}
