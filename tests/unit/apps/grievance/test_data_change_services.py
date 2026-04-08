from unittest.mock import MagicMock

import pytest

from hope.apps.grievance.services.data_change_services import InvalidIssueTypeError, get_service


def test_get_service_raises_when_issue_type_is_none():
    ticket = MagicMock()
    ticket.issue_type = None

    with pytest.raises(InvalidIssueTypeError, match="Issue type is not set"):
        get_service(ticket, {})
