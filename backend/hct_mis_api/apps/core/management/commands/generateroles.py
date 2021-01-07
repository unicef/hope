from django.core.management import BaseCommand
from account.permissions import Permissions
from account.models import Role


class Command(BaseCommand):
    help = "Generate roles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete_before",
            action="store_true",
            help="Should delete all existing roles before creating defaults. Be aware that it would also remove all existing UserRoles.",
        )

    def handle(self, *args, **options):

        default_roles_matrix = [
            {"name": "Basic User", "permissions": [Permissions.DASHBOARD_VIEW_HQ]},
            {
                "name": "Reader",
                "permissions": [
                    Permissions.DASHBOARD_VIEW_COUNTRY,
                    Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
                    Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
                    Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS,
                    Permissions.TARGETING_VIEW_LIST,
                    Permissions.PAYMENT_VERIFICATION_VIEW_LIST,
                    Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS,
                    Permissions.USER_MANAGEMENT_VIEW_LIST,
                ],
            },
            {
                "name": "Advanced Registration Reader",
                "permissions": [
                    Permissions.RDI_VIEW_LIST,
                    Permissions.RDI_VIEW_DETAILS,
                    Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
                    Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS,
                    Permissions.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
                ],
            },
            {
                "name": "Planner",
                "permissions": [
                    Permissions.RDI_IMPORT_DATA,
                    Permissions.RDI_RERUN_DEDUPE,
                    Permissions.PROGRAMME_CREATE,
                    Permissions.PROGRAMME_UPDATE,
                    Permissions.PROGRAMME_REMOVE,
                    Permissions.PROGRAMME_ACTIVATE,
                    Permissions.PROGRAMME_FINISH,
                    Permissions.TARGETING_VIEW_DETAILS,
                    Permissions.TARGETING_CREATE,
                    Permissions.TARGETING_UPDATE,
                    Permissions.TARGETING_DUPLICATE,
                    Permissions.TARGETING_REMOVE,
                    Permissions.TARGETING_LOCK,
                    Permissions.TARGETING_UNLOCK,
                    Permissions.TARGETING_SEND,
                    Permissions.PAYMENT_VERIFICATION_CREATE,
                    Permissions.PAYMENT_VERIFICATION_UPDATE,
                    Permissions.PAYMENT_VERIFICATION_DISCARD,
                    Permissions.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
                ],
            },
            {
                "name": "Approver",
                "permissions": [
                    Permissions.RDI_MERGE_IMPORT,
                    Permissions.PROGRAMME_CREATE,
                    Permissions.PROGRAMME_UPDATE,
                    Permissions.PROGRAMME_REMOVE,
                    Permissions.PROGRAMME_ACTIVATE,
                    Permissions.PROGRAMME_FINISH,
                    Permissions.TARGETING_VIEW_DETAILS,
                    Permissions.PAYMENT_VERIFICATION_ACTIVATE,
                    Permissions.PAYMENT_VERIFICATION_DISCARD,
                    Permissions.PAYMENT_VERIFICATION_FINISH,
                    Permissions.PAYMENT_VERIFICATION_EXPORT,
                    Permissions.PAYMENT_VERIFICATION_IMPORT,
                    Permissions.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
                ],
            },
            {"name": "Authorizer", "permissions": []},
            {
                "name": "Releaser",
                "permissions": [
                    Permissions.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
                    Permissions.PAYMENT_VERIFICATION_CREATE,
                    Permissions.PAYMENT_VERIFICATION_UPDATE,
                    Permissions.PAYMENT_VERIFICATION_DISCARD,
                    Permissions.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
                ],
            },
            {
                "name": "Grievance Collector",
                "permissions": [
                    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                    Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                    Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS,
                    Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS,
                    Permissions.GRIEVANCES_CREATE,
                    Permissions.GRIEVANCES_ADD_NOTE,
                ],
            },
            {
                "name": "Ticket Creator",
                "permissions": [
                    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
                    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
                    Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
                    Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
                    Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR,
                    Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS,
                    Permissions.GRIEVANCES_CREATE,
                    Permissions.GRIEVANCES_UPDATE_AS_CREATOR,
                    Permissions.GRIEVANCES_ADD_NOTE_AS_CREATOR,
                ],
            },
            {
                "name": "Ticket Owner",
                "permissions": [
                    Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
                    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
                    Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
                    Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
                    Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER,
                    Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER,
                    Permissions.GRIEVANCES_CREATE,
                    Permissions.GRIEVANCES_UPDATE_AS_OWNER,
                    Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER,
                    Permissions.GRIEVANCES_ADD_NOTE_AS_OWNER,
                    Permissions.GRIEVANCES_SET_IN_PROGRESS_AS_OWNER,
                    Permissions.GRIEVANCES_SET_ON_HOLD_AS_OWNER,
                    Permissions.GRIEVANCES_SEND_FOR_APPROVAL_AS_OWNER,
                    Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER,
                ],
            },
            {
                "name": "Grievance Approver",
                "permissions": [
                    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                    Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                    Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS,
                    Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS,
                    Permissions.GRIEVANCES_ADD_NOTE,
                    Permissions.GRIEVANCES_SEND_BACK,
                    Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
                    Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
                ],
            },
            {
                "name": "Senior Management",
                "permissions": [
                    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
                    Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                    Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
                    Permissions.GRIEVANCES_ADD_NOTE,
                ],
            },
            {
                "name": "Adjudicator",
                "permissions": [
                    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
                    Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
                    Permissions.GRIEVANCES_ADD_NOTE,
                ],
            },
            {"name": "Role with all permissions", "permissions": Permissions},
        ]

        if options["delete_before"]:
            Role.objects.all().delete()
            print("All old roles were deleted.")

        roles_created = []
        roles_updated = []
        for default_role in default_roles_matrix:
            role, created = Role.objects.update_or_create(
                name=default_role["name"],
                defaults={"permissions": [permission.value for permission in default_role["permissions"]]},
            )

            if created:
                roles_created.append(role.name)
            else:
                roles_updated.append(role.name)

        if roles_created:
            print(f"New roles were created: {', '.join(roles_created)}")
        else:
            print("No new roles were created.")
        if roles_updated:
            print(f"These roles were updated: {', '.join(roles_updated)}")
        else:
            print("No roles were updated")
