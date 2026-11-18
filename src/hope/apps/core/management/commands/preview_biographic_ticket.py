# Local-only preview helper for REVIEW #6 — do not commit.
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.needs_adjudication_ticket_services import (
    create_grouped_grievance_ticket_from_hde_findings_with_details,
)
from hope.models import BiographicDedupeSimilarityPair, Individual


class Command(BaseCommand):
    help = "Create one grouped biographic Needs Adjudication ticket (FOR_APPROVAL) from existing demo individuals."

    @transaction.atomic
    def handle(self, *args: object, **options: object) -> None:
        main = (
            Individual.objects.filter(registration_data_import__isnull=False, household__isnull=False)
            .select_related("program", "registration_data_import")
            .first()
        )
        if main is None:
            raise CommandError("No merged individual with RDI and household; run `make initdemo` first.")
        others = list(Individual.objects.filter(program=main.program, household__isnull=False).exclude(id=main.id)[:2])
        if len(others) < 2:
            raise CommandError(f"Program {main.program} needs at least 3 individuals.")

        pairs = []
        for other, score in zip(others, (Decimal("12.50"), Decimal("20.00")), strict=True):
            individual1_id, individual2_id = sorted([main.id, other.id], key=str)
            pair, _ = BiographicDedupeSimilarityPair.objects.update_or_create(
                program=main.program,
                individual1_id=individual1_id,
                individual2_id=individual2_id,
                defaults={"similarity_score": score, "proximity_to_score": score - Decimal("10.00")},
            )
            pairs.append(pair)

        ticket, _ = create_grouped_grievance_ticket_from_hde_findings_with_details(
            main_individual=main,
            pairs=pairs,
            business_area=main.program.business_area,
            registration_data_import=main.registration_data_import,
        )
        if ticket is None:
            raise CommandError("An open biographic ticket for these individuals already exists; close it and rerun.")
        GrievanceTicket.objects.filter(pk=ticket.pk).update(status=GrievanceTicket.STATUS_FOR_APPROVAL)

        details = ticket.ticket_details
        self.stdout.write(f"possible_duplicate: {details.possible_duplicate_id}")
        self.stdout.write(f"extra_data.possible_duplicate: {details.extra_data.get('possible_duplicate')}")
        self.stdout.write(
            f"http://localhost:3000/{main.program.business_area.slug}/programs/{main.program.code}"
            f"/grievance/tickets/system-generated/{ticket.pk}"
        )
