from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

import pytest

from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.steficon.admin import AutocompleteWidget
from hct_mis_api.apps.steficon.models import Rule


@pytest.mark.django_db
class TestAutocompleteWidget:
    def test_get_url_without_business_area(self) -> None:
        widget = AutocompleteWidget(model=Program, admin_site="admin")
        expected_url = reverse("admin:autocomplete")
        assert widget.get_url() == expected_url

    def test_get_url_with_business_area(self) -> None:
        business_area_id = uuid4()
        widget = AutocompleteWidget(
            model=Program, admin_site="admin", business_area=business_area_id
        )
        expected_url = (
            f"{reverse('admin:autocomplete')}?business_area={business_area_id}"
        )
        assert widget.get_url() == expected_url

    def test_get_context_without_business_area(self) -> None:
        widget = AutocompleteWidget(model=Program, admin_site="admin")
        mock_attrs = {"class": "test-class"}
        context = widget.get_context("program", "test_value", mock_attrs)

        assert context["widget"]["query_string"] == ""
        assert context["widget"]["url"] == reverse("admin:autocomplete")
        assert context["widget"]["target_opts"]["app_label"] == "program"
        assert context["widget"]["target_opts"]["model_name"] == "program"
        assert context["widget"]["target_opts"]["target_field"] == "id"
        assert context["widget"]["name"] == "program"
        assert context["widget"]["attrs"]["class"] == "test-class"

    def test_get_context_with_business_area(self) -> None:
        business_area_id = uuid4()
        widget = AutocompleteWidget(
            model=Program, admin_site="admin", business_area=business_area_id
        )
        mock_attrs = {"class": "test-class"}
        context = widget.get_context("program", "test_value", mock_attrs)

        assert (
            context["widget"]["query_string"]
            == f"business_area__exact={business_area_id}"
        )
        assert (
            context["widget"]["url"]
            == f"{reverse('admin:autocomplete')}?business_area={business_area_id}"
        )


@pytest.mark.django_db
class TestTestRuleMixin(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username="root", email="root@root.com", password="password"
        )
        self.client.login(username=self.admin_user.username, password="password")
        self.rule = Rule.objects.create(
            name="Test Rule",
            definition="result.value = 2 + 3",
            language="python",
            type=Rule.TYPE_PAYMENT_PLAN,
        )

    def test_test_button_with_raw_data(self) -> None:
        url = reverse("admin:steficon_rule_test", args=[self.rule.pk])
        raw_data = '{"a": 1, "b": 2}'
        post_data = {
            "opt": "optData",
            "raw_data": raw_data,
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.context)
        results = response.context["results"]
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["success"])
        self.assertEqual(results[0]["result"].value, 5)
        self.assertIsNone(results[0]["error"])

    def test_test_button_with_failing_raw_data(self) -> None:
        self.rule.definition = 'result.value = data["a"] + data["b"]'
        self.rule.save()

        url = reverse("admin:steficon_rule_test", args=[self.rule.pk])
        raw_data = '{"a": 1}'  # missing "b"
        post_data = {
            "opt": "optData",
            "raw_data": raw_data,
        }

        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.context)
        results = response.context["results"]
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0]["success"])
        self.assertIn("NameError", results[0]["error"])
