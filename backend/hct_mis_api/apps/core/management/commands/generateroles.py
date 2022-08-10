from django.core.management import BaseCommand
from django.db.models import Q

from hct_mis_api.apps.account.models import IncompatibleRoles, Role
from hct_mis_api.apps.account.permissions import Permissions


class Command(BaseCommand):
    help = "Generate roles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete_all",
            action="store_true",
            help="Should delete all existing roles before creating defaults. Be aware that it would also remove all existing UserRoles and IncompatibleRoles.",
        )
        parser.add_argument(
            "--delete_incompatible",
            action="store_true",
            help="Should delete all current incompatible roles, but only update Roles.",
        )

    def handle(self, *args, **options):

        default_roles_matrix = [
            {"name": "Basic User", "permissions": [Permissions.DASHBOARD_VIEW_COUNTRY]},
            {
                "name": "Advanced Registration Reader",
                "permissions": [
                    Permissions.RDI_VIEW_LIST,
                    Permissions.RDI_VIEW_DETAILS,
                    Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
                    Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
                    Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
                    Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS,
                    Permissions.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
                    Permissions.ALL_VIEW_PII_DATA_ON_LISTS,
                ],
            },
            {
                "name": "Planner",
                "permissions": [
                    Permissions.DASHBOARD_VIEW_COUNTRY,
                    Permissions.DASHBOARD_EXPORT,
                    Permissions.RDI_VIEW_LIST,
                    Permissions.RDI_VIEW_DETAILS,
                    Permissions.RDI_IMPORT_DATA,
                    Permissions.RDI_RERUN_DEDUPE,
                    Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
                    Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
                    Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS,
                    Permissions.PROGRAMME_CREATE,
                    Permissions.PROGRAMME_UPDATE,
                    Permissions.PROGRAMME_REMOVE,
                    Permissions.PROGRAMME_ACTIVATE,
                    Permissions.PROGRAMME_FINISH,
                    Permissions.TARGETING_VIEW_LIST,
                    Permissions.TARGETING_VIEW_DETAILS,
                    Permissions.TARGETING_VIEW_DETAILS,
                    Permissions.TARGETING_CREATE,
                    Permissions.TARGETING_UPDATE,
                    Permissions.TARGETING_DUPLICATE,
                    Permissions.TARGETING_REMOVE,
                    Permissions.TARGETING_LOCK,
                    Permissions.TARGETING_UNLOCK,
                    Permissions.TARGETING_SEND,
                    Permissions.PAYMENT_VERIFICATION_VIEW_LIST,
                    Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS,
                    Permissions.PAYMENT_VERIFICATION_CREATE,
                    Permissions.PAYMENT_VERIFICATION_UPDATE,
                    Permissions.PAYMENT_VERIFICATION_DISCARD,
                    Permissions.PAYMENT_VERIFICATION_INVALID,
                    Permissions.PAYMENT_VERIFICATION_DELETE,
                    Permissions.PAYMENT_VERIFICATION_VERIFY,
                    Permissions.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
                    Permissions.REPORTING_EXPORT,
                    Permissions.USER_MANAGEMENT_VIEW_LIST,
                    Permissions.ACTIVITY_LOG_VIEW,
                    Permissions.ACTIVITY_LOG_DOWNLOAD,
                ],
            },
            {
                "name": "Approver",
                "permissions": [
                    Permissions.DASHBOARD_VIEW_COUNTRY,
                    Permissions.DASHBOARD_EXPORT,
                    Permissions.RDI_VIEW_LIST,
                    Permissions.RDI_VIEW_DETAILS,
                    Permissions.RDI_MERGE_IMPORT,
                    Permissions.RDI_REFUSE_IMPORT,
                    Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
                    Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
                    Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS,
                    Permissions.PROGRAMME_CREATE,
                    Permissions.PROGRAMME_UPDATE,
                    Permissions.PROGRAMME_REMOVE,
                    Permissions.PROGRAMME_ACTIVATE,
                    Permissions.PROGRAMME_FINISH,
                    Permissions.TARGETING_VIEW_LIST,
                    Permissions.TARGETING_VIEW_DETAILS,
                    Permissions.TARGETING_CREATE,
                    Permissions.TARGETING_UPDATE,
                    Permissions.TARGETING_DUPLICATE,
                    Permissions.TARGETING_REMOVE,
                    Permissions.TARGETING_LOCK,
                    Permissions.TARGETING_UNLOCK,
                    Permissions.TARGETING_SEND,
                    Permissions.PAYMENT_VERIFICATION_VIEW_LIST,
                    Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS,
                    Permissions.PAYMENT_VERIFICATION_ACTIVATE,
                    Permissions.PAYMENT_VERIFICATION_DISCARD,
                    Permissions.PAYMENT_VERIFICATION_INVALID,
                    Permissions.PAYMENT_VERIFICATION_DELETE,
                    Permissions.PAYMENT_VERIFICATION_FINISH,
                    Permissions.PAYMENT_VERIFICATION_EXPORT,
                    Permissions.PAYMENT_VERIFICATION_IMPORT,
                    Permissions.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
                    Permissions.REPORTING_EXPORT,
                    Permissions.USER_MANAGEMENT_VIEW_LIST,
                    Permissions.ACTIVITY_LOG_VIEW,
                    Permissions.ACTIVITY_LOG_DOWNLOAD,
                ],
            },
            {
                "name": "Authorizer",
                "permissions": [
                    Permissions.DASHBOARD_VIEW_COUNTRY,
                    Permissions.DASHBOARD_EXPORT,
                    Permissions.RDI_VIEW_LIST,
                    Permissions.RDI_VIEW_DETAILS,
                    Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
                    Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
                    Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS,
                    Permissions.TARGETING_VIEW_LIST,
                    Permissions.TARGETING_VIEW_DETAILS,
                    Permissions.PAYMENT_VERIFICATION_VIEW_LIST,
                    Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS,
                    Permissions.REPORTING_EXPORT,
                    Permissions.USER_MANAGEMENT_VIEW_LIST,
                    Permissions.ACTIVITY_LOG_VIEW,
                    Permissions.ACTIVITY_LOG_DOWNLOAD,
                ],
            },
            {
                "name": "Releaser",
                "permissions": [
                    Permissions.DASHBOARD_VIEW_COUNTRY,
                    Permissions.DASHBOARD_EXPORT,
                    Permissions.RDI_VIEW_LIST,
                    Permissions.RDI_VIEW_DETAILS,
                    Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
                    Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
                    Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS,
                    Permissions.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
                    Permissions.TARGETING_VIEW_LIST,
                    Permissions.TARGETING_VIEW_DETAILS,
                    Permissions.TARGETING_SEND,
                    Permissions.PAYMENT_VERIFICATION_VIEW_LIST,
                    Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS,
                    Permissions.PAYMENT_VERIFICATION_CREATE,
                    Permissions.PAYMENT_VERIFICATION_UPDATE,
                    Permissions.PAYMENT_VERIFICATION_DISCARD,
                    Permissions.PAYMENT_VERIFICATION_INVALID,
                    Permissions.PAYMENT_VERIFICATION_DELETE,
                    Permissions.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
                    Permissions.PAYMENT_VERIFICATION_VERIFY,
                    Permissions.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
                    Permissions.REPORTING_EXPORT,
                    Permissions.USER_MANAGEMENT_VIEW_LIST,
                    Permissions.ACTIVITY_LOG_VIEW,
                    Permissions.ACTIVITY_LOG_DOWNLOAD,
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
                    Permissions.GRIEVANCES_UPDATE_AS_CREATOR,
                    Permissions.GRIEVANCES_UPDATE_AS_OWNER,
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
                    Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR,
                    Permissions.GRIEVANCES_CREATE,
                    Permissions.GRIEVANCES_UPDATE_AS_CREATOR,
                    Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR,
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
                    Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
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

        default_incompatible_roles = [
            ("Planner", "Approver"),
            ("Planner", "Authorizer"),
            ("Planner", "Releaser"),
            ("Approver", "Authorizer"),
            ("Approver", "Releaser"),
            ("Authorizer", "Releaser"),
            ("Grievance Collector", "Grievance Approver"),
        ]

        if options["delete_all"]:
            Role.objects.all().delete()
            print("All old roles were deleted.")
        if options["delete_incompatible"]:
            IncompatibleRoles.objects.all().delete()
            print("Old incompatible roles pairs were deleted.")

        roles_created = []
        roles_updated = []
        for default_role in default_roles_matrix:
            role, created = Role.objects.update_or_create(
                subsystem=Role.HOPE,
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

        incompatible_roles_created = []
        for role_pair in default_incompatible_roles:
            if not IncompatibleRoles.objects.filter(
                Q(role_one__name=role_pair[0], role_two__name=role_pair[1])
                | Q(role_one__name=role_pair[1], role_two__name=role_pair[0])
            ).exists():
                IncompatibleRoles.objects.create(
                    role_one=Role.objects.get(subsystem=Role.HOPE, name=role_pair[0]),
                    role_two=Role.objects.get(subsystem=Role.HOPE, name=role_pair[1]),
                )
                incompatible_roles_created.append(f"{role_pair[0]} and {role_pair[1]}")
        if incompatible_roles_created:
            print(f"Incompatible roles pairs created: {', '.join(incompatible_roles_created)}")
        else:
            print("No new incompatible roles pairs were created.")
