from django.contrib.admin import AdminSite
from django.http import HttpRequest
import pytest

from extras.test_utils.factories import FileTempFactory, UserFactory
from hope.admin.file_temp import FileTempAdmin
from hope.models import FileTemp

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_instance() -> FileTempAdmin:
    return FileTempAdmin(FileTemp, AdminSite())


@pytest.fixture
def root_request() -> HttpRequest:
    request = HttpRequest()
    request.user = UserFactory(is_superuser=True)
    return request


@pytest.fixture
def non_root_request() -> HttpRequest:
    request = HttpRequest()
    request.user = UserFactory(is_superuser=False, is_staff=True)
    return request


def test_download_link_returns_dash_when_file_is_missing(admin_instance: FileTempAdmin) -> None:
    file_temp = FileTempFactory()
    file_temp.file = ""

    assert admin_instance.download_link(file_temp) == "-"


def test_download_link_returns_anchor_when_file_exists(admin_instance: FileTempAdmin) -> None:
    file_temp = FileTempFactory()

    html = str(admin_instance.download_link(file_temp))

    assert 'target="_blank"' in html
    assert "Download" in html
    assert file_temp.file.url in html


def test_non_root_cannot_see_encrypted_passwords(admin_instance: FileTempAdmin, non_root_request: HttpRequest) -> None:
    assert admin_instance.get_exclude(non_root_request) == ("password", "xlsx_password")
    assert admin_instance.get_readonly_fields(non_root_request) == ("download_link",)


def test_root_can_see_encrypted_passwords(
    admin_instance: FileTempAdmin, root_request: HttpRequest, enable_is_root
) -> None:
    assert admin_instance.get_exclude(root_request) is None
    assert admin_instance.get_readonly_fields(root_request) == ("download_link", "password", "xlsx_password")
