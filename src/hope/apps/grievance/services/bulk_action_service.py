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
from hope.apps.grievance.utils import validate_individual_for_need_adjudication
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
    def _open_tickets(self, tickets_ids: Sequence[str], business_area_slug: str) -> QuerySet[GrievanceTicket]:
        return GrievanceTicket.objects.filter(
            ~Q(status=GrievanceTicket.STATUS_CLOSED),
            id__in=tickets_ids,
            business_area__slug=business_area_slug,
        )

    def _clear_cache(self, business_area_slug: str) -> None:
        cache_key = f"count_{business_area_slug}_GrievanceTicketNodeConnection_"
        clear_cache_for_key(cache_key)

    @transaction.atomic
    def bulk_assign(
        self,
        tickets_ids: Sequence[str],
        assigned_to_id: str | None,
        business_area_slug: str,
        action_user: User | None = None,
    ) -> QuerySet[GrievanceTicket]:
        user = get_object_or_404(User, id=assigned_to_id)
        queryset = self._open_tickets(tickets_ids, business_area_slug)

        new_tickets = queryset.filter(status=GrievanceTicket.STATUS_NEW)
        # Capture which tickets actually change assignee before the update; only those count as assigned.
        reassigned_ids = list(queryset.exclude(assigned_to=user).values_list("id", flat=True))

        now = timezone.now()
        updated_count = queryset.update(assigned_to=user, updated_at=now)
        if updated_count != len(tickets_ids):
            raise ValidationError("Some tickets do not exist or are closed")
        if reassigned_ids:
            queryset.filter(id__in=reassigned_ids).update(assigned_at=now, assigned_by=action_user)

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
        queryset = self._open_tickets(tickets_ids, business_area_slug)
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
        queryset = self._open_tickets(tickets_ids, business_area_slug)
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
            .order_by("pk")
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
    ) -> tuple[list[GrievanceTicket], list[GrievanceTicket]]:
        """Resolve and auto-close the selected Needs Adjudication tickets in one batch.

        Each resolution marks individuals as duplicate/distinct and closes the ticket directly,
        bypassing the FOR_APPROVAL step. Returns the tickets it resolved and, separately, the ones
        somebody else closed in the meantime, which are skipped. If any other ticket is missing, is
        not a Needs Adjudication ticket, or is not resolvable by this user, nothing is committed.
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
            .order_by("pk")
            .select_for_update(of=("self",))
            .select_related(*_ACTIVITY_LOG_SELECT_RELATED)
            .prefetch_related("programs")
        )
        skipped_closed: list[GrievanceTicket] = []
        if len(tickets) != len(ticket_ids):
            missing_ids = set(ticket_ids) - {str(ticket.id) for ticket in tickets}
            skipped_closed = list(
                GrievanceTicket.objects.filter(
                    id__in=missing_ids,
                    category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
                    business_area__slug=business_area_slug,
                    status=GrievanceTicket.STATUS_CLOSED,
                ).order_by("unicef_id")
            )
            if len(skipped_closed) != len(missing_ids):
                raise ValidationError("Some selected tickets do not exist or are not Needs Adjudication tickets.")

        required = [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE.value,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK.value,
        ]
        for ticket in tickets:
            scope = ticket.programs.first() or ticket.business_area
            if not all(user.has_perm(permission, scope) for permission in required):
                raise PermissionDenied(detail={"required_permissions": required})

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
        return tickets, skipped_closed

    def _resolve_single_needs_adjudication(self, ticket: GrievanceTicket, resolution: dict, user: User) -> None:
        ticket_details = ticket.ticket_details
        ticket_individuals = {
            str(individual.id): individual
            for individual in [
                ticket_details.golden_records_individual,
                ticket_details.possible_duplicate,
                *ticket_details.possible_duplicates.all(),
            ]
            if individual is not None
        }
        duplicate_ids = [str(individual_id) for individual_id in resolution["duplicate_individual_ids"]]
        distinct_ids = [str(individual_id) for individual_id in resolution["distinct_individual_ids"]]

        unknown = (set(duplicate_ids) | set(distinct_ids)) - ticket_individuals.keys()
        if unknown:
            raise ValidationError(f"Individuals {sorted(unknown)} do not belong to ticket {ticket.unicef_id}.")

        for individual_id in duplicate_ids + distinct_ids:
            validate_individual_for_need_adjudication(user.partner, ticket_individuals[individual_id], ticket_details)

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
        tickets = self._open_tickets(tickets_ids, business_area_slug)
        if len(tickets) != len(tickets_ids):
            raise ValidationError("Some tickets do not exist, or are closed")
        for ticket in tickets:
            TicketNote.objects.create(ticket=ticket, description=comment, created_by=created_by)
        self._clear_cache(business_area_slug)
        return tickets
