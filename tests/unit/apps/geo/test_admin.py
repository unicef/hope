from django.contrib.admin import AdminSite
from django.contrib.admin.options import ModelAdmin
from django.test import RequestFactory, override_settings
from django.urls import reverse

from django_webtest import WebTest
from factory import fuzzy
from flaky import flaky
from webtest import Upload

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import Partner, User
from hct_mis_api.apps.geo.admin import AreaAdmin
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.geo.models import Area, AreaType


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestGeoApp(WebTest):
    databases = ["default"]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.factory = RequestFactory()
        cls.area_types = AreaTypeFactory.create_batch(2)
        cls.areas = AreaFactory.create_batch(5, area_type=fuzzy.FuzzyChoice(AreaType.objects.all()))
        cls.superuser: User = UserFactory(is_superuser=True, is_staff=True)

    def setUp(self) -> None:
        self.site = AdminSite()
        self.admin = AreaAdmin(Area, self.site)
        unicef_partner, _ = Partner.objects.get_or_create(name="UNICEF")
        self.client.force_login(
            User.objects.get_or_create(
                username="testuser", partner=Partner.objects.get_or_create(name="UNICEF HQ", parent=unicef_partner)[0]
            )[0]
        )

    def test_modeladmin_str(self) -> None:
        ma = ModelAdmin(Area, self.site)
        self.assertEqual(str(ma), "geo.ModelAdmin")

    def test_login(self) -> None:
        url = reverse("admin:geo_area_changelist")
        resp = self.app.get(url)
        assert resp.status_int == 302, "You need to be logged in"
        resp = self.app.get(url, user=self.superuser)
        assert resp.status_int == 200, "You need to be logged in and superuser"

    @flaky(max_runs=3, min_passes=1)
    def test_upload(self) -> None:
        self.assertEqual(AreaType.objects.count(), 2, "Two area types created")
        self.assertEqual(Area.objects.count(), 5, "Five area created")
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
        self.assertEqual(AreaType.objects.count(), 4, "Two new area types created")
        self.assertEqual(Area.objects.count(), 8, "Two new area created")
