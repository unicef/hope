import pytest

from extras.test_utils.factories import (
    AdminAreaLimitedToFactory,
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db


def test_account_factories():
    assert AdminAreaLimitedToFactory()
    assert PartnerFactory()
    assert RoleAssignmentFactory()
    assert RoleFactory()
    assert UserFactory()
