"""Tests for IndividualAdmin configuration and button links."""

from django.contrib.admin.sites import AdminSite
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    UserFactory,
)
from hope.admin.individual import IndividualAdmin
from hope.models import Individual

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_client(client):
    user = UserFactory(username="admin_ind", is_staff=True, is_superuser=True, is_active=True, status="ACTIVE")
    user.set_password("password")
    user.save()
    client.login(username="admin_ind", password="password")
    return client


@pytest.fixture
def individual():
    ba = BusinessAreaFactory(slug="test-ind-ba")
    program = ProgramFactory(business_area=ba, status="ACTIVE")
    hh = HouseholdFactory(business_area=ba, program=program, create_role=False)
    ind = IndividualFactory(household=hh, business_area=ba, program=program)
    hh.head_of_household = ind
    hh.save(update_fields=["head_of_household"])
    return ind


def test_individual_admin_top_fieldset_has_program_and_business_area():
    site = AdminSite()
    individual_admin = IndividualAdmin(Individual, site)
    top_fields = individual_admin.fieldsets[0][1]["fields"]
    flat = []
    for f in top_fields:
        if isinstance(f, (list, tuple)):
            flat.extend(f)
        else:
            flat.append(f)
    assert "program" in flat
    assert "business_area" in flat


def test_individual_admin_fieldset_names():
    site = AdminSite()
    individual_admin = IndividualAdmin(Individual, site)
    fieldset_names = [fs[0] for fs in individual_admin.fieldsets]
    assert None in fieldset_names
    assert "Dates" in fieldset_names
    assert "Registration" in fieldset_names
    assert "Others" in fieldset_names


def test_individual_household_members_redirects(admin_client, individual):
    url = reverse("admin:household_individual_household_members", args=[individual.pk])
    response = admin_client.get(url)
    assert response.status_code == 302
    location = response["Location"]
    assert "household_individual" in location
    assert f"household__id__exact={individual.household.id}" in location


def test_individual_changelist_loads(admin_client, individual):
    url = reverse("admin:household_individual_changelist")
    response = admin_client.get(url)
    assert response.status_code == 200


def test_individual_change_page_loads(admin_client, individual):
    url = reverse("admin:household_individual_change", args=[individual.pk])
    response = admin_client.get(url)
    assert response.status_code == 200
