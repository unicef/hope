import pytest

from extras.test_utils.factories import BusinessAreaFactory, PaymentPlanPurposeFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.models import BusinessArea, PaymentPlanPurpose, Program

BA_PURPOSE_NAME = "BA Purpose"
SECOND_BA_PURPOSE_NAME = "Second BA Purpose"
OTHER_BA_PURPOSE_NAME = "Other BA Purpose"
FIVE_PURPOSE_NAMES = ("Purpose 1", "Purpose 2", "Purpose 3", "Purpose 4", "Purpose 5")


@pytest.fixture
def ba_purpose(business_area: BusinessArea) -> PaymentPlanPurpose:
    return PaymentPlanPurposeFactory(business_area=business_area, name=BA_PURPOSE_NAME)


@pytest.fixture
def second_ba_purpose(business_area: BusinessArea) -> PaymentPlanPurpose:
    return PaymentPlanPurposeFactory(business_area=business_area, name=SECOND_BA_PURPOSE_NAME)


@pytest.fixture
def other_ba_purpose() -> PaymentPlanPurpose:
    other_ba = BusinessAreaFactory()
    return PaymentPlanPurposeFactory(business_area=other_ba, name=OTHER_BA_PURPOSE_NAME)


@pytest.fixture
def purpose() -> PaymentPlanPurpose:
    ba = BusinessArea.objects.get(slug="afghanistan")
    return PaymentPlanPurposeFactory(business_area=ba, name=BA_PURPOSE_NAME)


@pytest.fixture
def program_with_purpose(business_area: BusinessArea, ba_purpose: PaymentPlanPurpose) -> Program:
    prog = ProgramFactory(business_area=business_area, status=Program.DRAFT)
    prog.payment_plan_purposes.add(ba_purpose)
    return prog


@pytest.fixture
def five_ba_purposes(business_area: BusinessArea) -> list[PaymentPlanPurpose]:
    return [PaymentPlanPurposeFactory(business_area=business_area, name=name) for name in FIVE_PURPOSE_NAMES]


@pytest.fixture
def program_with_five_purposes(business_area: BusinessArea, five_ba_purposes: list[PaymentPlanPurpose]) -> Program:
    prog = ProgramFactory(business_area=business_area, status=Program.DRAFT)
    prog.payment_plan_purposes.set(five_ba_purposes)
    return prog
