from django.conf import settings
from django.core.management import call_command

import pytest
from page_object.programme_details.programme_details import ProgrammeDetails

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)

@pytest.fixture
def standard_program() -> Program:
    return get_program_with_dct_type_and_name("Test For Edit", "TEST")


def get_program_with_dct_type_and_name(
        name: str, programme_code: str, dct_type: str = DataCollectingType.Type.STANDARD, status: str = Program.ACTIVE
) -> Program:
    BusinessArea.objects.filter(slug="afghanistan").update(is_payment_plan_applicable=True)
    dct = DataCollectingTypeFactory(type=dct_type)
    program = ProgramFactory(
        name=name,
        programme_code=programme_code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
    )
    return program

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
