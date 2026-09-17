from typing import TYPE_CHECKING
from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from django.urls import reverse
import pytest
import responses

from extras.test_utils.factories import UserFactory
from hope.admin.sanction_list_uploaded_xlsx_file import UploadedXLSXFileAdmin
from hope.models import UploadedXLSXFile

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from responses import RequestsMock

    from hope.models import SanctionList, User


@pytest.fixture
def staff_user() -> "User":
    return UserFactory.create(is_staff=True)


def test_uploaded_xlsx_get_actions(staff_user: "User") -> None:
    request = HttpRequest()
    request.user = staff_user

    actions = UploadedXLSXFileAdmin(UploadedXLSXFile, AdminSite()).get_actions(request)
    assert isinstance(actions, dict)


def test_uploaded_xlsx_get_actions_with_action_location(staff_user: "User") -> None:
    request = HttpRequest()
    request.user = staff_user

    admin = UploadedXLSXFileAdmin(UploadedXLSXFile, AdminSite())
    with patch("django.contrib.admin.ModelAdmin.get_actions", return_value={}) as mock_get:
        admin.get_actions(request, action_location="changelist")
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1].get("action_location") == "changelist"


def test_sanction_list_refresh(
    django_app: "DjangoTestApp",
    admin_user: "User",
    sanction_list: "SanctionList",
    eu_file: str,
    mocked_responses: "RequestsMock",
) -> None:
    mocked_responses.add(responses.GET, "http://example.com/sl.xml", body=eu_file, status=200)
    url = reverse("admin:sanction_list_sanctionlist_change", args=(sanction_list.id,))
    res = django_app.get(url, user=admin_user)
    res = res.click("Refresh")
    assert res.status_code == 302


def test_sanction_list_empty(
    django_app: "DjangoTestApp",
    admin_user: "User",
    sanction_list: "SanctionList",
    mocked_responses: "RequestsMock",
) -> None:
    url = reverse("admin:sanction_list_sanctionlist_change", args=(sanction_list.id,))
    res = django_app.get(url, user=admin_user)
    res = res.click("Empty")
    assert res.status_code == 200
    form = res.forms[1]
    res = form.submit()
    assert res.status_code == 302
