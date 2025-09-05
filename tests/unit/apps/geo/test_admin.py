from unittest.mock import Mock, patch

from django.contrib.admin import AdminSite
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.models import Permission
from django.test import Client, RequestFactory, override_settings
from django.urls import reverse
from django_webtest import DjangoTestApp
from factory import fuzzy
from flaky import flaky
import pytest
from webtest import Upload

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from hope.admin.geo import AreaAdmin
from hope.apps.account.models import User
from hope.apps.geo.models import Area, AreaType, Country

pytestmark = pytest.mark.django_db


@pytest.fixture
def superuser() -> User:
    user = UserFactory(is_superuser=True, is_staff=True, is_active=True, email="test123@mail.com")
    perm = Permission.objects.get(codename="import_areas", content_type__app_label="geo")
    user.user_permissions.add(perm)
    return user


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


@pytest.fixture
def app() -> DjangoTestApp:
    from django.core.cache import cache

    app_instance = DjangoTestApp()
    yield app_instance
    cache.clear()


@pytest.fixture
def site() -> AdminSite:
    return AdminSite()


@pytest.fixture
def rf() -> RequestFactory:
    return RequestFactory()


def test_modeladmin_str(site: AdminSite) -> None:
    ma = ModelAdmin(Area, site)
    assert str(ma) == "geo.ModelAdmin"


def test_login(app: DjangoTestApp, superuser: User, rf: RequestFactory, site: AdminSite) -> None:
    url = reverse("admin:geo_area_changelist")
    resp = app.get(url)
    assert resp.status_int == 302, "You need to be logged in"

    request = rf.get(reverse("admin:geo_area_changelist"))
    request.user = superuser

    resp = site.admin_view(AreaAdmin(Area, site).changelist_view)(request)
    assert resp.status_code == 200, "You need to be logged in and superuser"


@flaky(max_runs=3, min_passes=1)
@patch("hope.apps.geo.celery_tasks.import_areas_from_csv_task.delay")
@override_settings(POWER_QUERY_DB_ALIAS="default")
def test_upload(mock_task_delay: Mock, rf: RequestFactory, site: AdminSite, superuser):
    assert AreaType.objects.count() == 2
    assert Area.objects.count() == 5

    # get
    request = rf.get(reverse("admin:geo_area_changelist"))
    request.user = superuser
    changelist_view = AreaAdmin(Area, site).changelist_view
    site.admin_view(changelist_view)(request)

    csv_content = (
        b"Country,Province,District,Admin0,Adm1,Adm2\n"
        b"Afghanistan,Prov1,Distr1,AF,AF99,AF9999\n"
        b"Afghanistan,Prov1,Distr1,AF,AF99,AF9988\n"
    )
    file_upload = Upload("file.csv", csv_content, "text/csv")
    # post
    request = rf.post(
        reverse("admin:geo_area_changelist"),
        {"file": file_upload},
    )
    request.user = superuser
    site.admin_view(changelist_view)(request)
    # FIXME!!!
    # assert resp.status_code == 302
    # mock_task_delay.assert_called_once_with(csv_content.decode("utf-8-sig"))


@pytest.mark.parametrize(
    ("csv_content", "expected_message"),
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

    # resp = app.get(reverse("admin:geo_area_changelist")).click("Import Areas") # fix login
    # form = resp.form
    # form["file"] = Upload(
    #     "file.csv",
    #     csv_content,
    #     "text/csv",
    # )
    # resp = form.submit("Import")
    # FIXME
    # assert resp.status_int == 302
    # redirect_resp = resp.follow()
    # messages = list(redirect_resp.context["messages"])
    # assert len(messages) == 1
    # assert expected_message in str(messages[0])
