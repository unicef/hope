"""dedup_teardown — remove everything dedup_setup created.

Each BusinessArea built by dedup_setup is stamped in ``custom_fields`` with
``dedup_harness=True`` and ``dedup_harness_run=<tag>``.

Why this deletes the way it does. Individual/Household/Program are HOPE
soft-delete models: an *instance* ``.delete()`` only flips ``is_removed``, while
a *QuerySet* ``.delete()`` runs Django's collector (a real SQL delete). The
collector also enforces a PROTECT cycle — ``Household.head_of_household`` ->
Individual and ``Individual.household`` -> Household — plus PROTECTs on
``Individual.program`` / ``Household.program`` / ``*.registration_data_import``.
So a single ``BusinessArea.delete()`` (or RDI-first delete) raises ProtectedError.

The robust path is explicit bottom-up on the ``all_objects`` (BaseManager)
querysets, breaking the cycle first by nulling the nullable side
(``Individual.household``), then deleting leaves -> roots so no level is ever
protected by a child that still exists:

    individuals.update(household=None)  ->  households  ->  individuals
      ->  RDIs  ->  program cycles  ->  programs  ->  business areas

ES program indexes (no DB FK) and the orphaned Household/Individual
*collections* (FK points the wrong way; collections carry no business_area) are
captured up front and removed explicitly.

    ./manage.py dedup_teardown --run-id <tag>   # one run
    ./manage.py dedup_teardown --all            # every harness run
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.core.management import BaseCommand

from hope.apps.household.services.index_management import delete_program_indexes
from hope.models import (
    BusinessArea,
    Household,
    HouseholdCollection,
    Individual,
    IndividualCollection,
    Partner,
    Program,
    ProgramCycle,
    RegistrationDataImport,
    RoleAssignment,
)

if TYPE_CHECKING:
    from argparse import ArgumentParser


class Command(BaseCommand):
    help = "Remove the dedup-regression substrate created by dedup_setup (BAs + dependents + collections + ES indexes)."

    def add_arguments(self, parser: ArgumentParser) -> None:
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--run-id", dest="run_id", help="Remove only the run stamped with this tag.")
        group.add_argument("--all", dest="all", action="store_true", help="Remove every dedup-harness run.")

    def handle(self, *args: Any, **options: Any) -> None:
        if options["all"]:
            bas = BusinessArea.objects.filter(custom_fields__dedup_harness=True)
        else:
            bas = BusinessArea.objects.filter(custom_fields__dedup_harness_run=options["run_id"])

        ba_ids = list(bas.values_list("id", flat=True))
        if not ba_ids:
            self.stdout.write("Nothing to remove.")
            return

        # Capture (before any delete) what the FK graph won't reach on its own.
        program_ids = list(Program.all_objects.filter(business_area_id__in=ba_ids).values_list("id", flat=True))
        hh_coll_ids = list(
            HouseholdCollection.objects.filter(households__business_area_id__in=ba_ids)
            .values_list("id", flat=True)
            .distinct()
        )
        ind_coll_ids = list(
            IndividualCollection.objects.filter(individuals__business_area_id__in=ba_ids)
            .values_list("id", flat=True)
            .distinct()
        )
        # The `business_area_created` signal creates one "UNICEF Partner for <slug>"
        # sub-partner per BA (plus its RoleAssignment). Deleting the BA does not
        # reach the Partner, so capture them now — otherwise a same-tag re-run
        # collides on account_partner_name_key. Capture by exact signal-generated
        # name to avoid touching the shared UNICEF / UNICEF HQ partners that also
        # link to these BAs.
        subpartner_ids = list(
            Partner.objects.filter(
                name__in=[f"UNICEF Partner for {slug}" for slug in bas.values_list("slug", flat=True)]
            ).values_list("id", flat=True)
        )

        for program_id in program_ids:
            delete_program_indexes(str(program_id))

        # Bottom-up hard delete on BaseManager (all_objects) querysets.
        # 1) break the Household <-> Individual PROTECT cycle via the nullable side.
        Individual.all_objects.filter(business_area_id__in=ba_ids).update(household=None)
        # 2) leaves -> roots.
        Household.all_objects.filter(business_area_id__in=ba_ids).delete()
        Individual.all_objects.filter(business_area_id__in=ba_ids).delete()
        RegistrationDataImport.objects.filter(business_area_id__in=ba_ids).delete()
        ProgramCycle.objects.filter(program__business_area_id__in=ba_ids).delete()
        Program.all_objects.filter(business_area_id__in=ba_ids).delete()
        BusinessArea.objects.filter(id__in=ba_ids).delete()
        # 3) orphaned collections (no business_area FK to reach them).
        HouseholdCollection.objects.filter(id__in=hh_coll_ids).delete()
        IndividualCollection.objects.filter(id__in=ind_coll_ids).delete()
        # 4) signal-created sub-partners (RoleAssignments first, in case the
        # BA delete didn't cascade them, then the now-unreferenced partners).
        RoleAssignment.objects.filter(partner_id__in=subpartner_ids).delete()
        Partner.objects.filter(id__in=subpartner_ids).delete()

        self.stdout.write(
            f"=== DEDUP TEARDOWN DONE === removed {len(ba_ids)} BA(s), {len(program_ids)} program(s), "
            f"{len(hh_coll_ids)} hh-collection(s), {len(ind_coll_ids)} ind-collection(s), "
            f"{len(subpartner_ids)} sub-partner(s)"
        )
