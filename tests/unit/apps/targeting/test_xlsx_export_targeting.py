from unittest.mock import MagicMock, patch

from hope.apps.targeting.services.xlsx_export_targeting_service import XlsxExportTargetingService


def test_add_individuals_rows_calls_add_individual_row_for_each_individual() -> None:
    service = XlsxExportTargetingService.__new__(XlsxExportTargetingService)
    mock_individual = MagicMock()
    service.individuals = [mock_individual]

    with patch.object(service, "_add_individual_row") as mock_add_row:
        service._add_individuals_rows()

    mock_add_row.assert_called_once_with(mock_individual)
