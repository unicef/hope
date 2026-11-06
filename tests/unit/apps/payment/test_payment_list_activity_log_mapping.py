import pytest

from extras.test_utils.factories import PaymentListFactory
from hope.apps.core.utils import nested_getattr
from hope.models import PaymentList
from hope.models.currency import Currency

pytestmark = pytest.mark.django_db


@pytest.fixture
def payment_list(currency_usd: Currency) -> PaymentList:
    return PaymentListFactory(currency=currency_usd)


@pytest.mark.parametrize("field_path", sorted(PaymentList.ACTIVITY_LOG_MAPPING.keys()))
def test_activity_log_mapping_keys_resolve_on_instance(payment_list: PaymentList, field_path: str) -> None:
    # Every key in ACTIVITY_LOG_MAPPING must resolve to a real attribute on PaymentList.
    # create_diff() calls nested_getattr() with default=None, so a dead key (e.g. a renamed
    # field) silently logs nothing instead of raising - this guard catches such keys.
    nested_getattr(payment_list, field_path)
