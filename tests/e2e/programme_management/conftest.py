import pytest

from extras.test_utils.factories.core import PaymentPlanPurposeFactory
from hope.models import PaymentPlanPurpose

PURPOSE_NAME = "Test Purpose"


@pytest.fixture
def payment_plan_purpose() -> PaymentPlanPurpose:
    return PaymentPlanPurposeFactory(name=PURPOSE_NAME)
