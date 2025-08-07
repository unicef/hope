from pathlib import Path
from typing import TYPE_CHECKING

from django.urls import reverse

import pytest
from webtest import Upload

from hope.apps.sanction_list.models import UploadedXLSXFile

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp

    from hope.apps.account.models import User
    from hope.apps.sanction_list.models import SanctionList


@pytest.fixture
def sample_file() -> bytes:
    return (Path(__file__).parent / "test_files" / "TestSanctionList.xlsx").read_bytes()


def test_upload(
    django_app: "DjangoTestApp", admin_user: "User", sample_file: bytes, sanction_list: "SanctionList"
) -> None:
    url = reverse("sanction:upload")
    res = django_app.get(url, user=admin_user)
    res.forms["upload-form"]["file"] = Upload("sample.xls", sample_file, content_type="application/vnd.ms-excel")
    res.forms["upload-form"]["selected_lists"] = sanction_list.pk
    res = res.forms["upload-form"].submit()
    assert res.status_code == 302
    assert UploadedXLSXFile.objects.filter(associated_email=admin_user.email).exists()


def test_download_sanction_template(django_app: "DjangoTestApp", admin_user: "User", sample_file: bytes) -> None:
    url = reverse("sanction:download_sanction_template")
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 200
