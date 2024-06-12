import pytest
from programme_population.households import People

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.usefixtures("login")
class TestSmokePeople:
    def test_smoke_page_people(
            self, pagePeople: People
    ) -> None:
        pagePeople.selectGlobalProgramFilter("Test Programm").click()
        pagePeople.getNavPeople().click()
