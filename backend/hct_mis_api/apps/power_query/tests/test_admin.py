from django.contrib.contenttypes.management import create_contenttypes
from django.test import override_settings
from django.urls import reverse

import pytest
from django_webtest import WebTest

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.power_query.defaults import create_defaults
from hct_mis_api.apps.power_query.models import Parametrizer, Query
from hct_mis_api.apps.power_query.tests.fixtures import (
    DatasetFactory,
    FormatterFactory,
    ParametrizerFactory,
    QueryFactory,
    ReportDocumentFactory,
    ReportFactory,
)


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQueryAdmin(WebTest):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)
        cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        BusinessAreaFactory()
        create_defaults()
        # ----
        from django.apps import apps

        create_contenttypes(apps.get_app_config("auth"))
        # cls.formatter_json = FormatterFactory(name="Queryset To JSON", content_type="json", code="")
        cls.query_qs = QueryFactory()
        cls.query_values = QueryFactory(name="byValue", code="result=list(conn.values())")
        cls.query_error = QueryFactory(name="Error", code="result=1")
        cls.query_dataset = QueryFactory(code="result=Dataset(conn.values())")
        cls.query_params = QueryFactory(parametrizer=ParametrizerFactory())
        # cls.report1: Report = ReportFactory(formatter=cls.formatter_json, query=cls.query, owner=cls.user1)
        # cls.report2: Report = ReportFactory(formatter=cls.formatter_json, query=cls.query, owner=cls.user2)
        # cls.report2.execute(run_query=True)

    def test_change_list(self) -> None:
        url = reverse("admin:power_query_query_changelist")
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200

    def test_change_form(self) -> None:
        url = reverse("admin:power_query_query_change", args=[self.query_qs.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.forms["query_form"].submit()
        assert res.status_code == 302

    @pytest.mark.xfail(reason="todo investigate")
    def test_button_run(self) -> None:
        url = reverse("admin:power_query_query_change", args=[self.query_qs.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.click("Run", linkid="btn-run")
        assert res.status_code == 200

    def test_button_datasets(self) -> None:
        url = reverse("admin:power_query_query_change", args=[self.query_qs.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.click("Datasets", linkid="btn-datasets")
        assert res.status_code == 302

    def test_button_queue(self) -> None:
        url = reverse("admin:power_query_query_change", args=[self.query_qs.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.click("Queue")
        assert res.status_code == 302

    def test_button_preview_qs(self) -> None:
        url = reverse("admin:power_query_query_change", args=[self.query_qs.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.click("Preview")
        assert res.status_code == 200

    def test_button_preview_values(self) -> None:
        url = reverse("admin:power_query_query_change", args=[self.query_values.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.click("Preview")
        assert res.status_code == 200

    def test_button_preview_dataset(self) -> None:
        url = reverse("admin:power_query_query_change", args=[self.query_dataset.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.click("Preview")
        assert res.status_code == 200

    def test_button_preview_value_error(self) -> None:
        url = reverse("admin:power_query_query_change", args=[self.query_error.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.click("Preview")
        assert res.status_code == 200

    def test_button_preview_parametrizer(self) -> None:
        url = reverse("admin:power_query_query_change", args=[self.query_params.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.click("Preview")
        assert res.status_code == 200

    def test_create(self) -> None:
        url = reverse("admin:power_query_query_add")
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestDatasetAdmin(WebTest):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)
        cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        BusinessAreaFactory()
        create_defaults()
        cls.dataset = DatasetFactory()

    def test_change_list(self) -> None:
        url = reverse("admin:power_query_dataset_changelist")
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200

    def test_change_form(self) -> None:
        url = reverse("admin:power_query_dataset_change", args=[self.dataset.pk])
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200

    def test_button_preview(self) -> None:
        url = reverse("admin:power_query_dataset_change", args=[self.dataset.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.click("Preview")
        assert res.status_code == 200


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestFormatterAdmin(WebTest):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)
        cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        BusinessAreaFactory()
        create_defaults()
        cls.formatter = FormatterFactory()

    def test_change_list(self) -> None:
        url = reverse("admin:power_query_formatter_changelist")
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200

    def test_change_form(self) -> None:
        url = reverse("admin:power_query_formatter_change", args=[self.formatter.pk])
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200

    def test_button_test(self) -> None:
        url = reverse("admin:power_query_formatter_change", args=[self.formatter.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.click("Test")
        res.forms["formatter-form"]["query"] = Query.objects.first().pk
        res = res.forms["formatter-form"].submit()
        assert res.status_code == 200


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestReportAdmin(WebTest):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)
        cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        BusinessAreaFactory()
        create_defaults()
        cls.report = ReportFactory()

    def test_change_list(self) -> None:
        url = reverse("admin:power_query_report_changelist")
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200

    def test_add(self) -> None:
        url = reverse("admin:power_query_report_add")
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200

    def test_add_param(self) -> None:
        url = reverse("admin:power_query_report_add")
        qid = QueryFactory().pk
        res = self.app.get(f"{url}?q={qid}", user=self.superuser)
        assert res.status_code == 200

    def test_change_form(self) -> None:
        url = reverse("admin:power_query_report_change", args=[self.report.pk])
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200

    def test_button_queue(self) -> None:
        url = reverse("admin:power_query_report_change", args=[self.report.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.click("Queue")
        assert res.status_code == 302

    def test_button_execute(self) -> None:
        url = reverse("admin:power_query_report_change", args=[self.report.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.click("Execute")
        assert res.status_code == 302

    def test_button_refresh(self) -> None:
        url = reverse("admin:power_query_report_changelist")
        res = self.app.get(url, user=self.superuser)
        res = res.click("Refresh")
        assert res.status_code == 302


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestParametrizerAdmin(WebTest):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)
        cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        BusinessAreaFactory()
        create_defaults()
        cls.params = ParametrizerFactory()
        cls.system_params = Parametrizer.objects.get(code="active-business-areas")

    def test_button_refresh(self) -> None:
        url = reverse("admin:power_query_parametrizer_change", args=[self.system_params.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.click("Refresh")
        assert res.status_code == 302

    def test_button_preview(self) -> None:
        url = reverse("admin:power_query_parametrizer_change", args=[self.params.pk])
        res = self.app.get(url, user=self.superuser)
        res = res.click("Preview")
        assert res.status_code == 200


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestReportDocumentAdmin(WebTest):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        cls.superuser = UserFactory(is_superuser=True, is_staff=True, is_active=True)
        cls.user1 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        cls.user2 = UserFactory(is_superuser=False, is_staff=False, is_active=True)
        BusinessAreaFactory()
        create_defaults()
        cls.document = ReportDocumentFactory()

    def test_change_list(self) -> None:
        url = reverse("admin:power_query_reportdocument_changelist")
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200

    def test_change_form(self) -> None:
        url = reverse("admin:power_query_reportdocument_change", args=[self.document.pk])
        res = self.app.get(url, user=self.superuser)
        assert res.status_code == 200
