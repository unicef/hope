from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta
from page_object.programme_details.programme_details import ProgrammeDetails
from page_object.programme_management.programme_management import ProgrammeManagement

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def social_worker_program() -> Program:
    yield get_program_with_dct_type_and_name("Worker Program", "WORK", DataCollectingType.Type.SOCIAL)


@pytest.fixture
def normal_program() -> Program:
    yield get_program_with_dct_type_and_name("Normal Program", "NORM", DataCollectingType.Type.STANDARD)


@pytest.fixture
def active_program() -> Program:
    yield get_program_with_dct_type_and_name("Active Program", "ACTI", status=Program.ACTIVE)


@pytest.fixture
def draft_program() -> Program:
    yield get_program_with_dct_type_and_name("Draft Program", "DRAF", status=Program.DRAFT)


@pytest.fixture
def finished_program() -> Program:
    yield get_program_with_dct_type_and_name("Finished Program", "FINI", status=Program.FINISHED)


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


@pytest.mark.usefixtures("login")
class TestDrawer:
    def test_social_worker_program_drawer_order(
        self,
        social_worker_program: Program,
        pageProgrammeManagement: ProgrammeManagement,
        pageProgrammeDetails: ProgrammeDetails,
    ) -> None:
        pageProgrammeManagement.selectGlobalProgramFilter("Worker Program")
        assert "Worker Program" in pageProgrammeDetails.getHeaderTitle().text
        expected_menu_items = [
            "Country Dashboard",
            "Registration Data Import",
            "People",
            "Program Details",
            "Targeting",
            "Payment Module",
            "Payment Verification",
            "Grievance",
            "Accountability",
            "Programme Users",
            "Program Log",
        ]
        actual_menu_items = pageProgrammeManagement.getDrawerItems().text.split("\n")
        assert expected_menu_items == actual_menu_items

    def test_normal_program_drawer_order(
        self,
        normal_program: Program,
        pageProgrammeManagement: ProgrammeManagement,
        pageProgrammeDetails: ProgrammeDetails,
    ) -> None:
        pageProgrammeManagement.selectGlobalProgramFilter("Normal Program")
        assert "Normal Program" in pageProgrammeDetails.getHeaderTitle().text
        expected_menu_items = [
            "Country Dashboard",
            "Registration Data Import",
            "Program Population",
            "Program Details",
            "Targeting",
            "Payment Module",
            "Payment Verification",
            "Grievance",
            "Accountability",
            "Programme Users",
            "Program Log",
        ]
        actual_menu_items = pageProgrammeManagement.getDrawerItems().text.split("\n")
        assert expected_menu_items == actual_menu_items

    def test_all_program_drawer_order(
        self,
        social_worker_program: Program,
        pageProgrammeManagement: ProgrammeManagement,
        pageProgrammeDetails: ProgrammeDetails,
    ) -> None:
        expected_menu_items = [
            "Country Dashboard",
            "Programs",
            "Managerial Console",
            "Grievance",
            "Reporting",
            "Activity Log",
        ]
        actual_menu_items = pageProgrammeManagement.getDrawerItems().text.split("\n")
        assert expected_menu_items == actual_menu_items

    def test_inactive_draft_subheader(
        self,
        draft_program: Program,
        active_program: Program,
        finished_program: Program,
        pageProgrammeManagement: ProgrammeManagement,
        pageProgrammeDetails: ProgrammeDetails,
    ) -> None:
        draft_program_name = draft_program.name
        active_program_name = active_program.name
        finished_program_name = finished_program.name

        pageProgrammeManagement.selectGlobalProgramFilter(draft_program_name)
        assert draft_program_name in pageProgrammeDetails.getHeaderTitle().text
        assert pageProgrammeDetails.getDrawerInactiveSubheader().text == "program inactive"

        pageProgrammeManagement.selectGlobalProgramFilter(active_program_name)
        assert active_program_name in pageProgrammeDetails.getHeaderTitle().text
        with pytest.raises(Exception):
            pageProgrammeDetails.getDrawerInactiveSubheader(timeout=0.05)

        # first have to search Finished program because of default filtering
        pageProgrammeManagement.selectGlobalProgramFilter(finished_program_name)
        assert finished_program_name in pageProgrammeDetails.getHeaderTitle().text
        assert pageProgrammeDetails.getDrawerInactiveSubheader().text == "program inactive"
