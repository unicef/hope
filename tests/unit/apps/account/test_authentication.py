"""Tests for account authentication pipeline functions."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from social_core.exceptions import InvalidEmail

from extras.test_utils.factories import (
    BusinessAreaFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.account.authentication import (
    create_user,
    require_email,
    social_details,
    user_details,
)
from hope.models import ACTIVE, BusinessArea, Role, RoleAssignment, User

pytestmark = pytest.mark.django_db


# --- Fixtures ---


@pytest.fixture
def user(db: Any) -> User:
    return UserFactory(email="test@example.com", first_name="John", last_name="Doe")


@pytest.fixture
def business_area(db: Any) -> BusinessArea:
    return BusinessAreaFactory(code="AFG", slug="afghanistan", name="Afghanistan")


@pytest.fixture
def basic_user_role(db: Any) -> Role:
    return RoleFactory(name="Basic User")


@pytest.fixture
def mock_backend() -> MagicMock:
    backend = MagicMock()
    backend.user_data.return_value = {}
    return backend


@pytest.fixture
def mock_strategy() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_ms_graph() -> Any:
    with patch("hope.apps.account.authentication.MicrosoftGraphAPI") as mock_class:
        mock_instance = MagicMock()
        mock_instance.get_user_data.return_value = {}
        mock_class.return_value = mock_instance
        yield mock_instance


# --- social_details tests ---


@patch("hope.apps.account.authentication.social_auth.social_details")
def test_social_details_returns_email_from_original_details_when_present(
    mock_social_auth_details: MagicMock, mock_backend: MagicMock
) -> None:
    mock_social_auth_details.return_value = {"details": {"email": "original@example.com"}}
    response = {}

    result = social_details(mock_backend, {}, response)

    assert result["details"]["email"] == "original@example.com"


@patch("hope.apps.account.authentication.social_auth.social_details")
def test_social_details_fetches_email_from_backend_user_data_when_missing(
    mock_social_auth_details: MagicMock, mock_backend: MagicMock
) -> None:
    mock_social_auth_details.return_value = {"details": {"email": None}}
    mock_backend.user_data.return_value = {"email": "backend@example.com"}
    response = {}

    result = social_details(mock_backend, {}, response)

    assert result["details"]["email"] == "backend@example.com"
    mock_backend.user_data.assert_called()


@patch("hope.apps.account.authentication.social_auth.social_details")
def test_social_details_fetches_email_from_backend_when_email_is_empty_string(
    mock_social_auth_details: MagicMock, mock_backend: MagicMock
) -> None:
    mock_social_auth_details.return_value = {"details": {"email": ""}}
    mock_backend.user_data.return_value = {"email": "fallback@example.com"}
    response = {}

    result = social_details(mock_backend, {}, response)

    assert result["details"]["email"] == "fallback@example.com"


@patch("hope.apps.account.authentication.social_auth.social_details")
def test_social_details_fetches_email_from_signin_names_when_email_key_missing(
    mock_social_auth_details: MagicMock, mock_backend: MagicMock
) -> None:
    mock_social_auth_details.return_value = {"details": {}}
    mock_backend.user_data.return_value = {"signInNames.emailAddress": "signin@example.com"}
    response = {}

    result = social_details(mock_backend, {}, response)

    assert result["details"]["email"] == "signin@example.com"


@patch("hope.apps.account.authentication.social_auth.social_details")
def test_social_details_keeps_email_none_when_user_data_empty(
    mock_social_auth_details: MagicMock, mock_backend: MagicMock
) -> None:
    mock_social_auth_details.return_value = {"details": {}}
    mock_backend.user_data.return_value = {}
    response = {}

    result = social_details(mock_backend, {}, response)

    assert result["details"]["email"] is None


@patch("hope.apps.account.authentication.social_auth.social_details")
def test_social_details_adds_idp_from_response(
    mock_social_auth_details: MagicMock, mock_backend: MagicMock
) -> None:
    mock_social_auth_details.return_value = {"details": {"email": "test@example.com"}}
    response = {"idp": "azure-ad"}

    result = social_details(mock_backend, {}, response)

    assert result["details"]["idp"] == "azure-ad"


@patch("hope.apps.account.authentication.social_auth.social_details")
def test_social_details_adds_empty_idp_when_missing_in_response(
    mock_social_auth_details: MagicMock, mock_backend: MagicMock
) -> None:
    mock_social_auth_details.return_value = {"details": {"email": "test@example.com"}}
    response = {}

    result = social_details(mock_backend, {}, response)

    assert result["details"]["idp"] == ""


# --- user_details tests ---


@patch("hope.apps.account.authentication.social_core_user.user_details")
def test_user_details_updates_username_to_email_when_user_exists(
    mock_social_core_user_details: MagicMock, user: User, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    details = {"email": "new@example.com"}
    mock_social_core_user_details.return_value = None

    user_details(mock_strategy, details, mock_backend, user)

    user.refresh_from_db()
    assert user.username == "new@example.com"


@patch("hope.apps.account.authentication.social_core_user.user_details")
def test_user_details_sets_status_to_active_when_user_exists(
    mock_social_core_user_details: MagicMock, user: User, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    user.status = "INACTIVE"
    user.save()
    details = {"email": "test@example.com"}
    mock_social_core_user_details.return_value = None

    user_details(mock_strategy, details, mock_backend, user)

    user.refresh_from_db()
    assert user.status == ACTIVE


@patch("hope.apps.account.authentication.social_core_user.user_details")
def test_user_details_preserves_first_name_when_details_empty(
    mock_social_core_user_details: MagicMock, user: User, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    details = {"email": "test@example.com", "first_name": ""}
    mock_social_core_user_details.return_value = None

    user_details(mock_strategy, details, mock_backend, user)

    assert details["first_name"] == "John"


@patch("hope.apps.account.authentication.social_core_user.user_details")
def test_user_details_preserves_last_name_when_details_empty(
    mock_social_core_user_details: MagicMock, user: User, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    details = {"email": "test@example.com", "last_name": ""}
    mock_social_core_user_details.return_value = None

    user_details(mock_strategy, details, mock_backend, user)

    assert details["last_name"] == "Doe"


@patch("hope.apps.account.authentication.social_core_user.user_details")
def test_user_details_uses_new_first_name_when_provided_in_details(
    mock_social_core_user_details: MagicMock, user: User, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    details = {"email": "test@example.com", "first_name": "Jane"}
    mock_social_core_user_details.return_value = None

    user_details(mock_strategy, details, mock_backend, user)

    assert details["first_name"] == "Jane"


@patch("hope.apps.account.authentication.social_core_user.user_details")
def test_user_details_uses_new_last_name_when_provided_in_details(
    mock_social_core_user_details: MagicMock, user: User, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    details = {"email": "test@example.com", "last_name": "Smith"}
    mock_social_core_user_details.return_value = None

    user_details(mock_strategy, details, mock_backend, user)

    assert details["last_name"] == "Smith"


@patch("hope.apps.account.authentication.social_core_user.user_details")
def test_user_details_skips_update_when_user_is_none(
    mock_social_core_user_details: MagicMock, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    details = {"email": "test@example.com"}
    mock_social_core_user_details.return_value = None

    result = user_details(mock_strategy, details, mock_backend, None)

    assert result is None
    mock_social_core_user_details.assert_called_once_with(mock_strategy, details, mock_backend, None)


@patch("hope.apps.account.authentication.social_core_user.user_details")
def test_user_details_calls_social_core_user_details(
    mock_social_core_user_details: MagicMock, user: User, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    details = {"email": "test@example.com"}
    mock_social_core_user_details.return_value = {"result": "value"}

    result = user_details(mock_strategy, details, mock_backend, user)

    mock_social_core_user_details.assert_called_once()
    assert result == {"result": "value"}


# --- require_email tests ---


def test_require_email_returns_none_when_user_has_email(user: User, mock_strategy: MagicMock) -> None:
    result = require_email(mock_strategy, {}, user=user, is_new=False)

    assert result is None


def test_require_email_returns_none_when_user_none_and_not_new(mock_strategy: MagicMock) -> None:
    result = require_email(mock_strategy, {}, user=None, is_new=False)

    assert result is None


def test_require_email_returns_none_when_new_user_with_email_in_details(mock_strategy: MagicMock) -> None:
    details = {"email": "new@example.com"}

    result = require_email(mock_strategy, details, user=None, is_new=True)

    assert result is None


def test_require_email_raises_invalid_email_when_new_user_without_email(mock_strategy: MagicMock) -> None:
    with pytest.raises(InvalidEmail):
        require_email(mock_strategy, {}, user=None, is_new=True)


def test_require_email_raises_invalid_email_when_new_user_with_empty_email_string(mock_strategy: MagicMock) -> None:
    with pytest.raises(InvalidEmail):
        require_email(mock_strategy, {"email": ""}, user=None, is_new=True)


# --- create_user tests ---


def test_create_user_returns_is_new_false_when_user_exists(
    user: User, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    result = create_user(mock_strategy, {}, mock_backend, user)

    assert result == {"is_new": False}


def test_create_user_creates_user_with_email_and_names(
    mock_ms_graph: MagicMock, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    details = {
        "email": "newuser@example.com",
        "first_name": "New",
        "last_name": "User",
    }

    result = create_user(mock_strategy, details, mock_backend, None)

    assert result["is_new"] is True
    created_user = result["user"]
    assert created_user.email == "newuser@example.com"
    assert created_user.username == "newuser@example.com"
    assert created_user.first_name == "New"
    assert created_user.last_name == "User"


def test_create_user_sets_status_to_active(
    mock_ms_graph: MagicMock, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    details = {"email": "newuser@example.com", "first_name": "New", "last_name": "User"}

    result = create_user(mock_strategy, details, mock_backend, None)

    assert result["user"].status == ACTIVE


def test_create_user_sets_unusable_password(
    mock_ms_graph: MagicMock, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    details = {"email": "newuser@example.com", "first_name": "New", "last_name": "User"}

    result = create_user(mock_strategy, details, mock_backend, None)

    assert result["user"].has_usable_password() is False


def test_create_user_fetches_and_sets_job_title_from_ms_graph(
    mock_ms_graph: MagicMock, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    mock_ms_graph.get_user_data.return_value = {"jobTitle": "Software Engineer"}
    details = {"email": "newuser@example.com", "first_name": "New", "last_name": "User"}

    result = create_user(mock_strategy, details, mock_backend, None)

    assert result["user"].job_title == "Software Engineer"


def test_create_user_skips_job_title_when_none_in_ms_graph(
    mock_ms_graph: MagicMock, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    mock_ms_graph.get_user_data.return_value = {"jobTitle": None}
    details = {"email": "newuser@example.com", "first_name": "New", "last_name": "User"}

    result = create_user(mock_strategy, details, mock_backend, None)

    assert result["user"].job_title == ""


def test_create_user_creates_role_assignment_when_business_area_code_exists(
    mock_ms_graph: MagicMock,
    mock_strategy: MagicMock,
    mock_backend: MagicMock,
    business_area: BusinessArea,
    basic_user_role: Role,
) -> None:
    mock_ms_graph.get_user_data.return_value = {
        "extension_f4805b4021f643d0aa596e1367d432f1_unicefBusinessAreaCode": "AFG"
    }
    details = {"email": "newuser@example.com", "first_name": "New", "last_name": "User"}

    result = create_user(mock_strategy, details, mock_backend, None)

    role_assignment = RoleAssignment.objects.get(user=result["user"], business_area=business_area)
    assert role_assignment.role == basic_user_role
    assert role_assignment.business_area == business_area


def test_create_user_raises_when_business_area_code_not_found_in_db(
    mock_ms_graph: MagicMock,
    mock_strategy: MagicMock,
    mock_backend: MagicMock,
    basic_user_role: Role,
) -> None:
    mock_ms_graph.get_user_data.return_value = {
        "extension_f4805b4021f643d0aa596e1367d432f1_unicefBusinessAreaCode": "NONEXISTENT"
    }
    details = {"email": "newuser@example.com", "first_name": "New", "last_name": "User"}

    with pytest.raises(BusinessArea.DoesNotExist):
        create_user(mock_strategy, details, mock_backend, None)


def test_create_user_skips_role_assignment_when_no_business_area_code(
    mock_ms_graph: MagicMock, mock_strategy: MagicMock, mock_backend: MagicMock
) -> None:
    details = {"email": "newuser@example.com", "first_name": "New", "last_name": "User"}

    result = create_user(mock_strategy, details, mock_backend, None)

    assert not RoleAssignment.objects.filter(user=result["user"]).exists()
