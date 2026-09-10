import pytest

from extras.test_utils.factories import BusinessAreaFactory
from hope.apps.grievance.constants import (
    PRESET_MINE,
    PRESET_MINE_SENSITIVE,
    PRESET_NEEDS_ASSIGNMENT,
)
from hope.apps.grievance.utils import my_tasks_url
from hope.models import BusinessArea

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory()


def test_needs_assignment_preset_is_carried_in_the_query_string(business_area: BusinessArea) -> None:
    url = my_tasks_url(business_area, PRESET_NEEDS_ASSIGNMENT)

    assert url.endswith(f"/{business_area.slug}/programs/all/grievance/tickets/my-tasks?tab=needs-assignment")


def test_mine_sensitive_preset_is_carried_in_the_query_string(business_area: BusinessArea) -> None:
    url = my_tasks_url(business_area, PRESET_MINE_SENSITIVE)

    assert url.endswith(f"/{business_area.slug}/programs/all/grievance/tickets/my-tasks?tab=mine-sensitive")


def test_overdue_narrows_a_preset_rather_than_replacing_it(business_area: BusinessArea) -> None:
    url = my_tasks_url(business_area, PRESET_MINE, overdue=True)

    assert url.endswith(f"/{business_area.slug}/programs/all/grievance/tickets/my-tasks?tab=mine&overdue=true")


def test_url_is_absolute(business_area: BusinessArea) -> None:
    url = my_tasks_url(business_area, PRESET_MINE)

    assert url.startswith("http")
