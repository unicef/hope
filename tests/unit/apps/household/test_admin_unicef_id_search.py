"""Search by unicef_id in the Household/Individual admin must prefix-match, not scan."""

from django.contrib.admin.sites import AdminSite
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
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


def test_individual_search_by_unicef_id_emits_prefix_like_without_upper(population, staff_request):
    model_admin = IndividualAdmin(Individual, AdminSite())

    sql = search_sql(model_admin, staff_request, "IND-24-0000.0001")

    assert "LIKE IND-24-0000.0001%" in sql
    assert "UPPER" not in sql


def test_individual_search_by_household_unicef_id_returns_household_members(population, staff_request):
    model_admin = IndividualAdmin(Individual, AdminSite())

    queryset, _ = model_admin.get_search_results(
        staff_request, model_admin.get_queryset(staff_request), "HH-24-0000.0001"
    )

    assert set(queryset) == set(population["household"].individuals.all())
    assert population["other"] not in queryset


@pytest.mark.parametrize("term", ["Kowalski", "IND", "XYZ-24-0000.0001"])
def test_individual_search_by_non_unicef_id_term_falls_back_to_default_search(population, staff_request, term):
    model_admin = IndividualAdmin(Individual, AdminSite())

    sql = search_sql(model_admin, staff_request, term)

    assert "UPPER" in sql


def test_individual_search_by_name_still_matches(population, staff_request):
    model_admin = IndividualAdmin(Individual, AdminSite())

    queryset, _ = model_admin.get_search_results(staff_request, model_admin.get_queryset(staff_request), "Kowalski")

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
