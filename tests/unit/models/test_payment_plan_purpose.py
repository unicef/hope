from django.core.exceptions import ValidationError
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentPlanFactory,
    PaymentPlanPurposeFactory,
    ProgramCycleFactory,
    ProgramFactory,
)
from hope.models import BusinessArea, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area_afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def business_area_syria() -> BusinessArea:
    return BusinessAreaFactory(name="Syria", slug="syria")


def test_program_requires_at_least_one_purpose_to_activate(business_area_afghanistan: BusinessArea) -> None:
    program = ProgramFactory(status=Program.DRAFT, business_area=business_area_afghanistan)
    program.status = Program.ACTIVE
    with pytest.raises(
        ValidationError, match="Program must have at least one Payment Plan Purpose before becoming ACTIVE."
    ):
        program.save()


def test_program_can_have_multiple_purposes(business_area_afghanistan: BusinessArea) -> None:
    program = ProgramFactory(status=Program.DRAFT, business_area=business_area_afghanistan)
    p1 = PaymentPlanPurposeFactory(business_area=business_area_afghanistan)
    p2 = PaymentPlanPurposeFactory(business_area=business_area_afghanistan)
    program.payment_plan_purposes.set([p1, p2])
    program.status = Program.ACTIVE
    program.save()
    assert program.payment_plan_purposes.count() == 2


def test_program_cannot_have_purpose_from_different_business_area(
    business_area_afghanistan: BusinessArea, business_area_syria: BusinessArea
) -> None:
    program = ProgramFactory(status=Program.DRAFT, business_area=business_area_afghanistan)
    purpose = PaymentPlanPurposeFactory(business_area=business_area_syria)
    program.payment_plan_purposes.add(purpose)

    with pytest.raises(ValidationError, match="All Payment Plan Purposes must belong to this program's business area."):
        program.save()


def test_payment_plan_requires_at_least_one_purpose(business_area_afghanistan: BusinessArea) -> None:
    plan = PaymentPlanFactory(program_cycle__program__business_area=business_area_afghanistan)

    with pytest.raises(ValidationError, match="PaymentPlan must have at least one Payment Plan Purpose."):
        plan.clean()


def test_payment_plan_purpose_must_be_subset_of_program_purposes(business_area_afghanistan: BusinessArea) -> None:
    program = ProgramFactory(status=Program.ACTIVE, business_area=business_area_afghanistan)
    purpose_for_program = PaymentPlanPurposeFactory(business_area=business_area_afghanistan)
    unrelated_purpose = PaymentPlanPurposeFactory(business_area=business_area_afghanistan)
    program.payment_plan_purposes.add(purpose_for_program)
    cycle = ProgramCycleFactory(program=program)
    plan = PaymentPlanFactory(program_cycle=cycle)
    plan.payment_plan_purposes.add(unrelated_purpose)

    with pytest.raises(ValidationError, match="All PaymentPlan purposes must be a subset of the program's purposes."):
        plan.clean()
