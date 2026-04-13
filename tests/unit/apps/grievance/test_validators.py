from unittest.mock import MagicMock, patch

from hope.apps.grievance.validators import validate_grievance_documents_size


@patch("hope.apps.grievance.validators.GrievanceDocument")
def test_validate_grievance_documents_size_is_updated_branch(mock_grievance_document: MagicMock) -> None:
    mock_qs = MagicMock()
    mock_grievance_document.objects.filter.return_value = mock_qs
    mock_qs.exclude.return_value.values_list.return_value = [100, 200]

    file_mock = MagicMock()
    file_mock.size = 50

    validate_grievance_documents_size(
        ticket_id="some-ticket-id",
        new_documents=[{"id": "x", "file": file_mock}],
        is_updated=True,
    )

    mock_grievance_document.objects.filter.assert_called_once_with(grievance_ticket_id="some-ticket-id")
    mock_qs.exclude.assert_called_once_with(id__in=["x"])
