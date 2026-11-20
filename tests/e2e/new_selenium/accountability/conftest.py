import pytest

from extras.test_utils.factories import (
    HouseholdFactory,
    IndividualFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    UserFactory,
)
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.household.const import REFUGEE
from hope.models import BeneficiaryGroup, BusinessArea, Household, PaymentPlan, Program, User

PROGRAM_NAME = "Accountability Programme"
TARGET_POPULATION_NAME = "Accountability Target Population"


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(
        business_area=business_area,
        name=PROGRAM_NAME,
        status=Program.ACTIVE,
        beneficiary_group=BeneficiaryGroup.objects.get(name="Main Menu"),
    )


@pytest.fixture
def author() -> User:
    return UserFactory(first_name="Alice", last_name="Author")


@pytest.fixture
def target_population(program: Program, author: User) -> PaymentPlan:
    return PaymentPlanFactory(
        name=TARGET_POPULATION_NAME,
        status=PaymentPlan.Status.TP_LOCKED,
        created_by=author,
        business_area=program.business_area,
        program_cycle=ProgramCycleFactory(program=program),
    )


@pytest.fixture
def household(program: Program) -> Household:
    # Survey and message recipients are only households whose head has a valid phone number.
    head = IndividualFactory(
        household=None,
        business_area=program.business_area,
        program=program,
        phone_no="+48123456777",
        phone_no_alternative="+48123456789",
    )
    household = HouseholdFactory(
        program=program,
        business_area=program.business_area,
        residence_status=REFUGEE,
        head_of_household=head,
    )
    head.household = household
    head.save()
    return household


def open_accountability_page(browser: HopeTestBrowser, program: Program, page: str) -> None:
    browser.open(f"/{program.business_area.slug}/programs/{program.code}/details/{program.code}")
    browser.assert_text(program.name, 'h5[data-cy="page-header-title"]')
    browser.open_nav_section("Accountability")
    browser.click(f'a[data-cy="nav-{page}"]')
    browser.assert_text(page, 'h5[data-cy="page-header-title"]')
