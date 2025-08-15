import pytest
from extras.test_utils.factories.geo import CountryFactory

from hct_mis_api.apps.geo.celery_tasks import import_areas_from_csv_task
from hct_mis_api.apps.geo.models import Area, AreaType, Country

pytestmark = pytest.mark.django_db


@pytest.fixture
def country() -> Country:
    return CountryFactory(name="Testland", short_name="Testland", iso_code2="TL", iso_code3="TLD", iso_num="999")


def test_import_areas_from_csv_task(country: Country) -> None:
    """
    Test that the celery task correctly creates and updates AreaTypes and Areas,
    including their hierarchy.
    """
    assert Area.objects.count() == 0
    assert AreaType.objects.count() == 0

    # Test creation
    csv_data_create = (
        "Country,State,County,country_pcode,state_pcode,county_pcode\n"
        "Testland,State1,County1,TL,TL01,TL01001\n"
        "Testland,State1,County2,TL,TL01,TL01002\n"
        "Testland,State2,County3,TL,TL02,TL02001\n"
    )

    import_areas_from_csv_task(csv_data_create)

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

    # Test update
    csv_data_update = (
        "Country,State,County,country_pcode,state_pcode,county_pcode\n"
        "Testland,New State1 Name,County1,TL,TL01,TL01001\n"
    )

    import_areas_from_csv_task(csv_data_update)

    assert Area.objects.count() == 6  # No new areas created
    updated_state1 = Area.objects.get(p_code="TL01")
    assert updated_state1.name == "New State1 Name"
