from unittest.mock import Mock, patch

from django.contrib.admin import AdminSite
from django.contrib.admin.options import ModelAdmin
from django.test import RequestFactory, override_settings
from django.urls import reverse

from django_webtest import WebTest
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from factory import fuzzy
from flaky import flaky
from webtest import Upload

from hct_mis_api.apps.account.models import Partner, User
from hct_mis_api.apps.geo.admin import AreaAdmin
from hct_mis_api.apps.geo.models import Area, AreaType, Country


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
        self.client.force_login(
            User.objects.get_or_create(username="testuser", partner=Partner.objects.get_or_create(name="UNICEF")[0])[0]
        )

    def tearDown(self) -> None:
        from django.core.cache import cache

        cache.clear()
        super().tearDown()

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
    @patch("hct_mis_api.apps.geo.admin.import_areas_from_csv_task.delay")
    def test_upload(self, mock_task_delay: Mock) -> None:
        Country.objects.get_or_create(
            iso_code2="AF",
            defaults={
                "name": "Afghanistan",
                "short_name": "Afghanistan",
                "iso_code3": "AFG",
                "iso_num": "004",
            },
        )
        self.assertEqual(AreaType.objects.count(), 2)
        self.assertEqual(Area.objects.count(), 5)
        resp = self.app.get(reverse("admin:geo_area_changelist"), user=self.superuser).click("Import Areas")
        assert "Upload a csv" in resp
        form = resp.form
        csv_content = b"Country,Province,District,Admin0,Adm1,Adm2\nAfghanistan,Prov1,Distr1,AF,AF99,AF9999\nAfghanistan,Prov1,Distr1,AF,AF99,AF9988\n"
        form["file"] = Upload(
            "file.csv",
            csv_content,
            "text/csv",
        )
        resp = form.submit("Import")
        assert resp.status_int == 302

        redirect_resp = resp.follow()
        messages = list(redirect_resp.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertIn("Found 4 new areas to create.", str(messages[0]))
        self.assertIn("The import is running in the background.", str(messages[0]))

        self.assertEqual(AreaType.objects.count(), 2)
        self.assertEqual(Area.objects.count(), 5)
        mock_task_delay.assert_called_once_with(csv_content.decode("utf-8-sig"))
