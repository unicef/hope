import logging

from hct_mis_api.apps.account.models import Role

old_permissions_mapping = [
    ("ACCOUNTABILITY_FEEDBACK_VIEW_CREATE", "GRIEVANCES_FEEDBACK_VIEW_CREATE"),
    ("ACCOUNTABILITY_FEEDBACK_VIEW_LIST", "GRIEVANCES_FEEDBACK_VIEW_LIST"),
    ("ACCOUNTABILITY_FEEDBACK_VIEW_DETAILS", "GRIEVANCES_FEEDBACK_VIEW_DETAILS"),
    ("ACCOUNTABILITY_FEEDBACK_VIEW_UPDATE", "GRIEVANCES_FEEDBACK_VIEW_UPDATE"),
    ("ACCOUNTABILITY_FEEDBACK_MESSAGE_VIEW_CREATE", "GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE"),
]

logger = logging.getLogger(__name__)


def update_roles() -> None:
    roles = Role.objects.all()
    roles_to_update = []

    logger.info(f"Found {roles.count()} roles")
    for role in roles:
        logger.info(f"Processing role {role.name}")
        should_update = False
        for old_permission, new_permission in old_permissions_mapping:
            if role.permissions and old_permission in role.permissions:
                role.permissions.remove(old_permission)
                role.permissions.append(new_permission)
                should_update = True
        if should_update:
            logger.info("Role added to update")
            roles_to_update.append(role)
    logger.info(f"Updating {len(roles_to_update)} roles")
    Role.objects.bulk_update(roles_to_update, fields=("permissions",))
    logger.info("Roles updated")
