from django.contrib.admin import AdminSite
import pytest

from extras.test_utils.factories import FileTempFactory
from hope.admin.western_union_data_admin import WesternUnionDataAdmin
from hope.models import WesternUnionData, WesternUnionInvoice

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_instance() -> WesternUnionDataAdmin:
    return WesternUnionDataAdmin(WesternUnionData, AdminSite())


def test_download_link_returns_dash_when_file_is_missing(admin_instance: WesternUnionDataAdmin) -> None:
    data_file = WesternUnionData.objects.create(name="AD-missing.zip")

    assert admin_instance.download_link(data_file) == "-"


def test_download_link_returns_anchor_when_file_exists(admin_instance: WesternUnionDataAdmin) -> None:
    file_temp = FileTempFactory()
    data_file = WesternUnionData.objects.create(name="AD-file.zip", file=file_temp)

    html = str(admin_instance.download_link(data_file))

    assert 'target="_blank"' in html
    assert "Download" in html
    assert file_temp.file.url in html


def test_matched_invoices_list_returns_comma_separated_names(admin_instance: WesternUnionDataAdmin) -> None:
    data_file = WesternUnionData.objects.create(name="AD-matched.zip")
    WesternUnionInvoice.objects.create(name="QCF-1.zip", matched_data=data_file)
    WesternUnionInvoice.objects.create(name="QCF-2.zip", matched_data=data_file)

    assert admin_instance.matched_invoices_list(data_file) == "QCF-1.zip, QCF-2.zip"
