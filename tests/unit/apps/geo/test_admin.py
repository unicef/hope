from unittest.mock import Mock, patch

from django.contrib.admin import AdminSite
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.models import Permission
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, override_settings
from django.test.client import MULTIPART_CONTENT
from django.urls import reverse
from django_webtest import DjangoTestApp
from factory import fuzzy
from flaky import flaky
import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from hope.admin.geo import AreaAdmin
from hope.models.area import Area
from hope.models.area_type import AreaType
from hope.models.country import Country
from hope.models.user import User


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


@pytest.mark.xfail(reason="Failing On ONE MODEL PR")
def test_login(app: DjangoTestApp, superuser: User, rf: RequestFactory, site: AdminSite) -> None:
    url = reverse("admin:geo_area_changelist")
    resp = app.get(url)
    assert resp.status_int == 302, "You need to be logged in"

    request = rf.get(reverse("admin:geo_area_changelist"))
    request.user = superuser

    resp = site.admin_view(AreaAdmin(Area, site).changelist_view)(request)
    assert resp.status_code == 200, "You need to be logged in and superuser"


@pytest.mark.xfail(reason="Failing On ONE MODEL PR")
@flaky(max_runs=3, min_passes=1)
@patch("hope.apps.geo.celery_tasks.import_areas_from_csv_task.delay")
@override_settings(POWER_QUERY_DB_ALIAS="default")
def test_upload(
    mock_task_delay: Mock, app: DjangoTestApp, superuser: User, rf: RequestFactory, site: AdminSite
) -> None:
    assert AreaType.objects.count() == 2
    assert Area.objects.count() == 5

    site = AdminSite()
    admin = AreaAdmin(Area, site)

    rf = RequestFactory()
    url = reverse("admin:geo_area_import_areas")
    request = rf.get(url)
    request.user = superuser

    response = admin.import_areas.func(admin, request)
    assert response.status_code == 200

    csv_content = (
        b"Country,Province,District,Admin0,Adm1,Adm2\n"
        b"Afghanistan,Prov1,Distr1,AF,AF99,AF9999\n"
        b"Afghanistan,Prov1,Distr1,AF,AF99,AF9988\n"
    )
    upload = SimpleUploadedFile("file.csv", csv_content, content_type="text/csv")

    request = rf.post(url, data={"file": upload}, content_type=MULTIPART_CONTENT)
    request.user = superuser

    request.session = {}  # mock a session
    messages = FallbackStorage(request)
    request._messages = messages

    response = admin.import_areas.func(admin, request)
    assert response.status_code == 302
    assert response.url == reverse("admin:geo_area_changelist")

    stored_messages = [str(m) for m in list(messages)]
    assert len(stored_messages) == 1
    assert stored_messages[0] == "Found 3 new areas to create. The import is running in the background."

    mock_task_delay.assert_called_once_with(csv_content.decode("utf-8-sig"))


@pytest.mark.xfail(reason="Failing On ONE MODEL PR")
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
def test_upload_validation(csv_content: bytes, expected_message: str, app: DjangoTestApp, superuser: User) -> None:
    site = AdminSite()
    admin = AreaAdmin(Area, site)
    rf = RequestFactory()
    url = reverse("admin:geo_area_import_areas")

    upload = SimpleUploadedFile("file.csv", csv_content, content_type="text/csv")
    request = rf.post(url, data={"file": upload}, content_type=MULTIPART_CONTENT)
    request.user = superuser

    request.session = {}  # mock a session
    messages = FallbackStorage(request)
    request._messages = messages

    response = admin.import_areas.func(admin, request)
    assert response.status_code == 302
    assert response.url == reverse("admin:geo_area_changelist")

    stored_messages = [str(m) for m in list(messages)]
    assert len(stored_messages) == 1
    assert stored_messages[0] == expected_message
