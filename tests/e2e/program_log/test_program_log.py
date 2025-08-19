from datetime import datetime

import pytest
from e2e.helpers.fixtures import get_program_with_dct_type_and_name
from e2e.page_object.program_log.payment_log import ProgramLog
from e2e.page_object.programme_details.programme_details import ProgrammeDetails

from hope.apps.account.models import User
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def standard_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "TEST")


@pytest.mark.usefixtures("login")
class TestProgrammeLog:
    def test_smoke_program_log(
        self,
        standard_program: Program,
        pageProgramLog: ProgramLog,
        pageProgrammeDetails: ProgrammeDetails,
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("Test Program")
        pageProgrammeDetails.getButtonFinishProgram().click()
        pageProgrammeDetails.clickButtonFinishProgramPopup()
        pageProgramLog.getNavProgramLog().click()
        assert "Update" in pageProgramLog.getActionCell().text
        assert datetime.today().strftime("%-d %b %Y %H") in pageProgramLog.getTimestampCell().text
        user = User.objects.first()
        assert f"{user.first_name} {user.last_name}" in pageProgramLog.getUserCell().text
        assert "Programme" in pageProgramLog.getContentTypeCell().text
        assert pageProgramLog.getObjectRepresentationCell().text
        assert "status" in pageProgramLog.getChangeKeyCell().text
        assert "ACTIVE" in pageProgramLog.getFromValueCell().text
        assert "FINISHED" in pageProgramLog.getToValueCell().text
        assert "Rows per page: 20 1–1 of 1" in pageProgramLog.getTablePagination().text.replace("\n", " ")

    def test_smoke_activity_log(
        self,
        standard_program: Program,
        pageProgramLog: ProgramLog,
        pageProgrammeDetails: ProgrammeDetails,
    ) -> None:
        pageProgrammeDetails.selectGlobalProgramFilter("Test Program")
        pageProgrammeDetails.getButtonFinishProgram().click()
        pageProgrammeDetails.clickButtonFinishProgramPopup()
        pageProgrammeDetails.selectGlobalProgramFilter("All Programmes")
        pageProgramLog.getNavActivityLog().click()
        assert "Activity Log" in pageProgramLog.getPageHeaderTitle().text
        assert "Update" in pageProgramLog.getActionCell().text
        assert datetime.today().strftime("%-d %b %Y %H") in pageProgramLog.getTimestampCell().text
        user = User.objects.first()
        assert f"{user.first_name} {user.last_name}" in pageProgramLog.getUserCell().text
        assert "Programme" in pageProgramLog.getContentTypeCell().text
        assert pageProgramLog.getObjectRepresentationCell().text
        assert "status" in pageProgramLog.getChangeKeyCell().text
        assert "ACTIVE" in pageProgramLog.getFromValueCell().text
        assert "FINISHED" in pageProgramLog.getToValueCell().text
        assert "Rows per page: 20 1–1 of 1" in pageProgramLog.getTablePagination().text.replace("\n", " ")
