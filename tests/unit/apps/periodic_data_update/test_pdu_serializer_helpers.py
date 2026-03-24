from unittest.mock import MagicMock

import pytest

from hope.apps.periodic_data_update.api.serializers import PDUOnlineEditSaveDataSerializer


@pytest.fixture
def mock_serializer():
    mock_self = MagicMock(spec=PDUOnlineEditSaveDataSerializer)
    mock_self._check_field_editability = PDUOnlineEditSaveDataSerializer._check_field_editability.__get__(mock_self)
    return mock_self


def test_check_field_editability_editable_none_value(mock_serializer):
    field_data = {
        "value": None,
        "subtype": "STRING",
        "is_editable": True,
        "round_number": 1,
    }
    existing_pdu_fields = {
        "test_field": {"value": "old_value"},
    }

    result = mock_serializer._check_field_editability("test_field", field_data, existing_pdu_fields)

    assert result is False


def test_check_field_editability_non_editable_unchanged(mock_serializer):
    field_data = {
        "value": "existing_value",
        "subtype": "STRING",
        "is_editable": False,
        "round_number": 1,
    }
    existing_pdu_fields = {
        "test_field": {"value": "existing_value"},
    }

    result = mock_serializer._check_field_editability("test_field", field_data, existing_pdu_fields)

    assert result is False


def test_check_field_editability_editable_with_value(mock_serializer):
    field_data = {
        "value": "hello",
        "subtype": "STRING",
        "is_editable": True,
        "round_number": 1,
    }
    existing_pdu_fields = {
        "test_field": {"value": "old_value"},
    }

    result = mock_serializer._check_field_editability("test_field", field_data, existing_pdu_fields)

    assert result is True
