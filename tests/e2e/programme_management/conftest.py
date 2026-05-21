import pytest

from extras.test_utils.factories.core import PaymentPlanPurposeFactory
from hope.models import BusinessArea, PaymentPlanPurpose

PURPOSE_NAME = "Test Purpose"


@pytest.fixture
def payment_plan_purpose(business_area: BusinessArea) -> PaymentPlanPurpose:
    return PaymentPlanPurposeFactory(business_area=business_area, name=PURPOSE_NAME)
