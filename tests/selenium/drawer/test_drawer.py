from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program
from tests.selenium.page_object.programme_details.programme_details import (
    ProgrammeDetails,
)
from tests.selenium.page_object.programme_management.programme_management import (
    ProgrammeManagement,
)

pytestmark = pytest.mark.django_db()


@pytest.fixture
def social_worker_program() -> Program:
    yield get_social_program_with_dct_type_and_name("Worker Program", "WORK", DataCollectingType.Type.SOCIAL)


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
    name: str,
    programme_code: str,
    dct_type: str = DataCollectingType.Type.STANDARD,
    status: str = Program.ACTIVE,
    beneficiary_group_name: str = "Main Menu",
) -> Program:
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name=beneficiary_group_name).first()
    program = ProgramFactory(
        name=name,
        programme_code=programme_code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        beneficiary_group=beneficiary_group,
    )
    return program


def get_social_program_with_dct_type_and_name(
    name: str, programme_code: str, dct_type: str = DataCollectingType.Type.SOCIAL, status: str = Program.ACTIVE
) -> Program:
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="People").first()
    program = ProgramFactory(
        name=name,
        programme_code=programme_code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        beneficiary_group=beneficiary_group,
    )
    return program


@pytest.mark.usefixtures("login")
class TestDrawer:
    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
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
            "Programme Details",
            "Targeting",
            "Payment Module",
            "Payment Verification",
            "Grievance",
            "Accountability",
            "Programme Users",
            "Programme Log",
        ]
        actual_menu_items = pageProgrammeManagement.getDrawerItems().text.split("\n")
        assert expected_menu_items == actual_menu_items

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
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
            "Main Menu",
            "Programme Details",
            "Targeting",
            "Payment Module",
            "Payment Verification",
            "Grievance",
            "Accountability",
            "Programme Users",
            "Programme Log",
        ]
        actual_menu_items = pageProgrammeManagement.getDrawerItems().text.split("\n")
        assert expected_menu_items == actual_menu_items

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
    def test_all_program_drawer_order(
        self,
        social_worker_program: Program,
        pageProgrammeManagement: ProgrammeManagement,
        pageProgrammeDetails: ProgrammeDetails,
    ) -> None:
        expected_menu_items = [
            "Country Dashboard",
            "Programmes",
            "Managerial Console",
            "Grievance",
            "Activity Log",
        ]
        actual_menu_items = pageProgrammeManagement.getDrawerItems().text.split("\n")
        assert expected_menu_items == actual_menu_items

    @pytest.mark.skip(reason="Unskip after REST refactoring is complete")
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
        assert pageProgrammeDetails.getDrawerInactiveSubheader().text == "programme inactive"

        pageProgrammeManagement.selectGlobalProgramFilter(active_program_name)
        assert active_program_name in pageProgrammeDetails.getHeaderTitle().text
        with pytest.raises(Exception):
            pageProgrammeDetails.getDrawerInactiveSubheader(timeout=0.05)

        # first have to search Finished program because of default filtering
        pageProgrammeManagement.selectGlobalProgramFilter(finished_program_name)
        assert finished_program_name in pageProgrammeDetails.getHeaderTitle().text
        assert pageProgrammeDetails.getDrawerInactiveSubheader().text == "programme inactive"
