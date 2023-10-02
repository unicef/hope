from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.grievance.constants import PRIORITY_CHOICES, URGENCY_CHOICES
from hct_mis_api.apps.grievance.models import GrievanceTicket, TicketNote


class BulkActionService:
    @transaction.atomic
    def bulk_assign(self, tickets_ids, assigned_to):
        user = get_object_or_404(User, id=assigned_to)
        updated_count = GrievanceTicket.objects.filter(id__in=tickets_ids).update(assigned_to=user)
        if updated_count != len(tickets_ids):
            raise ValidationError("Some tickets do not exist")

    @transaction.atomic
    def bulk_set_priority(self, tickets_ids, priority):
        if priority not in [x for x,y in PRIORITY_CHOICES]:
            raise ValidationError("Invalid priority")
        updated_count = GrievanceTicket.objects.filter(id__in=tickets_ids).update(priority=priority)
        if updated_count != len(tickets_ids):
            raise ValidationError("Some tickets do not exist")

    @transaction.atomic
    def bulk_set_urgency(self, tickets_ids, urgency):
        if urgency not in [x for x, y in URGENCY_CHOICES]:
            raise ValidationError("Invalid priority")
        updated_count = GrievanceTicket.objects.filter(id__in=tickets_ids).update(urgency=urgency)
        if updated_count != len(tickets_ids):
            raise ValidationError("Some tickets do not exist")

    @transaction.atomic
    def bulk_add_note(self, tickets_ids, comment):
        tickets = GrievanceTicket.objects.filter(id__in=tickets_ids)
        if len(tickets) != len(tickets_ids):
            raise ValidationError("Some tickets do not exist")
        for ticket in tickets:
            TicketNote.objects.create(ticket=ticket, comment=comment)
            