from unittest.mock import MagicMock

from django.core.exceptions import ValidationError
import pytest

from hope.apps.periodic_data_update.service.periodic_data_update_import_service import (
    PDUXlsxImportService,
)


def test_build_form_raises_when_flexible_attribute_not_in_dict() -> None:
    svc = PDUXlsxImportService.__new__(PDUXlsxImportService)
    svc.periodic_data_update_template = MagicMock()
    svc.periodic_data_update_template.rounds_data = [
        {"field": "nonexistent_field", "round": 1, "round_name": "Round 1"},
    ]
    svc.flexible_attributes_dict = {}

    with pytest.raises(ValidationError, match="Flexible Attribute for field nonexistent_field not found"):
        svc._build_form()
