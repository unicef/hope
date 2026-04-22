from typing import Any

import pytest

from extras.test_utils.factories import ProgramFactory, UserFactory
from hope.apps.account.permissions import Permissions
from hope.models import Program


@pytest.fixture
def program_active(afghanistan: Any) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def authorized_user(
    afghanistan: Any,
    program_active: Program,
    create_user_role_with_permissions: Any,
) -> Any:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [Permissions.PM_VIEW_DETAILS],
        afghanistan,
        program_active,
    )
    return user
