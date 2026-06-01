import json

from django.contrib import admin
from django.urls import reverse
import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory
from hope.admin.universal_update_script import (
    ProgramAutocompleteSelect,
    ProgramChoiceField,
    UniversalUpdateAdmin,
    format_program_label,
)
from hope.models import Program, UniversalUpdate, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username="root",
        email="root@root.com",
        password="password",
    )


@pytest.fixture
def client_logged(client, admin_user):
    client.login(username="root", password="password")
    return client


@pytest.fixture
def business_area():
    return BusinessAreaFactory(code="0060", slug="afghanistan", name="Afghanistan", active=True)


@pytest.fixture
def program(business_area):
    return ProgramFactory(
        name="Test Program for Household",
        status=Program.ACTIVE,
        business_area=business_area,
    )


@pytest.fixture
def removed_program(business_area):
    removed = ProgramFactory(
        name="Disability Cash Transfers",
        status=Program.DRAFT,
        business_area=business_area,
    )
    removed.delete()
    return removed


@pytest.fixture
def active_program(business_area, removed_program):
    return ProgramFactory(
        name="Disability Cash Transfers",
        status=Program.ACTIVE,
        business_area=business_area,
    )


def test_universal_update_admin_edit_page_loads(client_logged, program):
    universal_update = UniversalUpdate.objects.create(
        program=program,
        individual_fields=["given_name", "family_name"],
    )

    url = reverse(
        "admin:universal_update_script_universalupdate_change",
        args=(universal_update.pk,),
    )

    response = client_logged.get(url)

    assert response.status_code == 200
    assert format_program_label(program) in response.content.decode()


def test_add_page_program_field_uses_scoped_autocomplete(client_logged):
    autocomplete_url = reverse("admin:universal_update_script_universalupdate_program_autocomplete")

    response = client_logged.get(reverse("admin:universal_update_script_universalupdate_add"))

    assert response.status_code == 200
    assert autocomplete_url in response.content.decode()


def test_program_autocomplete_excludes_removed_and_shows_business_area(client_logged, active_program, removed_program):
    response = client_logged.get(
        reverse("admin:universal_update_script_universalupdate_program_autocomplete"),
        data={"term": "Disability Cash Transfers"},
    )

    assert response.status_code == 200
    results_by_id = {item["id"]: item["text"] for item in response.json()["results"]}
    assert str(active_program.pk) in results_by_id
    assert str(removed_program.pk) not in results_by_id
    assert active_program.business_area.name in results_by_id[str(active_program.pk)]


def test_program_autocomplete_without_term_lists_saveable_programmes(client_logged, active_program, removed_program):
    response = client_logged.get(
        reverse("admin:universal_update_script_universalupdate_program_autocomplete"),
    )

    assert response.status_code == 200
    result_ids = {item["id"] for item in response.json()["results"]}
    assert str(active_program.pk) in result_ids
    assert str(removed_program.pk) not in result_ids


def test_program_autocomplete_handles_invalid_page(client_logged, active_program):
    response = client_logged.get(
        reverse("admin:universal_update_script_universalupdate_program_autocomplete"),
        data={"page": "not-a-number"},
    )

    assert response.status_code == 200
    result_ids = {item["id"] for item in response.json()["results"]}
    assert str(active_program.pk) in result_ids


def test_program_autocomplete_view_runs_single_query(rf, django_assert_num_queries, active_program, removed_program):
    model_admin = UniversalUpdateAdmin(UniversalUpdate, admin.site)
    request = rf.get("/", data={"term": "Disability"})

    with django_assert_num_queries(1):
        response = model_admin.program_autocomplete_view(request)

    assert response.status_code == 200
    assert json.loads(response.content)["results"]


def test_program_autocomplete_matches_business_area_name(client_logged, active_program, removed_program):
    response = client_logged.get(
        reverse("admin:universal_update_script_universalupdate_program_autocomplete"),
        data={"term": active_program.business_area.name},
    )

    assert response.status_code == 200
    result_ids = {item["id"] for item in response.json()["results"]}
    assert str(active_program.pk) in result_ids


def test_formfield_for_foreignkey_leaves_non_program_relations_unchanged(rf):
    model_admin = UniversalUpdateAdmin(UniversalUpdate, admin.site)
    business_area_fk = Program._meta.get_field("business_area")

    formfield = model_admin.formfield_for_foreignkey(business_area_fk, rf.get("/"))

    assert not isinstance(formfield.widget, ProgramAutocompleteSelect)
    assert not isinstance(formfield, ProgramChoiceField)
