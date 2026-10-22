"""Search by unicef_id in the Household/Individual admin must prefix-match, not scan."""

from admin_cursor_paginator.cursor import Cursor, encode_cursor
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Permission
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    UserFactory,
)
from hope.admin.household import HouseholdAdmin
from hope.admin.individual import IndividualAdmin
from hope.models import Household, Individual

pytestmark = pytest.mark.django_db


@pytest.fixture
def population():
    ba = BusinessAreaFactory(slug="unicef-id-search-ba")
    program = ProgramFactory(business_area=ba, status="ACTIVE")
    household = HouseholdFactory(business_area=ba, program=program, create_role=False, unicef_id="HH-24-0000.0001")
    individual = IndividualFactory(household=household, business_area=ba, program=program, unicef_id="IND-24-0000.0001")
    other = IndividualFactory(
        household=None, business_area=ba, program=program, unicef_id="IND-24-0000.0002", family_name="Kowalski"
    )
    return {"household": household, "individual": individual, "other": other}


@pytest.fixture
def staff_request():
    request = RequestFactory().get("/admin/")
    request.user = UserFactory(is_staff=True, is_superuser=True, is_active=True, status="ACTIVE")
    return request


def search_sql(model_admin, request, term):
    queryset, _ = model_admin.get_search_results(request, model_admin.get_queryset(request), term)
    return str(queryset.query)


@pytest.mark.parametrize("term", ["IND-24-0000.0001", "ind-24-0000.0001", "  IND-24-0000.0001  "])
def test_individual_search_by_unicef_id_finds_individual_regardless_of_case(population, staff_request, term):
    model_admin = IndividualAdmin(Individual, AdminSite())

    queryset, _ = model_admin.get_search_results(staff_request, model_admin.get_queryset(staff_request), term)

    assert list(queryset) == [population["individual"]]


@pytest.mark.parametrize("term", ["IND-24-0000.0001", "IND-2", "IND-24", "IND-24-00", "IND-24-0000."])
def test_individual_search_by_unicef_id_emits_prefix_like_without_upper(population, staff_request, term):
    model_admin = IndividualAdmin(Individual, AdminSite())

    sql = search_sql(model_admin, staff_request, term)

    assert f"LIKE {term}%" in sql
    assert "UPPER" not in sql


def test_individual_search_by_household_unicef_id_returns_household_members(population, staff_request):
    model_admin = IndividualAdmin(Individual, AdminSite())

    queryset, _ = model_admin.get_search_results(
        staff_request, model_admin.get_queryset(staff_request), "HH-24-0000.0001"
    )

    assert set(queryset) == set(population["household"].individuals.all())
    assert population["other"] not in queryset


@pytest.mark.parametrize(
    "term",
    ["Kowalski", "IND", "XYZ-24-0000.0001", "IND-24-0000.0002 Kowalski", "IND-24-0000.00012", "IND-2-34"],
)
def test_individual_search_by_non_unicef_id_term_falls_back_to_default_search(population, staff_request, term):
    model_admin = IndividualAdmin(Individual, AdminSite())

    sql = search_sql(model_admin, staff_request, term)

    assert "UPPER" in sql


def test_individual_search_by_name_still_matches(population, staff_request):
    model_admin = IndividualAdmin(Individual, AdminSite())

    queryset, _ = model_admin.get_search_results(staff_request, model_admin.get_queryset(staff_request), "Kowalski")

    assert list(queryset) == [population["other"]]


def test_individual_search_by_unicef_id_and_name_matches_both_terms(population, staff_request):
    model_admin = IndividualAdmin(Individual, AdminSite())

    queryset, _ = model_admin.get_search_results(
        staff_request, model_admin.get_queryset(staff_request), "IND-24-0000.0002 Kowalski"
    )

    assert list(queryset) == [population["other"]]


def test_individual_search_by_unicef_id_runs_a_single_query(population, staff_request, django_assert_num_queries):
    model_admin = IndividualAdmin(Individual, AdminSite())

    with django_assert_num_queries(1):
        queryset, _ = model_admin.get_search_results(
            staff_request, model_admin.get_queryset(staff_request), "IND-24-0000.0001"
        )
        list(queryset)


def test_household_search_by_unicef_id_emits_prefix_like_without_upper(population, staff_request):
    model_admin = HouseholdAdmin(Household, AdminSite())

    sql = search_sql(model_admin, staff_request, "HH-24-0000.0001")

    assert "LIKE HH-24-0000.0001%" in sql
    assert "UPPER" not in sql


def test_household_search_by_unicef_id_finds_household(population, staff_request):
    model_admin = HouseholdAdmin(Household, AdminSite())

    queryset, _ = model_admin.get_search_results(
        staff_request, model_admin.get_queryset(staff_request), "hh-24-0000.0001"
    )

    assert list(queryset) == [population["household"]]


@pytest.mark.parametrize(("model", "model_admin_class"), [(Individual, IndividualAdmin), (Household, HouseholdAdmin)])
def test_admin_does_not_run_a_count_query_for_a_search(population, staff_request, model, model_admin_class):
    model_admin = model_admin_class(model, AdminSite())
    assert model_admin.show_query_result_count is False

    with CaptureQueriesContext(connection) as captured:
        queryset, _ = model_admin.get_search_results(
            staff_request, model_admin.get_queryset(staff_request), "HH-24-0000.0001"
        )
        list(queryset)

    assert [query for query in captured.captured_queries if "COUNT(*)" in query["sql"]] == []


# Three ids per model in the program and a fourth in another program of the same business area, so the program
# filter (applied only together with business_area__exact) visibly drops it.
@pytest.fixture
def paged_population():
    ba = BusinessAreaFactory(slug="unicef-id-paging-ba")
    program = ProgramFactory(business_area=ba, status="ACTIVE")
    other_program = ProgramFactory(business_area=ba, status="ACTIVE")
    HouseholdFactory(
        business_area=ba,
        program=program,
        create_role=False,
        unicef_id="HH-24-0000.0001",
        head_of_household__unicef_id="IND-24-0000.0001",
    )
    HouseholdFactory(
        business_area=ba,
        program=program,
        create_role=False,
        unicef_id="HH-24-0000.0002",
        head_of_household__unicef_id="IND-24-0000.0002",
    )
    HouseholdFactory(
        business_area=ba,
        program=program,
        create_role=False,
        unicef_id="HH-24-0000.0003",
        head_of_household__unicef_id="IND-24-0000.0003",
    )
    HouseholdFactory(
        business_area=ba,
        program=other_program,
        create_role=False,
        unicef_id="HH-24-0000.0004",
        head_of_household__unicef_id="IND-24-0000.0004",
    )
    return {"business_area__exact": str(ba.id), "program__exact": str(program.id)}


@pytest.fixture
def staff_client(client):
    user = UserFactory(is_staff=True)
    user.user_permissions.set(
        Permission.objects.filter(
            content_type__app_label="household", codename__in=["view_individual", "view_household"]
        )
    )
    client.force_login(user, backend="django.contrib.auth.backends.ModelBackend")
    return client


@pytest.mark.parametrize(
    ("model", "model_admin_class", "term", "ordering_field"),
    [
        (Individual, IndividualAdmin, "IND-24", "unicef_id_c"),
        (Household, HouseholdAdmin, "HH-24", "unicef_id_c"),
        (Individual, IndividualAdmin, "HH-24", "unicef_id"),
        (Individual, IndividualAdmin, "", "unicef_id"),
        (Household, HouseholdAdmin, "", "unicef_id"),
    ],
    ids=[
        "individual-own-id",
        "household-own-id",
        "individual-household-id",
        "individual-no-search",
        "household-no-search",
    ],
)
def test_paginator_orders_by_c_collation_only_for_own_unicef_id_search(
    population, staff_request, model, model_admin_class, term, ordering_field
):
    model_admin = model_admin_class(model, AdminSite())
    queryset, _ = model_admin.get_search_results(staff_request, model_admin.get_queryset(staff_request), term)

    paginator = model_admin.get_paginator(staff_request, queryset, 100)

    assert paginator.ordering_field == ordering_field


@pytest.mark.parametrize(
    ("url_name", "params", "expected"),
    [
        (
            "admin:household_individual_changelist",
            {"q": "IND-24"},
            ["IND-24-0000.0001", "IND-24-0000.0002", "IND-24-0000.0003"],
        ),
        (
            "admin:household_individual_changelist",
            {"q": "IND-24", "p": encode_cursor(Cursor(value="IND-24-0000.0001", is_reverse=0, number=2))},
            ["IND-24-0000.0002", "IND-24-0000.0003"],
        ),
        (
            "admin:household_individual_changelist",
            {"q": "IND-24", "p": encode_cursor(Cursor(value="IND-24-0000.0003", is_reverse=1, number=2))},
            ["IND-24-0000.0001", "IND-24-0000.0002"],
        ),
        (
            "admin:household_household_changelist",
            {"q": "HH-24"},
            ["HH-24-0000.0001", "HH-24-0000.0002", "HH-24-0000.0003"],
        ),
        (
            "admin:household_household_changelist",
            {"q": "HH-24", "p": encode_cursor(Cursor(value="HH-24-0000.0001", is_reverse=0, number=2))},
            ["HH-24-0000.0002", "HH-24-0000.0003"],
        ),
        (
            "admin:household_household_changelist",
            {"q": "HH-24", "p": encode_cursor(Cursor(value="HH-24-0000.0003", is_reverse=1, number=2))},
            ["HH-24-0000.0001", "HH-24-0000.0002"],
        ),
    ],
    ids=[
        "individual-first",
        "individual-next",
        "individual-previous",
        "household-first",
        "household-next",
        "household-previous",
    ],
)
def test_changelist_search_by_own_unicef_id_pages_through_results(
    paged_population, staff_client, url_name, params, expected
):
    response = staff_client.get(reverse(url_name), {**params, **paged_population})

    assert [obj.unicef_id for obj in response.context["cl"].result_list] == expected
