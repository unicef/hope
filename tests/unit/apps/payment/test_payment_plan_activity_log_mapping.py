import pytest

from extras.test_utils.factories import PaymentPlanFactory
from hope.apps.core.utils import nested_getattr
from hope.models import PaymentPlan
from hope.models.currency import Currency

pytestmark = pytest.mark.django_db


@pytest.fixture
def payment_plan(currency_usd: Currency) -> PaymentPlan:
    return PaymentPlanFactory(currency=currency_usd)


@pytest.mark.parametrize("field_path", sorted(PaymentPlan.ACTIVITY_LOG_MAPPING.keys()))
def test_activity_log_mapping_keys_resolve_on_instance(payment_plan: PaymentPlan, field_path: str) -> None:
    # Every key in ACTIVITY_LOG_MAPPING must resolve to a real attribute on PaymentPlan.
    # create_diff() calls nested_getattr() with default=None, so a dead key (e.g. a renamed
    # field) silently logs nothing instead of raising - this guard catches such keys.
    nested_getattr(payment_plan, field_path)
