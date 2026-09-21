import pytest

from extras.test_utils.factories import BusinessAreaFactory
from hope.apps.grievance.constants import PRESET_MINE, PRESET_NEEDS_ASSIGNMENT
from hope.apps.grievance.utils import my_tasks_url
from hope.models import BusinessArea

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory()


def test_needs_assignment_preset_is_carried_in_the_query_string(business_area: BusinessArea) -> None:
    url = my_tasks_url(business_area, PRESET_NEEDS_ASSIGNMENT)

    assert url.endswith(f"/{business_area.slug}/programs/all/grievance/my-tasks?tab=needs-assignment")


def test_sensitive_is_carried_in_the_query_string(business_area: BusinessArea) -> None:
    url = my_tasks_url(business_area, PRESET_MINE, sensitive=True)

    assert url.endswith(f"/{business_area.slug}/programs/all/grievance/my-tasks?tab=mine&sensitive=true")


def test_non_sensitive_is_carried_in_the_query_string(business_area: BusinessArea) -> None:
    url = my_tasks_url(business_area, PRESET_MINE, sensitive=False)

    assert url.endswith(f"/{business_area.slug}/programs/all/grievance/my-tasks?tab=mine&sensitive=false")


def test_url_without_sensitive_carries_only_the_tab(business_area: BusinessArea) -> None:
    url = my_tasks_url(business_area, PRESET_MINE)

    assert url.endswith(f"/{business_area.slug}/programs/all/grievance/my-tasks?tab=mine")


def test_overdue_narrows_a_preset_rather_than_replacing_it(business_area: BusinessArea) -> None:
    url = my_tasks_url(business_area, PRESET_MINE, overdue=True)

    assert url.endswith(f"/{business_area.slug}/programs/all/grievance/my-tasks?tab=mine&overdue=true")


def test_sensitive_and_overdue_compose(business_area: BusinessArea) -> None:
    url = my_tasks_url(business_area, PRESET_MINE, overdue=True, sensitive=True)

    assert url.endswith(f"/{business_area.slug}/programs/all/grievance/my-tasks?tab=mine&sensitive=true&overdue=true")


def test_url_is_absolute(business_area: BusinessArea) -> None:
    url = my_tasks_url(business_area, PRESET_MINE)

    assert url.startswith("http")
