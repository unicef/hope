from datetime import datetime

import pytest

from e2e.helpers.fixtures import get_program_with_dct_type_and_name
from e2e.page_object.program_log.payment_log import ProgramLog
from e2e.page_object.programme_details.programme_details import ProgrammeDetails

from hope.models.user import User
from hope.models.program import Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def standard_program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "TEST")


@pytest.mark.usefixtures("login")
class TestProgrammeLog:
    def test_smoke_program_log(
        self,
        standard_program: Program,
        page_program_log: ProgramLog,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        page_programme_details.select_global_program_filter("Test Program")
        page_programme_details.get_button_finish_program().click()
        page_programme_details.click_button_finish_program_popup()
        page_program_log.get_nav_program_log().click()
        assert "Update" in page_program_log.get_action_cell().text
        assert datetime.today().strftime("%-d %b %Y %H") in page_program_log.get_timestamp_cell().text
        user = User.objects.first()
        assert f"{user.first_name} {user.last_name}" in page_program_log.get_user_cell().text
        assert "Programme" in page_program_log.get_content_type_cell().text
        assert page_program_log.get_object_representation_cell().text
        assert "status" in page_program_log.get_change_key_cell().text
        assert "ACTIVE" in page_program_log.get_from_value_cell().text
        assert "FINISHED" in page_program_log.get_to_value_cell().text
        assert "Rows per page: 20 1–1 of 1" in page_program_log.get_table_pagination().text.replace("\n", " ")

    def test_smoke_activity_log(
        self,
        standard_program: Program,
        page_program_log: ProgramLog,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        page_programme_details.select_global_program_filter("Test Program")
        page_programme_details.get_button_finish_program().click()
        page_programme_details.click_button_finish_program_popup()
        page_programme_details.select_global_program_filter("All Programmes")
        page_program_log.get_nav_activity_log().click()
        assert "Activity Log" in page_program_log.get_page_header_title().text
        assert "Update" in page_program_log.get_action_cell().text
        assert datetime.today().strftime("%-d %b %Y %H") in page_program_log.get_timestamp_cell().text
        user = User.objects.first()
        assert f"{user.first_name} {user.last_name}" in page_program_log.get_user_cell().text
        assert "Programme" in page_program_log.get_content_type_cell().text
        assert page_program_log.get_object_representation_cell().text
        assert "status" in page_program_log.get_change_key_cell().text
        assert "ACTIVE" in page_program_log.get_from_value_cell().text
        assert "FINISHED" in page_program_log.get_to_value_cell().text
        assert "Rows per page: 20 1–1 of 1" in page_program_log.get_table_pagination().text.replace("\n", " ")
