import pytest

from extras.test_utils.factories import DataCollectingTypeFactory, ProgramFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import BeneficiaryGroup, BusinessArea, DataCollectingType, Program

pytestmark = pytest.mark.django_db()

PAGE_HEADER_TITLE = 'h5[data-cy="page-header-title"]'
DRAWER_ITEMS = 'div[data-cy="drawer-items"]'
INACTIVE_SUBHEADER = 'div[data-cy="program-inactive-subheader"]'
GLOBAL_PROGRAM_FILTER = 'button[data-cy="global-program-filter"]'

PROGRAMME_MENU_ITEMS = [
    "Country Dashboard",
    "Registration Data Import",
    "{beneficiary_group}",
    "Programme Details",
    "Targeting",
    "Payment Module",
    "Payment Verification",
    "Grievance",
    "Accountability",
    "Programme Users",
    "Programme Log",
]
ALL_PROGRAMMES_MENU_ITEMS = [
    "Country Dashboard",
    "Programmes",
    "Managerial Console",
    "Grievance",
    "Activity Log",
    "Country Search",
]


def create_program(
    business_area: BusinessArea,
    name: str,
    status: str = Program.ACTIVE,
    dct_type: str = DataCollectingType.Type.STANDARD,
    beneficiary_group: str = "Main Menu",
) -> Program:
    return ProgramFactory(
        business_area=business_area,
        name=name,
        status=status,
        data_collecting_type=DataCollectingTypeFactory(type=dct_type),
        beneficiary_group=BeneficiaryGroup.objects.get(name=beneficiary_group),
    )


def programme_url(program: Program) -> str:
    return f"/{program.business_area.slug}/programs/{program.code}/details/{program.code}"


@pytest.fixture
def social_worker_program(business_area: BusinessArea) -> Program:
    return create_program(
        business_area, "Worker Program", dct_type=DataCollectingType.Type.SOCIAL, beneficiary_group="People"
    )


@pytest.fixture
def normal_program(business_area: BusinessArea) -> Program:
    return create_program(business_area, "Normal Program")


@pytest.fixture
def draft_program(business_area: BusinessArea) -> Program:
    return create_program(business_area, "Draft Program", status=Program.DRAFT)


@pytest.fixture
def finished_program(business_area: BusinessArea) -> Program:
    return create_program(business_area, "Finished Program", status=Program.FINISHED)


@pytest.mark.parametrize(
    ("program_fixture", "beneficiary_group"),
    [
        pytest.param("social_worker_program", "People", id="social-worker"),
        pytest.param("normal_program", "Main Menu", id="normal"),
    ],
)
def test_programme_drawer_order(
    request: pytest.FixtureRequest,
    login: HopeTestBrowser,
    program_fixture: str,
    beneficiary_group: str,
) -> None:
    program = request.getfixturevalue(program_fixture)

    login.open(programme_url(program))

    login.assert_text(program.name, PAGE_HEADER_TITLE)
    expected = "\n".join(PROGRAMME_MENU_ITEMS).format(beneficiary_group=beneficiary_group)
    login.assert_exact_text(expected, DRAWER_ITEMS)


def test_all_programmes_drawer_order(business_area: BusinessArea, login: HopeTestBrowser) -> None:
    login.open(f"/{business_area.slug}/programs/all/list")

    login.assert_text("Programme Management", PAGE_HEADER_TITLE)
    login.assert_exact_text("\n".join(ALL_PROGRAMMES_MENU_ITEMS), DRAWER_ITEMS)


@pytest.mark.parametrize("program_fixture", ["draft_program", "finished_program"])
def test_inactive_programme_shows_inactive_subheader(
    request: pytest.FixtureRequest, login: HopeTestBrowser, program_fixture: str
) -> None:
    program = request.getfixturevalue(program_fixture)

    login.open(programme_url(program))

    login.assert_text(program.name, PAGE_HEADER_TITLE)
    login.assert_exact_text("Programme Inactive", INACTIVE_SUBHEADER)


def test_active_programme_has_no_inactive_subheader(normal_program: Program, login: HopeTestBrowser) -> None:
    login.open(programme_url(normal_program))

    login.assert_text(normal_program.name, PAGE_HEADER_TITLE)
    login.assert_exact_text("\n".join(PROGRAMME_MENU_ITEMS).format(beneficiary_group="Main Menu"), DRAWER_ITEMS)
    login.assert_element_absent(INACTIVE_SUBHEADER)


@pytest.mark.parametrize("program_fixture", ["draft_program", "finished_program"])
def test_global_program_filter_switches_to_inactive_programme(
    request: pytest.FixtureRequest, login: HopeTestBrowser, program_fixture: str
) -> None:
    program = request.getfixturevalue(program_fixture)

    login.select_global_program(program.name)

    login.assert_text(program.name, PAGE_HEADER_TITLE)
    login.assert_text(program.name, GLOBAL_PROGRAM_FILTER)
    login.assert_exact_text("Programme Inactive", INACTIVE_SUBHEADER)


def test_global_program_filter_switches_between_active_and_all_programmes(
    normal_program: Program, login: HopeTestBrowser
) -> None:
    login.select_global_program(normal_program.name)
    login.assert_text(normal_program.name, PAGE_HEADER_TITLE)
    login.assert_exact_text("\n".join(PROGRAMME_MENU_ITEMS).format(beneficiary_group="Main Menu"), DRAWER_ITEMS)
    login.assert_element_absent(INACTIVE_SUBHEADER)

    login.select_global_program("All Programmes")

    login.assert_text("Programme Management", PAGE_HEADER_TITLE)
    login.assert_exact_text("\n".join(ALL_PROGRAMMES_MENU_ITEMS), DRAWER_ITEMS)
