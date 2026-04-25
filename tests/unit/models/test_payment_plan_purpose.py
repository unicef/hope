from django.core.exceptions import ValidationError
import pytest

from extras.test_utils.factories import PaymentPlanPurposeFactory, ProgramFactory

pytestmark = pytest.mark.django_db


def test_program_requires_at_least_one_purpose_to_activate():
    program = ProgramFactory(status="DRAFT")
    program.status = "ACTIVE"
    with pytest.raises(ValidationError, match="Program must have at least one Payment Plan Purpose before becoming ACTIVE."):
        program.save()


def test_program_can_have_multiple_purposes():
    program = ProgramFactory(status="DRAFT")
    p1 = PaymentPlanPurposeFactory()
    p2 = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.set([p1, p2])
    program.status = "ACTIVE"
    program.save()
    assert program.payment_plan_purposes.count() == 2
