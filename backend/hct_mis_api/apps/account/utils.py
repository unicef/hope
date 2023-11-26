from typing import List, Optional

from hct_mis_api.apps.account.models import Partner


def update_partner_permissions(partner: Partner, action: str, areas: Optional[List]) -> None:
    # TODO: update action_map
    action_map = {
        "create_program": update_partner_permissions_create_program,
        "update_program": update_partner_permissions_create_program,
        "copy_program": update_partner_permissions_create_program,
        "delete_program": update_partner_permissions_create_program,
    }
    fn = action_map.get(action)
    fn(partner, areas)


def update_partner_permissions_create_program(partner: Partner, areas: Optional[List]) -> None:
    # TODO: add update perms logic here
    pass
