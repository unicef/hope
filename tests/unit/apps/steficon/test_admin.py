from typing import Tuple
from uuid import uuid4

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client as DjangoClient
from django.urls import reverse
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.steficon import RuleFactory

from hope.admin.steficon import AutocompleteWidget
from hope.apps.program.models import Program
from hope.apps.steficon.forms import RuleTestForm
from hope.apps.steficon.models import Rule


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
def rule_test_setup(client: DjangoClient) -> Tuple[DjangoClient, Rule]:
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
def test_test_button_with_raw_data(rule_test_setup: Tuple[DjangoClient, Rule]) -> None:
    client, rule = rule_test_setup
    url = reverse("admin:steficon_rule_test", args=[rule.pk])
    raw_data = '{"a": 1, "b": 2}'
    post_data = {
        "opt": "optData",
        "raw_data": raw_data,
    }
    response = client.post(url, post_data)
    assert response.status_code == 200
    assert "results" in response.context_data
    results = response.context_data["results"]
    assert len(results) == 1
    assert results[0]["success"]
    assert results[0]["result"].value == 5
    assert results[0]["error"] is None


@pytest.mark.django_db
def test_test_button_with_failing_raw_data(rule_test_setup: Tuple[DjangoClient, Rule]) -> None:
    client, rule = rule_test_setup
    rule.definition = 'result.value = context["data"]["a"] + context["data"]["b"]'
    rule.save()

    url = reverse("admin:steficon_rule_test", args=[rule.pk])
    raw_data = '{"a": 1}'  # missing "b"
    post_data = {
        "opt": "optData",
        "raw_data": raw_data,
    }

    response = client.post(url, post_data)
    assert response.status_code == 200
    assert "results" in response.context_data
    results = response.context_data["results"]
    assert len(results) == 1
    assert not results[0]["success"]
    assert "KeyError" in results[0]["error"]


@pytest.mark.django_db
def test_test_button_get_request(rule_test_setup: Tuple[DjangoClient, Rule]) -> None:
    client, rule = rule_test_setup
    url = reverse("admin:steficon_rule_test", args=[rule.pk])
    response = client.get(url)
    assert response.status_code == 200
    assert "form" in response.context_data
    assert isinstance(response.context_data["form"], RuleTestForm)


@pytest.mark.django_db
def test_test_button_with_invalid_form(rule_test_setup: Tuple[DjangoClient, Rule]) -> None:
    client, rule = rule_test_setup
    url = reverse("admin:steficon_rule_test", args=[rule.pk])
    post_data = {
        "opt": "optData",
        # "raw_data" is missing, so form is invalid
    }
    response = client.post(url, post_data)
    assert response.status_code == 200
    assert "form" in response.context_data
    assert response.context_data["form"].errors


@pytest.mark.django_db
def test_test_button_with_file(rule_test_setup: tuple) -> None:
    client, rule = rule_test_setup
    rule.definition = 'result.value = context["data"]["a"] + context["data"]["b"]'
    rule.save()

    url = reverse("admin:steficon_rule_test", args=[rule.pk])
    file_content = '[{"a": 1, "b": 2}, {"a": 10, "b": 20}]'
    uploaded_file = SimpleUploadedFile("test.json", file_content.encode("utf-8"), content_type="application/json")
    post_data = {"opt": "optFile", "file": uploaded_file}

    response = client.post(url, post_data)
    assert response.status_code == 200
    assert "results" in response.context_data
    results = response.context_data["results"]
    assert len(results) == 2
    assert results[0]["success"]
    assert results[0]["result"].value == 3
    assert results[1]["success"]
    assert results[1]["result"].value == 30


@pytest.mark.django_db
def test_test_button_with_target_population(rule_test_setup: Tuple[DjangoClient, Rule]) -> None:
    client, rule = rule_test_setup
    business_area = create_afghanistan()
    pp = PaymentPlanFactory(business_area=business_area)

    hoh1 = IndividualFactory(household=None)
    hoh2 = IndividualFactory(household=None)
    hh1 = HouseholdFactory(head_of_household=hoh1)
    hh1.save()
    hh2 = HouseholdFactory(head_of_household=hoh2)
    hh2.save()
    hoh1.household = hh1
    hoh1.save()
    hoh2.household = hh2
    hoh2.save()

    PaymentFactory(parent=pp, household=hh1)
    PaymentFactory(parent=pp, household=hh2)

    rule.definition = 'result.value = context["data"]["household"]'
    rule.save()

    url = reverse("admin:steficon_rule_test", args=[rule.pk])
    post_data = {
        "opt": "optTargetPopulation",
        "target_population": pp.pk,
    }

    response = client.post(url, post_data)
    assert response.status_code == 200
    assert "results" in response.context_data
    results = response.context_data["results"]
    assert len(results) == 2
    result_values = {str(r["result"].value) for r in results}
    assert {r["success"] for r in results} == {True}
    assert result_values == {str(hh1), str(hh2)}


@pytest.mark.django_db
def test_test_button_with_content_type(rule_test_setup: Tuple[DjangoClient, Rule]) -> None:
    client, rule = rule_test_setup

    RuleFactory(name="Rule 1", definition="result.value=1")
    RuleFactory(name="Rule 2", definition="result.value=2")

    rule_ct = ContentType.objects.get_for_model(Rule)

    rule.definition = "result.value = context['data'].name"
    rule.save()

    url = reverse("admin:steficon_rule_test", args=[rule.pk])
    post_data = {
        "opt": "optContentType",
        "content_type": rule_ct.pk,
        "content_type_filters": '{"name__startswith": "Rule "}',  # Note the space
    }

    response = client.post(url, post_data)
    assert response.status_code == 200
    assert "results" in response.context_data
    results = response.context_data["results"]
    assert len(results) == 2
    names = {r["result"].value for r in results}
    assert names == {"Rule 1", "Rule 2"}


@pytest.mark.django_db
def test_test_button_with_invalid_selection(rule_test_setup: Tuple[DjangoClient, Rule]) -> None:
    client, rule = rule_test_setup
    url = reverse("admin:steficon_rule_test", args=[rule.pk])
    post_data = {
        "opt": "invalid_option",
        "raw_data": "{}",
    }
    with pytest.raises(Exception, match="Invalid option 'invalid_option'"):
        client.post(url, post_data)


@pytest.mark.django_db
def test_test_button_for_rule_commit(rule_test_setup: Tuple[DjangoClient, Rule]) -> None:
    client, rule = rule_test_setup
    rule_commit = rule.latest_commit
    assert rule_commit

    url = reverse("admin:steficon_rulecommit_test", args=[rule_commit.pk])
    raw_data = '{"a": 1, "b": 2}'
    post_data = {
        "opt": "optData",
        "raw_data": raw_data,
    }
    response = client.post(url, post_data)
    assert response.status_code == 200
    assert "results" in response.context_data
    results = response.context_data["results"]
    assert len(results) == 1
    assert results[0]["success"]
    assert results[0]["result"].value == 5
    assert results[0]["error"] is None
