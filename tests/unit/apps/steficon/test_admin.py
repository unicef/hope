from uuid import uuid4

from django.urls import reverse

import pytest

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.steficon.admin import AutocompleteWidget
from hct_mis_api.apps.steficon.fixtures import RuleFactory
from hct_mis_api.apps.steficon.models import Rule


@pytest.mark.django_db
def test_get_url_without_business_area() -> None:
    widget = AutocompleteWidget(model=Program, admin_site="admin")
    expected_url = reverse("admin:autocomplete")
    assert widget.get_url() == expected_url


@pytest.mark.django_db
def test_get_url_with_business_area() -> None:
    business_area_id = uuid4()
    widget = AutocompleteWidget(model=Program, admin_site="admin", business_area=business_area_id)
    expected_url = f"{reverse('admin:autocomplete')}?business_area={business_area_id}"
    assert widget.get_url() == expected_url


@pytest.mark.django_db
def test_get_context_without_business_area() -> None:
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


@pytest.mark.django_db
def test_get_context_with_business_area() -> None:
    business_area_id = uuid4()
    widget = AutocompleteWidget(model=Program, admin_site="admin", business_area=business_area_id)
    mock_attrs = {"class": "test-class"}
    context = widget.get_context("program", "test_value", mock_attrs)

    assert context["widget"]["query_string"] == f"business_area__exact={business_area_id}"
    assert context["widget"]["url"] == f"{reverse('admin:autocomplete')}?business_area={business_area_id}"


@pytest.fixture
def rule_test_setup(client):
    admin_user = UserFactory(is_superuser=True, username="admin", email="admin@admin.com")
    admin_user.set_password("password")
    admin_user.save()
    client.login(username=admin_user.username, password="password")
    rule = RuleFactory(
        name="Test Rule",
        definition="result.value = 2 + 3",
        language="python",
        type=Rule.TYPE_PAYMENT_PLAN,
    )
    return client, rule


@pytest.mark.django_db
def test_test_button_with_raw_data(rule_test_setup) -> None:
    client, rule = rule_test_setup
    url = reverse("admin:steficon_rule_test", args=[rule.pk])
    raw_data = '{"a": 1, "b": 2}'
    post_data = {
        "opt": "optData",
        "raw_data": raw_data,
    }
    response = client.post(url, post_data)
    assert response.status_code == 200
    assert "results" in response.context
    results = response.context["results"]
    assert len(results) == 1
    assert results[0]["success"]
    assert results[0]["result"].value == 5
    assert results[0]["error"] is None


@pytest.mark.django_db
def test_test_button_with_failing_raw_data(rule_test_setup) -> None:
    client, rule = rule_test_setup
    rule.definition = 'result.value = data["a"] + data["b"]'
    rule.save()

    url = reverse("admin:steficon_rule_test", args=[rule.pk])
    raw_data = '{"a": 1}'  # missing "b"
    post_data = {
        "opt": "optData",
        "raw_data": raw_data,
    }

    response = client.post(url, post_data)
    assert response.status_code == 200
    assert "results" in response.context
    results = response.context["results"]
    assert len(results) == 1
    assert not results[0]["success"]
    assert "NameError" in results[0]["error"]
