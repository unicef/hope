"""Querysets behind the My Tasks page: which tickets wait for a user, and which changed since they looked.

Every helper returns a `Q` so the API list, the per-tab change flags and the email all answer
the same question with the same SQL.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from django.db.models import Exists, OuterRef, Q

from hope.apps.account.permissions import Permissions
from hope.apps.grievance.constants import PRESET_MINE, PRESET_NEEDS_ASSIGNMENT, PRESET_PENDING_APPROVAL
from hope.apps.grievance.models import GrievanceTicket, TicketNote
from hope.apps.grievance.visibility import (
    VIEW_LIST_PERMISSIONS,
    _program_ids_for,
    in_programs_q,
    without_program_q,
)
from hope.models import Program

if TYPE_CHECKING:
    from hope.models import BusinessArea, User

# Which permission lets a user act on a ticket waiting for approval, per category: all / creator / owner.
CATEGORY_APPROVE_PERMISSIONS = {
    GrievanceTicket.CATEGORY_DATA_CHANGE: (
        Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
        Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
        Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER,
    ),
    GrievanceTicket.CATEGORY_SYSTEM_FLAGGING: (
        Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
        Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
        Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
    ),
    GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION: (
        Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
        Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
        Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
    ),
    GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: (
        Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION,
        Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_CREATOR,
        Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_OWNER,
    ),
    GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE: (
        Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR,
        Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER,
    ),
    GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT: (
        Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR,
        Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER,
    ),
    GrievanceTicket.CATEGORY_BENEFICIARY: (
        Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR,
        Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER,
    ),
    # Referral is a feedback-type ticket, so closing/approving is gated by the feedback permission.
    GrievanceTicket.CATEGORY_REFERRAL: (
        Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK,
        Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_CREATOR,
        Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER,
    ),
}

# every grant that gives a user something on My Tasks - who the email check looks at
MY_TASKS_PERMISSIONS = (
    Permissions.GRIEVANCE_ASSIGN,
    *VIEW_LIST_PERMISSIONS,
    *{permission for grants in CATEGORY_APPROVE_PERMISSIONS.values() for permission in grants},
)


def in_active_program_q() -> Q:
    """Tickets the My Tasks list can show: in an active programme, or in no programme at all."""
    through_model = GrievanceTicket.programs.through
    return (
        Q(Exists(through_model.objects.filter(grievanceticket=OuterRef("pk"), program__status=Program.ACTIVE)))
        | without_program_q()
    )


def assignable_tickets_q(user: "User", business_area: "BusinessArea") -> Q:
    """Select the NEEDS ASSIGNMENT tab: unassigned tickets in a programme `user` may assign in."""
    program_ids = _program_ids_for(user, business_area, Permissions.GRIEVANCE_ASSIGN)
    if not program_ids:
        return Q(pk__in=[])
    return (in_programs_q(program_ids) | without_program_q()) & Q(assigned_to__isnull=True)


def assigned_tickets_q(user: "User", business_area: "BusinessArea") -> Q:
    """Select the ASSIGNED TO ME tab."""
    return Q(assigned_to=user)


def approvable_tickets_q(user: "User", business_area: "BusinessArea") -> Q:
    """Select the PENDING APPROVAL tab: tickets waiting for approval that `user` may approve, per category."""
    approvable = Q(pk__in=[])
    for category, (base, creator, owner) in CATEGORY_APPROVE_PERMISSIONS.items():
        for permission, role_scope in ((base, Q()), (creator, Q(created_by=user)), (owner, Q(assigned_to=user))):
            program_ids = _program_ids_for(user, business_area, permission)
            if program_ids:
                approvable |= (in_programs_q(program_ids) | without_program_q()) & Q(category=category) & role_scope
    return Q(status=GrievanceTicket.STATUS_FOR_APPROVAL) & approvable


TAB_SCOPES = {
    PRESET_NEEDS_ASSIGNMENT: assignable_tickets_q,
    PRESET_MINE: assigned_tickets_q,
    PRESET_PENDING_APPROVAL: approvable_tickets_q,
}


def changed_since_q(user: "User", since: datetime) -> Q:
    """Tickets somebody other than `user` created, assigned, edited, moved or annotated after `since`.

    A status change stamps `user_modified`, so a ticket sent back or sent for approval counts as edited.
    """
    note_by_someone_else = TicketNote.objects.filter(ticket=OuterRef("pk"), created_at__gt=since).exclude(
        created_by=user
    )
    return (
        (Q(created_at__gt=since) & ~Q(created_by=user))
        | (Q(assigned_at__gt=since) & ~Q(assigned_by=user))
        | (Q(user_modified__gt=since, user_modified_by__isnull=False) & ~Q(user_modified_by=user))
        | Q(Exists(note_by_someone_else))
    )
