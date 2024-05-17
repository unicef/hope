from django.conf import settings
from django.core.management import call_command

import pytest
from page_object.programme_details.programme_details import ProgrammeDetails

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def create_programs() -> None:
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data-selenium.json")
    call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
    return


@pytest.mark.usefixtures("login")
class TestProgrammeDetails:

    def test_program_details(
        self, pageProgrammeDetails: ProgrammeDetails
    ) -> None:
        # Go to Programme Management
        pageProgrammeDetails.getNavProgrammeManagement().click()
        # Check Details page
        assert "New Programme" in pageProgrammeDetails.getHeaderTitle().text
        assert "DRAFT" in pageProgrammeDetails.getProgramStatus().text
        assert "" in pageProgrammeDetails.getLabelStartDate().text
        assert "" in pageProgrammeDetails.getLabelEndDate().text
        assert "" in pageProgrammeDetails.getLabelSelector().text
        assert "" in pageProgrammeDetails.getLabelDataCollectingType().text
        assert "Regular" in pageProgrammeDetails.getLabelFreqOfPayment().text
        assert "-" in pageProgrammeDetails.getLabelAdministrativeAreas().text
        assert "No" in pageProgrammeDetails.getLabelCashPlus().text
        assert "0" in pageProgrammeDetails.getLabelProgramSize().text
