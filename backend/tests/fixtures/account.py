from typing import Any, Callable, Iterable, Optional

import pytest

from hct_mis_api.apps.account.models import Role, User, UserRole
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.models import Program


@pytest.fixture()
def update_user_partner_perm_for_program() -> Callable:
    def _update_user_partner_perm_for_program(user: User, business_area: BusinessArea, program: Program) -> None:
        partner_permissions = user.partner.permissions or {}
        if str(business_area.pk) in partner_permissions:
            # only add new program_id
            if str(program.pk) not in partner_permissions[str(business_area.pk)]["programs"]:
                partner_permissions[str(business_area.pk)]["programs"].update({str(program.pk): []})
            else:
                pass
        else:
            partner_permissions.update({str(business_area.pk): {"programs": {str(program.pk): []}}})

        user.partner.permissions = partner_permissions
        user.partner.save()

    return _update_user_partner_perm_for_program


@pytest.fixture()
def create_user_role_with_permissions(update_user_partner_perm_for_program: Any) -> Callable:
    def _create_user_role_with_permissions(
        user: User,
        permissions: Iterable,
        business_area: BusinessArea,
        program: Optional[Program] = None,
        name: Optional[str] = "Role with Permissions",
    ) -> UserRole:
        permission_list = [perm.value for perm in permissions]
        role, created = Role.objects.update_or_create(name=name, defaults={"permissions": permission_list})
        user_role, _ = UserRole.objects.get_or_create(user=user, role=role, business_area=business_area)

        # update Partner permissions for the program
        if program:
            update_user_partner_perm_for_program(user, business_area, program)
        return user_role

    return _create_user_role_with_permissions
