import copy
from typing import Sequence

from django.db import transaction
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from hope.apps.account.permissions import Permissions, check_creator_or_owner_permission
from hope.apps.core.utils import clear_cache_for_key
from hope.apps.grievance.constants import PRIORITY_CHOICES, URGENCY_CHOICES
from hope.apps.grievance.models import GrievanceTicket, TicketNote
from hope.apps.grievance.services.needs_adjudication_ticket_services import (
    close_needs_adjudication_ticket_service,
)
from hope.apps.grievance.services.ticket_status_changer_service import TicketStatusChangerService
from hope.apps.grievance.signals import increment_grievance_ticket_version_cache_for_ticket_ids
from hope.models import User, log_create

# prevent N+1 queries with Grievance Ticket queries in log_create
_ACTIVITY_LOG_SELECT_RELATED = (
    "business_area",
    "assigned_to",
    "created_by",
    "admin2",
    "complaint_ticket_details__household",
    "complaint_ticket_details__individual",
    "complaint_ticket_details__payment",
    "sensitive_ticket_details",
    "positive_feedback_ticket_details",
    "negative_feedback_ticket_details",
    "referral_ticket_details",
    "household_data_update_ticket_details",
    "individual_data_update_ticket_details",
    "add_individual_ticket_details",
    "delete_individual_ticket_details",
    "system_flagging_ticket_details",
    "needs_adjudication_ticket_details",
    "payment_verification_ticket_details",
)


class BulkActionService:
    def _clear_cache(self, business_area_slug: str) -> None:
        cache_key = f"count_{business_area_slug}_GrievanceTicketNodeConnection_"
        clear_cache_for_key(cache_key)

    @transaction.atomic
    def bulk_assign(
        self,
        tickets_ids: Sequence[str],
        assigned_to_id: str | None,
        business_area_slug: str,
    ) -> QuerySet[GrievanceTicket]:
        user = get_object_or_404(User, id=assigned_to_id)
        queryset = GrievanceTicket.objects.filter(~Q(status=GrievanceTicket.STATUS_CLOSED), id__in=tickets_ids)

        new_tickets = queryset.filter(status=GrievanceTicket.STATUS_NEW)

        updated_count = queryset.update(assigned_to=user, updated_at=timezone.now())
        if updated_count != len(tickets_ids):
            raise ValidationError("Some tickets do not exist or are closed")

        # Update also status to assigned if status is new
        new_tickets.update(status=GrievanceTicket.STATUS_ASSIGNED)
        increment_grievance_ticket_version_cache_for_ticket_ids(business_area_slug, list(map(str, tickets_ids)))

        self._clear_cache(business_area_slug)
        return queryset

    @transaction.atomic
    def bulk_set_priority(
        self, tickets_ids: Sequence[str], priority: int, business_area_slug: str
    ) -> QuerySet[GrievanceTicket]:
        if priority not in [x for x, y in PRIORITY_CHOICES]:
            raise ValidationError("Invalid priority")
        queryset = GrievanceTicket.objects.filter(~Q(status=GrievanceTicket.STATUS_CLOSED), id__in=tickets_ids)
        updated_count = queryset.update(priority=priority)
        if updated_count != len(tickets_ids):
            raise ValidationError("Some tickets do not exist or are closed")
        increment_grievance_ticket_version_cache_for_ticket_ids(business_area_slug, list(map(str, tickets_ids)))
        self._clear_cache(business_area_slug)
        return queryset

    @transaction.atomic
    def bulk_set_urgency(
        self, tickets_ids: Sequence[str], urgency: int, business_area_slug: str
    ) -> QuerySet[GrievanceTicket]:
        if urgency not in [x for x, y in URGENCY_CHOICES]:
            raise ValidationError("Invalid priority")
        queryset = GrievanceTicket.objects.filter(~Q(status=GrievanceTicket.STATUS_CLOSED), id__in=tickets_ids)
        updated_count = queryset.update(urgency=urgency)
        if updated_count != len(tickets_ids):
            raise ValidationError("Some tickets do not exist or are closed")
        increment_grievance_ticket_version_cache_for_ticket_ids(business_area_slug, list(map(str, tickets_ids)))
        self._clear_cache(business_area_slug)
        return queryset

    @transaction.atomic
    def bulk_close(
        self,
        created_by: User,
        tickets_ids: Sequence[str],
        business_area_slug: str,
    ) -> list[GrievanceTicket]:
        """Close the selected tickets only if every one of them is closable, otherwise close none."""
        tickets = list(
            GrievanceTicket.objects.filter(
                ~Q(status=GrievanceTicket.STATUS_CLOSED),
                category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
                business_area__slug=business_area_slug,
                id__in=tickets_ids,
            )
            .select_for_update(of=("self",))
            .select_related(*_ACTIVITY_LOG_SELECT_RELATED)
            .prefetch_related("programs")
        )
        if len(tickets) != len(tickets_ids) or any(
            not ticket.can_change_status(GrievanceTicket.STATUS_CLOSED) for ticket in tickets
        ):
            raise ValidationError(
                "Some selected tickets cannot be closed. "
                "Only Grievance Complaint tickets in status For Approval can be closed."
            )

        # every selected ticket must be closable by this user (general, or as creator/owner)
        for ticket in tickets:
            check_creator_or_owner_permission(
                created_by,
                [
                    Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
                    Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR,
                    Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER,
                ],
                ticket.business_area,
                ticket,
            )

        for ticket in tickets:
            old_ticket = copy.copy(ticket)
            TicketStatusChangerService(ticket, created_by).change_status(GrievanceTicket.STATUS_CLOSED)
            log_create(
                GrievanceTicket.ACTIVITY_LOG_MAPPING,
                "business_area",
                created_by,
                ticket.programs.all(),
                old_object=old_ticket,
                new_object=ticket,
            )
        # version cache is bumped by the post_save signal on save()
        self._clear_cache(business_area_slug)
        return tickets

    @transaction.atomic
    def bulk_resolve_needs_adjudication(
        self,
        user: User,
        resolutions: Sequence[dict],
        business_area_slug: str,
    ) -> list[GrievanceTicket]:
        """Resolve and auto-close the selected Needs Adjudication tickets in one all-or-nothing batch.

        Each resolution marks individuals as duplicate/distinct and closes the ticket directly,
        bypassing the FOR_APPROVAL step. If any ticket is missing, already closed, not a Needs Adjudication ticket,
        or not resolvable by this user, nothing is committed.
        """
        resolutions_by_id = {str(resolution["ticket_id"]): resolution for resolution in resolutions}
        ticket_ids = list(resolutions_by_id.keys())
        tickets = list(
            GrievanceTicket.objects.filter(
                ~Q(status=GrievanceTicket.STATUS_CLOSED),
                category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                business_area__slug=business_area_slug,
                id__in=ticket_ids,
            )
            .select_for_update(of=("self",))
            .select_related(*_ACTIVITY_LOG_SELECT_RELATED)
            .prefetch_related("programs")
        )
        if len(tickets) != len(ticket_ids):
            raise ValidationError(
                "Some selected tickets do not exist, are closed, or are not Needs Adjudication tickets."
            )

        for ticket in tickets:
            scope = ticket.programs.first() or ticket.business_area
            if not user.has_perm(Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE.value, scope):
                raise PermissionDenied(
                    detail={"required_permissions": [Permissions.GRIEVANCES_NEEDS_ADJUDICATION_MANAGE.value]}
                )

        for ticket in tickets:
            old_ticket = copy.copy(ticket)
            self._resolve_single_needs_adjudication(ticket, resolutions_by_id[str(ticket.id)], user)
            log_create(
                GrievanceTicket.ACTIVITY_LOG_MAPPING,
                "business_area",
                user,
                ticket.programs.all(),
                old_object=old_ticket,
                new_object=ticket,
            )
        self._clear_cache(business_area_slug)
        return tickets

    def _resolve_single_needs_adjudication(self, ticket: GrievanceTicket, resolution: dict, user: User) -> None:
        ticket_details = ticket.ticket_details
        ticket_individual_ids = {str(ticket_details.golden_records_individual_id)} | {
            str(pk) for pk in ticket_details.possible_duplicates.values_list("id", flat=True)
        }
        duplicate_ids = [str(individual_id) for individual_id in resolution["duplicate_individual_ids"]]
        distinct_ids = [str(individual_id) for individual_id in resolution["distinct_individual_ids"]]

        unknown = (set(duplicate_ids) | set(distinct_ids)) - ticket_individual_ids
        if unknown:
            raise ValidationError(f"Individuals {sorted(unknown)} do not belong to ticket {ticket.unicef_id}.")

        ticket_details.role_reassign_data = resolution.get("role_reassign_data") or {}
        ticket_details.save(update_fields=["role_reassign_data"])
        ticket_details.selected_individuals.set(duplicate_ids)
        ticket_details.selected_distinct.set(distinct_ids)

        # marks duplicates/distinct, reassigns roles, reports biometric false positives, traverses siblings
        close_needs_adjudication_ticket_service(ticket, user)

        ticket.status = GrievanceTicket.STATUS_CLOSED
        ticket.save()

    @transaction.atomic
    def bulk_add_note(
        self,
        created_by: User,
        tickets_ids: Sequence[str],
        comment: str,
        business_area_slug: str,
    ) -> QuerySet[GrievanceTicket]:
        tickets = GrievanceTicket.objects.filter(~Q(status=GrievanceTicket.STATUS_CLOSED), id__in=tickets_ids)
        if len(tickets) != len(tickets_ids):
            raise ValidationError("Some tickets do not exist, or are closed")
        for ticket in tickets:
            TicketNote.objects.create(ticket=ticket, description=comment, created_by=created_by)
        self._clear_cache(business_area_slug)
        return tickets
