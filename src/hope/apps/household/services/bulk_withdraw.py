from django.db import transaction
from django.db.models import Case, F, Value, When
from django.db.models.expressions import RawSQL
from django.db.models.query import QuerySet
from django.utils import timezone

from hope.apps.core.utils import JSONBSet
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.signals import increment_grievance_ticket_version_cache_for_ticket_ids
from hope.apps.household.api.caches import invalidate_household_and_individual_list_cache
from hope.apps.program.signals import adjust_program_size
from hope.models import Document, Individual, Program


class HouseholdBulkWithdrawService:
    def __init__(self, program: Program) -> None:
        self.program = program

    @transaction.atomic
    def withdraw(self, households_qs: QuerySet, tag: str = "", processed_ticket_id: int | None = None) -> int:
        households = households_qs.filter(withdrawn=False)
        individuals = Individual.objects.filter(household__in=households, withdrawn=False, duplicate=False)

        tickets = GrievanceTicket.objects.belong_households_individuals(households, individuals)
        ticket_ids = list({t.ticket_id for t in tickets if t.ticket_id != processed_ticket_id})

        if ticket_ids:
            previous_status = Case(
                *[
                    When(status=status, then=Value(f'"{status}"'))
                    for status, _ in GrievanceTicket.STATUS_CHOICES
                    if status != GrievanceTicket.STATUS_CLOSED
                ]
            )
            GrievanceTicket.objects.filter(id__in=ticket_ids).exclude(
                status=GrievanceTicket.STATUS_CLOSED
            ).update(
                extras=JSONBSet(F("extras"), Value("{status_before_withdrawn}"), previous_status),
                status=GrievanceTicket.STATUS_CLOSED,
            )
            increment_grievance_ticket_version_cache_for_ticket_ids(self.program.business_area.slug, ticket_ids)

        Document.objects.filter(individual__in=individuals).update(status=Document.STATUS_INVALID)
        individuals.update(withdrawn=True, withdrawn_date=timezone.now())
        count = households.update(
            withdrawn=True,
            withdrawn_date=timezone.now(),
            internal_data=JSONBSet(F("internal_data"), Value("{withdrawn_tag}"), Value(f'"{tag}"')),
        )

        invalidate_household_and_individual_list_cache(self.program.id)
        adjust_program_size(self.program)

        return count

    @transaction.atomic
    def unwithdraw(self, households_qs: QuerySet, reopen_tickets: bool = True) -> int:
        households = households_qs.filter(withdrawn=True)
        individuals = Individual.objects.filter(household__in=households, duplicate=False)

        if reopen_tickets:
            tickets = GrievanceTicket.objects.belong_households_individuals(households, individuals)
            ticket_ids = list({t.ticket_id for t in tickets})

            if ticket_ids:
                GrievanceTicket.objects.filter(
                    id__in=ticket_ids,
                    status=GrievanceTicket.STATUS_CLOSED,
                ).filter(
                    extras__status_before_withdrawn__isnull=False,
                ).exclude(
                    extras__status_before_withdrawn="",
                ).update(
                    status=RawSQL("(extras->>'status_before_withdrawn')::integer", []),
                    extras=JSONBSet(F("extras"), Value("{status_before_withdrawn}"), Value('""')),
                )
                increment_grievance_ticket_version_cache_for_ticket_ids(self.program.business_area.slug, ticket_ids)

        Document.objects.filter(individual__in=individuals).update(status=Document.STATUS_NEED_INVESTIGATION)
        individuals.update(withdrawn=False, withdrawn_date=None)
        count = households.update(withdrawn=False, withdrawn_date=None)

        invalidate_household_and_individual_list_cache(self.program.id)
        adjust_program_size(self.program)

        return count
