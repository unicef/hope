from django.contrib.admin import AdminSite
import pytest

from extras.test_utils.factories import FileTempFactory
from hope.admin.file_temp import FileTempAdmin
from hope.models import FileTemp

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_instance() -> FileTempAdmin:
    return FileTempAdmin(FileTemp, AdminSite())


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
