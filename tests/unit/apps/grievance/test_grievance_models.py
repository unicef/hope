"""Tests for GrievanceTicket model properties covered by mypy fixes."""

from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    GrievanceTicketFactory,
    UserFactory,
)
from hope.apps.grievance.models import GrievanceTicket

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def user(business_area: Any) -> Any:
    return UserFactory()


@pytest.fixture
def ticket_grievance_complaint_no_issue_type(business_area: Any, user: Any) -> Any:
    # CATEGORY_GRIEVANCE_COMPLAINT maps to a plain string in TICKET_DETAILS_NAME_MAPPING,
    # so issue_type=None is valid for that category.
    # We use CATEGORY_POSITIVE_FEEDBACK which is a plain string mapping and allows issue_type=None.
    return GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        issue_type=None,
        business_area=business_area,
        created_by=user,
    )


@pytest.fixture
def ticket_data_change_no_issue_type_unsaved(business_area: Any, user: Any) -> Any:
    # CATEGORY_DATA_CHANGE uses a dict mapping — issue_type=None should cause ticket_details to return None.
    # We build without saving because save() validates issue_type.
    return GrievanceTicket(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=None,
        business_area=business_area,
        created_by=user,
        status=GrievanceTicket.STATUS_NEW,
        description="test",
    )


def test_ticket_details_returns_none_when_category_not_in_mapping(
    ticket_grievance_complaint_no_issue_type: Any,
) -> None:
    # CATEGORY_POSITIVE_FEEDBACK maps to a plain string, not a dict, so the attribute
    # "positive_feedback_ticket_details" doesn't exist on this bare ticket — getattr returns None.
    result = ticket_grievance_complaint_no_issue_type.ticket_details
    assert result is None


def test_ticket_details_returns_none_when_dict_mapping_and_issue_type_is_none(
    ticket_data_change_no_issue_type_unsaved: Any,
) -> None:
    # When the category uses a dict mapping and issue_type is None, ticket_details must return None.
    result = ticket_data_change_no_issue_type_unsaved.ticket_details
    assert result is None


def test_get_issue_type_returns_empty_string_when_issue_type_is_none(
    ticket_grievance_complaint_no_issue_type: Any,
) -> None:
    result = ticket_grievance_complaint_no_issue_type.get_issue_type()
    assert result == ""


def test_get_issue_type_returns_label_when_issue_type_is_set(business_area: Any, user: Any) -> None:
    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        business_area=business_area,
        created_by=user,
    )
    result = ticket.get_issue_type()
    assert result != ""
    assert "Individual" in str(result)
