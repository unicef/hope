from collections.abc import Callable
import datetime as dt

from dateutil.relativedelta import relativedelta
import pytest

from extras.test_utils.factories import (
    CurrencyFactory,
    DataCollectingTypeFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import (
    BeneficiaryGroup,
    BusinessArea,
    DataCollectingType,
    Household,
    Individual,
    PaymentPlan,
    Program,
)

from .conftest import payment_plan_url

pytestmark = pytest.mark.django_db()

CREATE_EXCLUSIONS = 'button[data-cy="button-create-exclusions"]'
FEMALE_CHILDREN = 'div[data-cy="label-Female Children"]'
FEMALE_ADULTS = 'div[data-cy="label-Female Adults"]'
MALE_CHILDREN = 'div[data-cy="label-Male Children"]'
MALE_ADULTS = 'div[data-cy="label-Male Adults"]'
TOTAL_HOUSEHOLDS = 'div[data-cy="label-Total Number of Items Groups"]'
TARGETED_INDIVIDUALS = 'div[data-cy="label-Targeted Items"]'
TOTAL_PEOPLE = 'div[data-cy="label-Total Number of People"]'


def _member(household: Household | None, program: Program, sex: str, age: int) -> Individual:
    return IndividualFactory(
        household=household,
        program=program,
        business_area=program.business_area,
        sex=sex,
        birth_date=dt.date.today() - relativedelta(years=age, months=6),
    )


def _locked_payment_plan(business_area: BusinessArea, dct_type: str, beneficiary_group: str) -> PaymentPlan:
    """LOCKED plan with two households: the first one is excluded by the tests.

    First:  1 female child, 1 female adult, 2 male children, 1 male adult (5 members).
    Second: 4 female children, 1 female adult, 1 male child (6 members).
    """
    program = ProgramFactory(
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=DataCollectingTypeFactory(type=dct_type),
        beneficiary_group=BeneficiaryGroup.objects.get(name=beneficiary_group),
    )
    delivery_mechanism = DeliveryMechanismFactory(code="cash", name="Cash")
    fsp = FinancialServiceProviderFactory()
    fsp.delivery_mechanisms.set([delivery_mechanism])
    currency = CurrencyFactory(code="PLN")
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        plan_type=PaymentPlan.PlanType.REGULAR,
        business_area=business_area,
        program_cycle=program.cycles.first(),
        dispersion_start_date=dt.date.today(),
        financial_service_provider=fsp,
        delivery_mechanism=delivery_mechanism,
        currency=currency,
    )
    members = (
        [("MALE", 12), ("MALE", 14), ("FEMALE", 5), ("FEMALE", 30), ("MALE", 30)],
        [("MALE", 2), ("FEMALE", 3), ("FEMALE", 5), ("FEMALE", 7), ("FEMALE", 9), ("FEMALE", 35)],
    )
    for household_members in members:
        (head_sex, head_age), *others = household_members
        head = _member(None, program, head_sex, head_age)
        household = HouseholdFactory(
            head_of_household=head,
            size=len(household_members),
            business_area=business_area,
            program=program,
        )
        for sex, age in others:
            _member(household, program, sex, age)
        PaymentFactory(parent=payment_plan, household=household, collector=head, currency=currency, excluded=False)
    payment_plan.update_population_count_fields()
    payment_plan.update_money_fields()
    return payment_plan


@pytest.fixture
def locked_household_payment_plan(business_area: BusinessArea) -> PaymentPlan:
    return _locked_payment_plan(business_area, DataCollectingType.Type.STANDARD, "Main Menu")


@pytest.fixture
def locked_people_payment_plan(business_area: BusinessArea) -> PaymentPlan:
    return _locked_payment_plan(business_area, DataCollectingType.Type.SOCIAL, "People")


def excluded_household(payment_plan: PaymentPlan) -> Household:
    return payment_plan.payment_items.get(household__size=5).household


def household_id(household: Household) -> str:
    return household.unicef_id


def adult_male_member_id(household: Household) -> str:
    return household.individuals.get(sex="MALE", birth_date__lte=dt.date.today() - relativedelta(years=18)).unicef_id


def summary(browser: HopeTestBrowser, labels: list[str]) -> list[str]:
    return [browser.get_text(label).split("\n")[-1] for label in labels]


@pytest.mark.parametrize(
    ("payment_plan_fixture", "ids_input", "excluded_id", "labels", "before", "after"),
    [
        pytest.param(
            "locked_household_payment_plan",
            '[data-cy="input-households-ids"] input',
            household_id,
            [FEMALE_CHILDREN, FEMALE_ADULTS, MALE_CHILDREN, MALE_ADULTS, TOTAL_HOUSEHOLDS, TARGETED_INDIVIDUALS],
            ["5", "2", "3", "1", "2", "11"],
            ["4", "1", "1", "0", "1", "6"],
            id="households",
        ),
        pytest.param(
            "locked_people_payment_plan",
            '[data-cy="input-beneficiaries-ids"] input',
            adult_male_member_id,
            [FEMALE_CHILDREN, FEMALE_ADULTS, MALE_CHILDREN, MALE_ADULTS, TOTAL_PEOPLE],
            ["5", "2", "3", "1", "2"],
            ["4", "1", "1", "0", "1"],
            id="people",
        ),
    ],
)
def test_save_exclusion_updates_payment_plan_summary(
    request: pytest.FixtureRequest,
    login: HopeTestBrowser,
    payment_plan_fixture: str,
    ids_input: str,
    excluded_id: Callable[[Household], str],
    labels: list[str],
    before: list[str],
    after: list[str],
) -> None:
    payment_plan = request.getfixturevalue(payment_plan_fixture)
    household = excluded_household(payment_plan)
    login.open(payment_plan_url(payment_plan))
    login.wait_for_text("LOCKED", 'div[data-cy="status-container"]')
    assert summary(login, labels) == before

    login.wait_for_element_clickable(CREATE_EXCLUSIONS).click()
    login.type('textarea[data-cy="input-exclusionReason"]', "Reason e2e Test")
    login.type(ids_input, excluded_id(household))
    login.wait_for_element_clickable('button[data-cy="button-apply-exclusions"]').click()
    login.wait_for_element_clickable('button[data-cy="button-save-exclusions"]').click()

    login.wait_for_text(after[-1], labels[-1])
    assert summary(login, labels) == after
    payment_plan.refresh_from_db()
    assert payment_plan.exclusion_reason == "Reason e2e Test"
    assert list(payment_plan.payment_items.filter(excluded=True).values_list("household", flat=True)) == [
        household.pk
    ]


def test_exclusions_cannot_be_created_for_accepted_payment_plan(
    login: HopeTestBrowser,
    accepted_payment_plan_without_payments: PaymentPlan,
) -> None:
    login.open(payment_plan_url(accepted_payment_plan_without_payments))
    login.wait_for_text("ACCEPTED", 'div[data-cy="status-container"]')

    login.assert_element_present(f"{CREATE_EXCLUSIONS}:disabled")
    login.hover_on_element(f'span:has(> {CREATE_EXCLUSIONS})')
    login.wait_for_text(
        "Items Groups can only be excluded from a Payment Plan in status open or locked", '[role="tooltip"]'
    )
