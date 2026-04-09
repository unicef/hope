from unittest.mock import Mock, patch

import pytest

from extras.test_utils.factories import CountryFactory
from hope.apps.geo.celery_tasks import import_areas_from_csv_async_task, import_areas_from_csv_async_task_action
from hope.models import Area, AreaType, AsyncJob, Country

pytestmark = pytest.mark.django_db


@pytest.fixture
def country() -> Country:
    return CountryFactory(name="Testland", short_name="Testland", iso_code2="TL", iso_code3="TLD", iso_num="999")


def create_async_job(csv_data: str, delay_mptt_updates: bool = False) -> AsyncJob:
    return AsyncJob.objects.create(
        type="JOB_TASK",
        action="hope.apps.geo.celery_tasks.import_areas_from_csv_async_task_action",
        config={"csv_data": csv_data, "delay_mptt_updates": delay_mptt_updates},
    )


@pytest.mark.parametrize("delay_mptt_updates", [True, False])
def test_import_areas_from_csv(country: Country, delay_mptt_updates: bool) -> None:
    """
    Test that the celery task correctly creates and updates AreaTypes and Areas,
    including their hierarchy.
    """
    assert Area.objects.count() == 0
    assert AreaType.objects.count() == 0

    csv_data_create = (
        "Country,State,County,country_pcode,state_pcode,county_pcode\n"
        "Testland,State1,County1,TL,TL01,TL01001\n"
        "Testland,State1,County2,TL,TL01,TL01002\n"
        "Testland,State2,County3,TL,TL02,TL02001\n"
    )

    import_areas_from_csv_async_task_action(create_async_job(csv_data_create, delay_mptt_updates))

    assert AreaType.objects.count() == 3  # Country, State, County
    assert Area.objects.count() == 6  # 1 country area, 2 states, 3 counties

    country_area = Area.objects.get(p_code="TL")
    state1 = Area.objects.get(p_code="TL01")
    state2 = Area.objects.get(p_code="TL02")
    county1 = Area.objects.get(p_code="TL01001")
    county2 = Area.objects.get(p_code="TL01002")
    county3 = Area.objects.get(p_code="TL02001")

    assert country_area.parent is None
    assert state1.parent == country_area
    assert state2.parent == country_area
    assert county1.parent == state1
    assert county2.parent == state1
    assert county3.parent == state2

    csv_data_update = (
        "Country,State,County,country_pcode,state_pcode,county_pcode\n"
        "Testland,New State1 Name,County1,TL,TL01,TL01001\n"
    )

    import_areas_from_csv_async_task_action(create_async_job(csv_data_update, delay_mptt_updates))

    assert Area.objects.count() == 6
    updated_state1 = Area.objects.get(p_code="TL01")
    assert updated_state1.name == "New State1 Name"


def test_import_areas_from_csv_task_action_preserves_existing_errors_on_success(country: Country) -> None:
    csv_data = "Country,State,County,country_pcode,state_pcode,county_pcode\nTestland,State1,County1,TL,TL01,TL01001\n"
    job = create_async_job(csv_data)
    job.errors = {"error": "previous failure"}
    job.save(update_fields=["errors"])

    import_areas_from_csv_async_task_action(job)

    job.refresh_from_db()
    assert job.errors == {"error": "previous failure"}


def test_import_areas_from_empty_csv() -> None:
    """
    Test that the celery task raises an IndexError when the csv data is empty.
    The validation is expected to happen before calling the task.
    """
    csv_data_empty = ""
    with pytest.raises(IndexError):
        import_areas_from_csv_async_task_action(create_async_job(csv_data_empty))

    csv_data_header_only = "Country,State,County,country_pcode,state_pcode,county_pcode\n"
    with pytest.raises(IndexError):
        import_areas_from_csv_async_task_action(create_async_job(csv_data_header_only))


def test_import_areas_from_csv_no_country() -> None:
    """
    Test that the celery task raises Country.DoesNotExist when the country is not in DB.
    The validation is expected to happen before calling the task.
    """
    assert Country.objects.count() == 0
    csv_data = "Country,State,country_pcode,state_pcode\nTestland,State1,TL,TL01"
    with pytest.raises(Country.DoesNotExist):
        import_areas_from_csv_async_task_action(create_async_job(csv_data))


def test_import_areas_from_no_country_column(country: Country) -> None:
    """
    Test that the celery task raises KeyError when there is no 'Country' column.
    The validation is expected to happen before calling the task.
    """
    csv_data = "WrongHeader,State,country_pcode,state_pcode\nTestland,State1,TL,TL01"
    with pytest.raises(KeyError):
        import_areas_from_csv_async_task_action(create_async_job(csv_data))


@patch.object(AsyncJob, "queue")
def test_import_areas_from_csv_task_schedules_async_job(mock_queue: Mock) -> None:
    csv_data = "Country,State,country_pcode,state_pcode\nTestland,State1,TL,TL01"

    import_areas_from_csv_async_task(csv_data, delay_mptt_updates=True)

    job = AsyncJob.objects.get()

    assert job.owner is None
    assert job.type == "JOB_TASK"
    assert job.action == "hope.apps.geo.celery_tasks.import_areas_from_csv_async_task_action"
    assert job.config == {"csv_data": csv_data, "delay_mptt_updates": True}
    assert job.group_key == "import_areas_from_csv_async_task"
    assert job.description == "Import areas from CSV"
    mock_queue.assert_called_once_with()
