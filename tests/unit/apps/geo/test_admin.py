from unittest.mock import Mock, patch

from django.contrib.admin import AdminSite
from django.contrib.admin.options import ModelAdmin
from django.test import Client, override_settings
from django.urls import reverse
from django_webtest import WebTest

import pytest
from django_webtest import DjangoTestApp
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from factory import fuzzy
from flaky import flaky
from webtest import Upload

from extras.test_utils.factories.account import UserFactory
from hope.apps.account.models import User
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, Country
from hope.admin.geo import AreaAdmin
from hope.apps.account.models import Partner, User
from hope.apps.geo.models import Area, AreaType


pytestmark = pytest.mark.django_db

@pytest.fixture
def superuser() -> User:
    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture(autouse=True)
def test_data() -> None:
    AreaTypeFactory.create_batch(2)
    AreaFactory.create_batch(5, area_type=fuzzy.FuzzyChoice(AreaType.objects.all()))
    Country.objects.get_or_create(
        iso_code2="AF",
        defaults={
            "name": "Afghanistan",
            "short_name": "Afghanistan",
            "iso_code3": "AFG",
            "iso_num": "004",
        },
    )

    def test_modeladmin_str(self) -> None:
        ma = ModelAdmin(Area, self.site)
        assert str(ma) == "geo.ModelAdmin"

@pytest.fixture
def app() -> DjangoTestApp:
    from django.core.cache import cache

    app_instance = DjangoTestApp()
    yield app_instance
    cache.clear()


@pytest.fixture
def admin_site() -> AdminSite:
    return AdminSite()


def test_modeladmin_str(admin_site: AdminSite) -> None:
    ma = ModelAdmin(Area, admin_site)
    assert str(ma) == "geo.ModelAdmin"


def test_login(app: DjangoTestApp, client: Client, superuser: User) -> None:
    url = reverse("admin:geo_area_changelist")
    resp = app.get(url)
    assert resp.status_int == 302, "You need to be logged in"

    client.force_login(superuser)
    app.set_cookie("sessionid", client.cookies["sessionid"].value)
    resp = app.get(url)
    assert resp.status_int == 200, "You need to be logged in and superuser"

    @flaky(max_runs=3, min_passes=1)
    def test_upload(self) -> None:
        assert AreaType.objects.count() == 2, "Two area types created"
        assert Area.objects.count() == 5, "Five area created"
        resp = self.app.get(reverse("admin:geo_area_changelist"), user=self.superuser).click("Import Areas")
        assert "Upload a csv" in resp
        form = resp.form
        form["file"] = Upload(
            "file.csv",
            b"Country,Province,District,Admin0,Adm1,Adm2\nAfghanistan,Prov1,Distr1,AF,AF99,AF9999\nAfghanistan,Prov1,Distr1,AF,AF99,AF9988\n",
            "text/csv",
        )
        resp = form.submit("Import")
        assert resp.status_int == 302, "The form is not good"
        assert AreaType.objects.count() == 4, "Two new area types created"
        assert Area.objects.count() == 8, "Two new area created"

@flaky(max_runs=3, min_passes=1)
@patch("hope.apps.geo.admin.import_areas_from_csv_task.delay")
@override_settings(POWER_QUERY_DB_ALIAS="default")
def test_upload(mock_task_delay: Mock, app: DjangoTestApp, client: Client, superuser: User) -> None:
    assert AreaType.objects.count() == 2
    assert Area.objects.count() == 5

    client.force_login(superuser)
    app.set_cookie("sessionid", client.cookies["sessionid"].value)

    resp = app.get(reverse("admin:geo_area_changelist")).click("Import Areas")
    assert "Upload a csv" in resp
    form = resp.form
    csv_content = (
        b"Country,Province,District,Admin0,Adm1,Adm2\n"
        b"Afghanistan,Prov1,Distr1,AF,AF99,AF9999\n"
        b"Afghanistan,Prov1,Distr1,AF,AF99,AF9988\n"
    )
    form["file"] = Upload(
        "file.csv",
        csv_content,
        "text/csv",
    )
    resp = form.submit("Import")
    assert resp.status_int == 302

    redirect_resp = resp.follow()
    messages = list(redirect_resp.context["messages"])
    assert len(messages) == 1
    assert "Found 3 new areas to create." in str(messages[0])
    assert "The import is running in the background." in str(messages[0])

    assert AreaType.objects.count() == 2
    assert Area.objects.count() == 5
    mock_task_delay.assert_called_once_with(csv_content.decode("utf-8-sig"))


@pytest.mark.parametrize(
    "csv_content, expected_message",
    [
        (b"Country,Province,District,Admin0,Adm1,Adm2\n", "CSV file is empty."),
        (
            b"Country,Province,District,Admin0,Adm1,Adm2\nWrongCountry,Prov1,Distr1,AF,AF99,AF9999\n",
            "Country 'WrongCountry' not found",
        ),
        (
            b"WrongHeader,Province,District,Admin0,Adm1,Adm2\nAfghanistan,Prov1,Distr1,AF,AF99,AF9999\n",
            "CSV must have a 'Country' column",
        ),
        (
            b"Country,Province,District,Admin0,Adm1\nAfghanistan,Prov1,Distr1,AF,AF99\n",
            "CSV must have an even number of columns (names and p-codes)",
        ),
        (
            b"Province,Country,District,Admin0,Adm1,Adm2\nProv1,Afghanistan,Distr1,AF,AF99,AF9999\n",
            "First column must be 'Country'",
        ),
    ],
)
@override_settings(POWER_QUERY_DB_ALIAS="default")
def test_upload_validation(
    csv_content: bytes, expected_message: str, app: DjangoTestApp, client: Client, superuser: User
) -> None:
    client.force_login(superuser)
    app.set_cookie("sessionid", client.cookies["sessionid"].value)

    resp = app.get(reverse("admin:geo_area_changelist")).click("Import Areas")
    form = resp.form
    form["file"] = Upload(
        "file.csv",
        csv_content,
        "text/csv",
    )
    resp = form.submit("Import")

    assert resp.status_int == 302
    redirect_resp = resp.follow()
    messages = list(redirect_resp.context["messages"])
    assert len(messages) == 1
    assert expected_message in str(messages[0])
