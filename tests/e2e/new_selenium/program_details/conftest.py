import pytest

from extras.test_utils.factories import BusinessAreaFactory, PaymentPlanPurposeFactory
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.models import BusinessArea, PaymentPlanPurpose, Program

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
