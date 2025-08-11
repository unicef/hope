from typing import Sequence

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone

from hope.apps.account.models import User
from hope.apps.core.utils import clear_cache_for_key
from hope.apps.grievance.constants import PRIORITY_CHOICES, URGENCY_CHOICES
from hope.apps.grievance.documents import (
    bulk_update_assigned_to,
    bulk_update_priority,
    bulk_update_status,
    bulk_update_urgency,
)
from hope.apps.grievance.models import GrievanceTicket, TicketNote


class BulkActionService:
    def _clear_cache(self, business_area_slug: str) -> None:
        cache_key = f"count_{business_area_slug}_GrievanceTicketNodeConnection_"
        clear_cache_for_key(cache_key)

    @transaction.atomic
    def bulk_assign(
        self, tickets_ids: Sequence[str], assigned_to_id: str | None, business_area_slug: str
    ) -> QuerySet[GrievanceTicket]:
        user = get_object_or_404(User, id=assigned_to_id)
        queryset = GrievanceTicket.objects.filter(~Q(status=GrievanceTicket.STATUS_CLOSED), id__in=tickets_ids)

        new_tickets = queryset.filter(status=GrievanceTicket.STATUS_NEW)
        new_tickets_ids = list(map(str, new_tickets.values_list("id", flat=True)))

        updated_count = queryset.update(assigned_to=user, updated_at=timezone.now())
        if updated_count != len(tickets_ids):
            raise ValidationError("Some tickets do not exist or are closed")

        # Update also status to assigned if status is new
        new_tickets.update(status=GrievanceTicket.STATUS_ASSIGNED)

        self._clear_cache(business_area_slug)

        bulk_update_assigned_to(tickets_ids, assigned_to_id)
        bulk_update_status(new_tickets_ids, GrievanceTicket.STATUS_ASSIGNED)
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
        self._clear_cache(business_area_slug)
        bulk_update_priority(tickets_ids, priority)
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
        self._clear_cache(business_area_slug)
        bulk_update_urgency(tickets_ids, urgency)
        return queryset

    @transaction.atomic
    def bulk_add_note(
        self, created_by: User, tickets_ids: Sequence[str], comment: str, business_area_slug: str
    ) -> QuerySet[GrievanceTicket]:
        tickets = GrievanceTicket.objects.filter(~Q(status=GrievanceTicket.STATUS_CLOSED), id__in=tickets_ids)
        if len(tickets) != len(tickets_ids):
            raise ValidationError("Some tickets do not exist, or are closed")
        for ticket in tickets:
            TicketNote.objects.create(ticket=ticket, description=comment, created_by=created_by)
        self._clear_cache(business_area_slug)
        return tickets
