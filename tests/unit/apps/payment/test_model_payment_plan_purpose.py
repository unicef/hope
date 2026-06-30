from django.core.exceptions import ValidationError
from django.db.models import Q
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PaymentPlanFactory,
    PaymentPlanPurposeFactory,
    ProgramCycleFactory,
    ProgramFactory,
)
from hope.models import BusinessArea, PaymentPlanPurpose, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area_afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


def test_program_requires_at_least_one_purpose(business_area_afghanistan: BusinessArea) -> None:
    program = ProgramFactory(status=Program.DRAFT, business_area=business_area_afghanistan)
    program.payment_plan_purposes.clear()
    with pytest.raises(ValidationError, match="Program must have at least one Payment Plan Purpose."):
        program.save()


def test_program_cannot_have_purpose_restricted_to_different_ba(business_area_afghanistan: BusinessArea) -> None:
    other_ba = BusinessAreaFactory()
    program = ProgramFactory(status=Program.DRAFT, business_area=business_area_afghanistan)
    restricted_purpose = PaymentPlanPurposeFactory()
    restricted_purpose.limit_to.add(other_ba)
    program.payment_plan_purposes.add(restricted_purpose)

    with pytest.raises(
        ValidationError, match="All Payment Plan Purposes must be available for this program's business area."
    ):
        program.save()


def test_program_can_have_multiple_purposes(business_area_afghanistan: BusinessArea) -> None:
    program = ProgramFactory(status=Program.DRAFT, business_area=business_area_afghanistan)
    p1 = PaymentPlanPurposeFactory()
    p2 = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.set([p1, p2])
    program.status = Program.ACTIVE
    program.save()
    assert program.payment_plan_purposes.count() == 2


def test_payment_plan_requires_at_least_one_purpose(business_area_afghanistan: BusinessArea) -> None:
    plan = PaymentPlanFactory(program_cycle__program__business_area=business_area_afghanistan)
    plan.payment_plan_purposes.clear()

    with pytest.raises(ValidationError, match="PaymentPlan must have at least one Payment Plan Purpose."):
        plan.save()


def test_payment_plan_purpose_must_be_subset_of_program_purposes(business_area_afghanistan: BusinessArea) -> None:
    program = ProgramFactory(status=Program.ACTIVE, business_area=business_area_afghanistan)
    purpose_for_program = PaymentPlanPurposeFactory()
    unrelated_purpose = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.add(purpose_for_program)
    cycle = ProgramCycleFactory(program=program)
    plan = PaymentPlanFactory(program_cycle=cycle)
    plan.payment_plan_purposes.add(unrelated_purpose)

    with pytest.raises(ValidationError, match="All PaymentPlan purposes must be a subset of the program's purposes."):
        plan.clean()


def test_limit_to_empty_returns_purpose_for_any_ba() -> None:
    ba = BusinessAreaFactory()
    global_purpose = PaymentPlanPurposeFactory()

    result = PaymentPlanPurpose.objects.filter(Q(limit_to__isnull=True) | Q(limit_to__slug=ba.slug)).distinct()

    assert global_purpose in result


def test_limit_to_set_returns_purpose_for_matching_ba() -> None:
    ba = BusinessAreaFactory()
    restricted_purpose = PaymentPlanPurposeFactory()
    restricted_purpose.limit_to.add(ba)

    result = PaymentPlanPurpose.objects.filter(Q(limit_to__isnull=True) | Q(limit_to__slug=ba.slug)).distinct()

    assert restricted_purpose in result


def test_limit_to_set_excludes_purpose_for_other_ba() -> None:
    ba = BusinessAreaFactory()
    other_ba = BusinessAreaFactory()
    restricted_purpose = PaymentPlanPurposeFactory()
    restricted_purpose.limit_to.add(other_ba)

    result = PaymentPlanPurpose.objects.filter(Q(limit_to__isnull=True) | Q(limit_to__slug=ba.slug)).distinct()

    assert restricted_purpose not in result
