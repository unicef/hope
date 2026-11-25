from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FlexibleAttributeForPDUFactory,
    PartnerFactory,
    PaymentPlanPurposeFactory,
    RegistrationDataImportFactory,
    RoleAssignmentFactory,
    RoleFactory,
)
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import BusinessArea, Partner, PaymentPlanPurpose, Program, ProgramCycle, User

BA_PURPOSE_NAME = "BA Purpose"
SECOND_BA_PURPOSE_NAME = "Second BA Purpose"
OTHER_BA_PURPOSE_NAME = "Other BA Purpose"
TEN_PURPOSE_NAMES = (
    "Purpose 1",
    "Purpose 2",
    "Purpose 3",
    "Purpose 4",
    "Purpose 5",
    "Purpose 6",
    "Purpose 7",
    "Purpose 8",
    "Purpose 9",
    "Purpose 10",
)


@pytest.fixture
def ba_purpose() -> PaymentPlanPurpose:
    return PaymentPlanPurposeFactory(name=BA_PURPOSE_NAME)


@pytest.fixture
def second_ba_purpose() -> PaymentPlanPurpose:
    return PaymentPlanPurposeFactory(name=SECOND_BA_PURPOSE_NAME)


@pytest.fixture
def other_ba_purpose() -> PaymentPlanPurpose:
    # limit_to a different business area so it is scoped out of the current BA
    purpose = PaymentPlanPurposeFactory(name=OTHER_BA_PURPOSE_NAME)
    purpose.limit_to.add(BusinessAreaFactory())
    return purpose


@pytest.fixture
def purpose() -> PaymentPlanPurpose:
    return PaymentPlanPurposeFactory(name=BA_PURPOSE_NAME)


@pytest.fixture
def program_with_purpose(business_area: BusinessArea, ba_purpose: PaymentPlanPurpose) -> Program:
    prog = ProgramFactory(business_area=business_area, status=Program.DRAFT)
    prog.payment_plan_purposes.add(ba_purpose)
    # Create a payment plan that uses this purpose so it shows as locked (used in PP)
    cycle = ProgramCycleFactory(program=prog)
    pp = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        payment_plan_purposes=[ba_purpose],
    )
    pp.payment_plan_purposes.set([ba_purpose])
    return prog


@pytest.fixture
def ten_ba_purposes() -> list[PaymentPlanPurpose]:
    return [PaymentPlanPurposeFactory(name=name) for name in TEN_PURPOSE_NAMES]


@pytest.fixture
def program_with_ten_purposes(business_area: BusinessArea, ten_ba_purposes: list[PaymentPlanPurpose]) -> Program:
    prog = ProgramFactory(business_area=business_area, status=Program.DRAFT)
    prog.payment_plan_purposes.set(ten_ba_purposes)
    return prog


def days_from_today(days: int) -> date:
    return timezone.now().date() + timedelta(days=days)


def details_url(program: Program) -> str:
    return f"/{program.business_area.slug}/programs/{program.code}/details/{program.code}"


def _programme(business_area: BusinessArea, status: str, *cycles: tuple[str, str, int, int | None]) -> Program:
    program = ProgramFactory(
        business_area=business_area,
        status=status,
        start_date=days_from_today(-30),
        end_date=days_from_today(30),
        cycle=False,
    )
    for title, cycle_status, start, end in cycles:
        ProgramCycleFactory(
            program=program,
            title=title,
            status=cycle_status,
            start_date=days_from_today(start),
            end_date=days_from_today(end) if end is not None else None,
        )
    return program


@pytest.fixture
def draft_programme(business_area: BusinessArea) -> Program:
    return _programme(business_area, Program.DRAFT, ("Default Programme Cycle", ProgramCycle.FINISHED, -25, 10))


@pytest.fixture
def active_programme_with_finished_cycle(business_area: BusinessArea) -> Program:
    return _programme(business_area, Program.ACTIVE, ("Default Programme Cycle", ProgramCycle.FINISHED, -25, 0))


@pytest.fixture
def active_programme_with_active_cycle(business_area: BusinessArea) -> Program:
    return _programme(business_area, Program.ACTIVE, ("Default Programme Cycle", ProgramCycle.ACTIVE, -25, 0))


@pytest.fixture
def programme_with_open_ended_cycle(business_area: BusinessArea) -> Program:
    program = _programme(business_area, Program.ACTIVE, ("Default Programme Cycle", ProgramCycle.DRAFT, -25, None))
    PaymentPlanFactory(
        program_cycle=program.cycles.get(),
        business_area=business_area,
        total_entitled_quantity_usd=Decimal("1234.99"),
        total_delivered_quantity_usd=Decimal("50.01"),
        total_undelivered_quantity_usd=Decimal("1184.98"),
    )
    return program


@pytest.fixture
def programme_with_draft_cycle(business_area: BusinessArea) -> Program:
    return _programme(business_area, Program.ACTIVE, ("Default Programme Cycle", ProgramCycle.DRAFT, 0, 1))


@pytest.fixture
def programme_with_three_draft_cycles(business_area: BusinessArea) -> Program:
    return _programme(
        business_area,
        Program.ACTIVE,
        ("First Cycle", ProgramCycle.DRAFT, -25, 10),
        ("Second Cycle", ProgramCycle.DRAFT, 11, 17),
        ("Third Cycle", ProgramCycle.DRAFT, 18, 20),
    )


@pytest.fixture
def programme_with_mixed_cycles(business_area: BusinessArea) -> Program:
    return _programme(
        business_area,
        Program.ACTIVE,
        ("Draft Cycle", ProgramCycle.DRAFT, -25, 10),
        ("Active Cycle", ProgramCycle.ACTIVE, 11, 17),
        ("Finished Cycle", ProgramCycle.FINISHED, 18, 20),
    )


@pytest.fixture
def programme_with_time_series_field_and_rdi(business_area: BusinessArea) -> Program:
    program = ProgramFactory(business_area=business_area, status=Program.DRAFT)
    FlexibleAttributeForPDUFactory(program=program, label="Time Series Field Name 1", pdu_data__number_of_rounds=2)
    RegistrationDataImportFactory(program=program, business_area=business_area)
    return program


@pytest.fixture
def superuser_of_unhcr(create_super_user: User) -> User:
    create_super_user.partner = Partner.objects.get(name="UNHCR")
    create_super_user.save()
    return create_super_user


@pytest.fixture
def partner_in_business_area(business_area: BusinessArea) -> Partner:
    partner = PartnerFactory(name="Test Partner 1")
    partner.allowed_business_areas.add(business_area)
    RoleAssignmentFactory(
        partner=partner,
        user=None,
        business_area=business_area,
        program=None,
        role=RoleFactory(name="Role in BA"),
    )
    return partner


@pytest.fixture
def partner_without_role() -> Partner:
    return PartnerFactory(name="Test Partner 2")


def navigate_to_programme_management(browser: HopeTestBrowser) -> None:
    browser.click('a[data-cy="nav-Programmes"]')
    browser.wait_for_text("Programme Management", 'h5[data-cy="page-header-title"]')


def fill_programme_create_required_fields(
    browser: HopeTestBrowser,
    *,
    name: str = "Test Programme",
    start_date: str = "2023-05-01",
    end_date: str = "2033-12-12",
    sector: str = "Child Protection",
    payee_type: str = "Household",
    dct: str = "Full",
    beneficiary_group: str = "Main Menu",
    purpose_name: str = BA_PURPOSE_NAME,
    fill_dates: bool = True,
) -> None:
    browser.type('input[name="name"]', name)
    if fill_dates:
        browser.fill_date('input[name="startDate"]', start_date)
        browser.click('input[name="name"]')
        browser.fill_date('input[name="endDate"]', end_date)
        browser.click('input[name="name"]')
    browser.select_dropdown_option("sector", sector)
    browser.select_dropdown_option("payeeType", payee_type)
    browser.select_dropdown_option("dataCollectingTypeCode", dct)
    browser.select_dropdown_option("beneficiaryGroup", beneficiary_group)
    browser.select_chip_option(purpose_name, '[data-cy="input-payment-plan-purposes"]')


def add_time_series_field(
    browser: HopeTestBrowser,
    index: int,
    *,
    label: str,
    subtype: str = "Text",
    num_rounds: str = "1",
    round_names: list[str] = (),
) -> None:
    browser.click('button[data-cy="button-add-time-series-field"]')
    browser.type(f'input[name="pduFields.{index}.label"]', label)
    browser.select_dropdown_option(f"pduFields.{index}.pduData.subtype", subtype)
    browser.click(f'[data-cy="select-pduFields.{index}.pduData.numberOfRounds"]')
    browser.select_listbox_element(num_rounds)
    for ri, rname in enumerate(round_names):
        browser.type(f'input[name="pduFields.{index}.pduData.roundsNames.{ri}"]', rname)


def choose_partner(browser: HopeTestBrowser, name: str, index: int = 0) -> None:
    browser.click(f'div[data-cy="select-partners[{index}].id"]')
    browser.select_option_by_name(name)


def open_create_programme_partners_step(browser: HopeTestBrowser, name: str = "Test Programme") -> None:
    navigate_to_programme_management(browser)
    browser.click('a[data-cy="button-new-program"]')
    fill_programme_create_required_fields(
        browser, name=name, sector="Health", dct="Partial", beneficiary_group="People"
    )
    browser.click('[data-cy="input-cashPlus"]')
    browser.click('button[data-cy="button-next"]')
    browser.wait_for_element_visible('button[data-cy="button-add-time-series-field"]')
    browser.click('button[data-cy="button-next"]')
    browser.wait_for_element_visible('button[data-cy="button-save"]')
