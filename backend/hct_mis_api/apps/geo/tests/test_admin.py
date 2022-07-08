from django.contrib.admin import AdminSite
from factory import fuzzy
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.geo.admin import AreaAdmin
from hct_mis_api.apps.geo.fixtures import AreaTypeFactory, AreaFactory
from django.test import override_settings, RequestFactory
from django.urls import reverse
from django.contrib.admin.options import ModelAdmin
from django_webtest import WebTest
from hct_mis_api.apps.geo.models import AreaType, Area
from django.contrib.auth import get_user_model
from io import BytesIO
from webtest import Upload
User = get_user_model()


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestGeoApp(WebTest):
    databases = ["default"]

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.area_types = AreaTypeFactory.create_batch(2)
        cls.areas = AreaFactory.create_batch(5, area_type=fuzzy.FuzzyChoice(AreaType.objects.all()))
        cls.superuser: User = UserFactory(is_superuser=True, is_staff=True)

    def setUp(self):
        self.site = AdminSite()
        self.admin = AreaAdmin(Area, self.site)
        self.client.force_login(User.objects.get_or_create(username='testuser')[0])
        self.file = BytesIO(b'Country,Province,District,Admin0,Adm1,Adm2\nAfghanistan,Prov1,Distr1,AF,AF99,AF9999\n')

    def test_modeladmin_str(self):
        ma = ModelAdmin(Area, self.site)
        self.assertEqual(str(ma), "geo.ModelAdmin")

    def test_login(self):
        url = reverse("admin:geo_area_changelist")
        resp = self.app.get(url)
        assert resp.status_int == 302, "You need to be logged in"
        resp = self.app.get(url, user=self.superuser)
        assert resp.status_int == 200, "You need to be logged in and superuser"

    def test_upload(self):
        self.assertEqual(AreaType.objects.count(), 2, "Two area types created")
        self.assertEqual(Area.objects.count(), 5, "Five area created")
        resp = self.app.get(reverse('admin:geo_area_changelist'), user=self.superuser).click("Import Areas")
        assert "Upload a csv" in resp
        form = resp.form
        form["file"] = Upload(
            "file.csv", 
            b'Country,Province,District,Admin0,Adm1,Adm2\nAfghanistan,Prov1,Distr1,AF,AF99,AF9999\n',
            "text/csv"
            )
        resp = form.submit("Import")
        assert resp.status_int == 302, "The form is not good"
        self.assertEqual(AreaType.objects.count(), 4, "Two new area types created")
        self.assertEqual(Area.objects.count(), 7, "Two new area created")
