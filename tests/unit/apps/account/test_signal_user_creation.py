"""Tests for signals triggered when a user is created."""

import pytest

from extras.test_utils.factories import UserFactory
from hope.models import BusinessArea, Role, RoleAssignment

pytestmark = pytest.mark.django_db


def test_user_created_assigns_basic_role():
    global_ba = BusinessArea.objects.create(name="Global", slug="global", code="GLO")
    basic_role = Role.objects.create(name="Basic User", permissions=[])

    user = UserFactory()

    assert RoleAssignment.objects.filter(user=user, business_area=global_ba, role=basic_role).exists()
