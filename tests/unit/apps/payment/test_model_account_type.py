import pytest

from extras.test_utils.factories.payment import AccountTypeFactory
from hope.models import AccountType

pytestmark = pytest.mark.django_db


@pytest.fixture
def account_types():
    return [
        AccountTypeFactory(key="bank", label="Bank", unique_fields=["number"]),
        AccountTypeFactory(key="mobile", label="Mobile", unique_fields=["number"]),
    ]


def test_get_targeting_field_names(account_types):
    assert AccountType.get_targeting_field_names() == [
        "bank__number",
        "mobile__number",
    ]
