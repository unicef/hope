"""Tests for IndividualAdmin configuration and button links."""

from django.contrib.admin.sites import AdminSite
from django.contrib.messages import get_messages
from django.forms.models import modelform_factory
from django.test import RequestFactory
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DataCollectingTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    UserFactory,
)
from hope.admin.individual import IndividualAdmin
from hope.apps.household.services.household_recalculate_data import recalculate_data
from hope.models import AsyncJob, Individual

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
    assert "household/individual" in location
    assert f"household__id__exact={individual.household.id}" in location


def test_individual_household_members_warns_and_redirects_when_no_household(admin_client):
    ba = BusinessAreaFactory(slug="test-ind-no-hh-ba")
    program = ProgramFactory(business_area=ba)
    ind = IndividualFactory(household=None, business_area=ba, program=program)

    url = reverse("admin:household_individual_household_members", args=[ind.pk])
    response = admin_client.get(url)

    assert response.status_code == 302
    assert response["Location"] == reverse("admin:household_individual_changelist")
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert "not assigned to any household" in str(messages[0])


def test_individual_changelist_loads(admin_client, individual):
    url = reverse("admin:household_individual_changelist")
    response = admin_client.get(url)
    assert response.status_code == 200


def test_individual_change_page_loads(admin_client, individual):
    url = reverse("admin:household_individual_change", args=[individual.pk])
    response = admin_client.get(url)
    assert response.status_code == 200


@pytest.fixture
def household_with_member():
    program = ProgramFactory(data_collecting_type=DataCollectingTypeFactory(recalculate_composition=True))
    household = HouseholdFactory(program=program, business_area=program.business_area)
    IndividualFactory(
        household=household,
        program=program,
        business_area=program.business_area,
        registration_data_import=household.registration_data_import,
    )
    recalculate_data(household)
    household.refresh_from_db()
    return household


def test_admin_withdrawing_individual_recalculates_household(household_with_member, django_capture_on_commit_callbacks):
    assert household_with_member.size == 2
    member = household_with_member.individuals.exclude(pk=household_with_member.head_of_household_id).get()

    form = modelform_factory(Individual, fields=["withdrawn"])({"withdrawn": True}, instance=member)
    assert form.is_valid()

    with django_capture_on_commit_callbacks(execute=True):
        IndividualAdmin(Individual, AdminSite()).save_model(
            RequestFactory().post("/"), form.save(commit=False), form, change=True
        )

    household_with_member.refresh_from_db()
    assert household_with_member.size == 1
    assert AsyncJob.objects.filter(job_name="adjust_program_size_async_task").exists()


def test_admin_editing_unrelated_field_skips_recalculation(household_with_member, django_capture_on_commit_callbacks):
    member = household_with_member.individuals.exclude(pk=household_with_member.head_of_household_id).get()

    form = modelform_factory(Individual, fields=["given_name"])({"given_name": "Renamed"}, instance=member)
    assert form.is_valid()

    with django_capture_on_commit_callbacks(execute=True):
        IndividualAdmin(Individual, AdminSite()).save_model(
            RequestFactory().post("/"), form.save(commit=False), form, change=True
        )

    assert not AsyncJob.objects.filter(job_name="adjust_program_size_async_task").exists()
