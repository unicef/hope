from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta
from e2e.page_object.programme_details.programme_details import ProgrammeDetails
from e2e.page_object.programme_management.programme_management import (
    ProgrammeManagement,
)
from extras.test_utils.factories.core import DataCollectingTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from selenium.common.exceptions import NoSuchElementException

from hope.models.core import DataCollectingType
from hope.models.program import BeneficiaryGroup, Program

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
    return ProgramFactory(
        name=name,
        programme_code=programme_code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        beneficiary_group=beneficiary_group,
    )


def get_social_program_with_dct_type_and_name(
    name: str,
    programme_code: str,
    dct_type: str = DataCollectingType.Type.SOCIAL,
    status: str = Program.ACTIVE,
) -> Program:
    dct = DataCollectingTypeFactory(type=dct_type)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="People").first()
    return ProgramFactory(
        name=name,
        programme_code=programme_code,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
        beneficiary_group=beneficiary_group,
    )


@pytest.mark.usefixtures("login")
class TestDrawer:
    def test_social_worker_program_drawer_order(
        self,
        social_worker_program: Program,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        page_programme_management.select_global_program_filter("Worker Program")
        assert "Worker Program" in page_programme_details.get_header_title().text
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
        actual_menu_items = page_programme_management.get_drawer_items().text.split("\n")
        assert expected_menu_items == actual_menu_items

    def test_normal_program_drawer_order(
        self,
        normal_program: Program,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        page_programme_management.select_global_program_filter("Normal Program")
        assert "Normal Program" in page_programme_details.get_header_title().text
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
        actual_menu_items = page_programme_management.get_drawer_items().text.split("\n")
        assert expected_menu_items == actual_menu_items

    def test_all_program_drawer_order(
        self,
        social_worker_program: Program,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        expected_menu_items = [
            "Country Dashboard",
            "Programmes",
            "Managerial Console",
            "Grievance",
            "Activity Log",
        ]
        actual_menu_items = page_programme_management.get_drawer_items().text.split("\n")
        assert expected_menu_items == actual_menu_items

    def test_inactive_draft_subheader(
        self,
        draft_program: Program,
        active_program: Program,
        finished_program: Program,
        page_programme_management: ProgrammeManagement,
        page_programme_details: ProgrammeDetails,
    ) -> None:
        draft_program_name = draft_program.name
        active_program_name = active_program.name
        finished_program_name = finished_program.name

        page_programme_management.select_global_program_filter(draft_program_name)
        assert draft_program_name in page_programme_details.get_header_title().text
        assert page_programme_details.get_drawer_inactive_subheader().text == "Programme Inactive"

        page_programme_management.select_global_program_filter(active_program_name)
        assert active_program_name in page_programme_details.get_header_title().text
        with pytest.raises(NoSuchElementException):
            page_programme_details.get_drawer_inactive_subheader(timeout=0.05)

        # first have to search Finished program because of default filtering
        page_programme_management.select_global_program_filter(finished_program_name)
        assert finished_program_name in page_programme_details.get_header_title().text
        assert page_programme_details.get_drawer_inactive_subheader().text == "Programme Inactive"
