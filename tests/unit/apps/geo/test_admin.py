"""Tests for Area admin import functionality."""

from unittest.mock import Mock, patch

from django.contrib.admin import AdminSite
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, override_settings
from django.test.client import MULTIPART_CONTENT
from django.urls import reverse
from django_webtest import DjangoTestApp
from flaky import flaky
import pytest

from extras.test_utils.factories import AreaFactory, AreaTypeFactory, CountryFactory, UserFactory
from hope.admin.geo import AreaAdmin
from hope.models import Area, AreaType, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def superuser() -> User:
    user = UserFactory(
        is_superuser=True,
        is_staff=True,
        is_active=True,
        email="test123@mail.com",
    )

    content_type, _ = ContentType.objects.get_or_create(
        app_label="geo",
        model="area",
    )
    permission, _ = Permission.objects.get_or_create(
        codename="import_areas",
        content_type=content_type,
    )
    user.user_permissions.add(permission)

    return user


@pytest.fixture
def geo_test_data() -> None:
    AreaTypeFactory.create_batch(2)
    AreaFactory.create_batch(
        2,
        area_type=AreaType.objects.first(),
    )
    AreaFactory.create_batch(
        3,
        area_type=AreaType.objects.last(),
    )
    CountryFactory(name="Afghanistan", short_name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="1234")


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


@pytest.fixture
def area_admin(site: AdminSite) -> AreaAdmin:
    return AreaAdmin(Area, site)


@pytest.fixture
def messages_request(rf: RequestFactory, superuser: User):
    def _factory(url: str, upload: SimpleUploadedFile):
        request = rf.post(url, data={"file": upload}, content_type=MULTIPART_CONTENT)
        request.user = superuser
        request.session = {}
        messages = FallbackStorage(request)
        request._messages = messages
        return request, messages

    return _factory


def test_modeladmin_str(site: AdminSite) -> None:
    model_admin = ModelAdmin(Area, site)
    assert str(model_admin) == "geo.ModelAdmin"


def test_admin_requires_login(app: DjangoTestApp) -> None:
    url = reverse("admin:geo_area_changelist")
    response = app.get(url)

    assert response.status_int == 302


def test_admin_changelist_view_accessible(
    rf: RequestFactory,
    site: AdminSite,
    superuser: User,
) -> None:
    request = rf.get(reverse("admin:geo_area_changelist"))
    request.user = superuser

    response = site.admin_view(AreaAdmin(Area, site).changelist_view)(request)

    assert response.status_code == 200


@flaky(max_runs=3, min_passes=1)
@patch("hope.apps.geo.celery_tasks.import_areas_from_csv_task.delay")
@override_settings(POWER_QUERY_DB_ALIAS="default")
def test_upload_triggers_background_task(
    mock_task_delay: Mock,
    area_admin: AreaAdmin,
    rf: RequestFactory,
    superuser: User,
    geo_test_data,
) -> None:
    assert AreaType.objects.count() == 2
    assert Area.objects.count() == 5

    url = reverse("admin:geo_area_import_areas")

    request = rf.get(url)
    request.user = superuser
    response = area_admin.import_areas.func(area_admin, request)

    assert response.status_code == 200

    csv_content = (
        b"Country,Province,District,Admin0,Adm1,Adm2\n"
        b"Afghanistan,Prov1,Distr1,AF,AF99,AF9999\n"
        b"Afghanistan,Prov1,Distr1,AF,AF99,AF9988\n"
    )
    upload = SimpleUploadedFile("file.csv", csv_content, content_type="text/csv")

    request = rf.post(url, data={"file": upload}, content_type=MULTIPART_CONTENT)
    request.user = superuser
    request.session = {}
    messages = FallbackStorage(request)
    request._messages = messages

    response = area_admin.import_areas.func(area_admin, request)

    assert response.status_code == 302
    assert response.url == reverse("admin:geo_area_changelist")

    stored_messages = [str(m) for m in messages]
    assert stored_messages == ["Found 4 new areas to create. The import is running in the background."]

    mock_task_delay.assert_called_once_with(csv_content.decode("utf-8-sig"))


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
def test_upload_validation_errors(
    csv_content: bytes,
    expected_message: str,
    area_admin: AreaAdmin,
    messages_request,
    geo_test_data,
) -> None:
    url = reverse("admin:geo_area_import_areas")
    upload = SimpleUploadedFile("file.csv", csv_content, content_type="text/csv")

    request, messages = messages_request(url, upload)
    response = area_admin.import_areas.func(area_admin, request)

    assert response.status_code == 302
    assert response.url == reverse("admin:geo_area_changelist")

    stored_messages = [str(m) for m in messages]
    assert stored_messages == [expected_message]
