"""dedup_setup — build the dedup-regression test substrate.

Creates two fresh BusinessAreas (one non-CW, one CW-only), each carrying a
MERGED golden-record population (B/D/E) on its own program, indexed into
Elasticsearch (autosync is OFF, so the explicit index is mandatory).

Everything is stamped with a short ``run_id`` in ``BusinessArea.custom_fields``
so ``dedup_teardown`` can remove exactly what this command created.

    ./manage.py dedup_setup [--run-id <tag>]

Field choices mirror ``init_e2e_scenario.create_household_with_individual`` and
the ``_generate_rdi_dedup_demo`` seeder, re-expressed as raw ORM because test
factories do not ship to deployed envs.
"""

from __future__ import annotations

from datetime import date
import json
import secrets
from typing import TYPE_CHECKING, Any

from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from hope.apps.household.const import FEMALE, HEAD, MALE
from hope.apps.household.services.index_management import rebuild_program_indexes
from hope.models import (
    APIToken,
    BeneficiaryGroup,
    BusinessArea,
    Country,
    DataCollectingType,
    Household,
    HouseholdCollection,
    Individual,
    IndividualCollection,
    MergeStatusModel,
    Program,
    ProgramCycle,
    RegistrationDataImport,
    Role,
    RoleAssignment,
    User,
)
from hope.models.grant import Grant

if TYPE_CHECKING:
    from argparse import ArgumentParser

# D and E carry the biographic values the TEST's incoming D'/E' must match
# (ES biographic score >= deduplication_duplicate_score, default 6.0).
# B is a plain filler unique.
POPULATION = [
    # key   given_name   family_name   birth_date            sex
    ("B", "Robert", "Smith", date(1985, 3, 10), MALE),
    ("D", "Maria", "Gonzalez", date(1990, 5, 15), FEMALE),
    ("E", "Ahmed", "Hassan", date(1978, 11, 22), MALE),
]

# (variant slug, BA-code suffix, ingest_source, biometric_dedup)
# non-CW = legacy biographic-only; CW = country-workspace path with biometric dedup on.
VARIANTS = [
    ("noncw", "N", BusinessArea.IngestSource.ALL_EXCEPT_COUNTRY_WORKSPACE, False),
    ("cw", "C", BusinessArea.IngestSource.COUNTRY_WORKSPACE_ONLY, True),
]


class Command(BaseCommand):
    help = (
        "Create the dedup-regression substrate: two fresh BAs (non-CW + CW-only), each with a "
        "MERGED golden-record population indexed into Elasticsearch."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--run-id",
            dest="run_id",
            default=None,
            help="Short tag (<=8 chars) identifying this run; teardown uses it. Default: random hex.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        # Lowercase: the tag feeds program.code, which feeds the ES index name
        # (individuals_<slug>_<code>) — ES rejects any uppercase in an index name.
        tag = (options["run_id"] or secrets.token_hex(3)).lower()
        if len(tag) > 8 or not tag.isalnum():
            raise CommandError("--run-id must be alphanumeric and <= 8 chars (feeds BA code / ES index name).")

        self.dct, self.bg, self.country = self._reference_data()
        self.user = User.objects.filter(is_superuser=True).first()

        result: dict[str, Any] = {"run_id": tag, "variants": {}}
        created_bas: list[BusinessArea] = []
        for variant, suffix, ingest_source, biometric in VARIANTS:
            with transaction.atomic():
                ba = self._create_ba(variant, suffix, ingest_source, tag)
                created_bas.append(ba)
                self._grant_access(ba)
                program = self._create_program(ba, tag, biometric)
                seed_rdi = self._create_seed_rdi(ba, program, tag)
                population = {}
                for key, given, family, dob, sex in POPULATION:
                    ind = self._create_golden_individual(ba, program, seed_rdi, given, family, dob, sex)
                    population[key] = {"id": str(ind.id), "unicef_id": ind.unicef_id}

            ok, msg = rebuild_program_indexes(str(program.id))
            if not ok:
                raise CommandError(f"ES index failed for variant {variant!r}: {msg}")

            result["variants"][variant] = {
                "business_area_id": str(ba.id),
                "business_area_slug": ba.slug,
                "ingest_source": ingest_source,
                "program_id": str(program.id),
                "program_code": program.code,
                "seed_rdi_id": str(seed_rdi.id),
                "population": population,
            }

        token = self._create_api_token(created_bas)
        result["api_token"] = token.key

        self.stdout.write("=== DEDUP SETUP DONE ===")
        self.stdout.write(json.dumps(result, indent=2))
        self.stdout.write("")
        self.stdout.write("=== CW HOPE_API_TOKEN (copy into CW compose env) ===")
        self.stdout.write(token.key)

    # -- reference data (env-existing rows) ---------------------------------
    def _reference_data(self) -> tuple[DataCollectingType, BeneficiaryGroup, Country | None]:
        dct = (
            DataCollectingType.objects.filter(code="partial_individuals").first()
            or DataCollectingType.objects.filter(active=True).first()
        )
        if not dct:
            raise CommandError("Missing reference data on env: no DataCollectingType found")
        # Program.clean() requires the pair to match: this command builds
        # household+individual (master-detail) data, so the beneficiary group's
        # master_detail must align with the dct type. The dct's `type` is
        # env-specific (e.g. partial_individuals is SOCIAL in demo data but
        # STANDARD on deployed envs), so derive the group from it rather than
        # hardcoding a name that only happens to be valid in one environment.
        needs_master_detail = dct.type == DataCollectingType.Type.STANDARD
        bg = BeneficiaryGroup.objects.filter(master_detail=needs_master_detail).first()
        if not bg:
            raise CommandError(
                f"Missing reference data on env: no BeneficiaryGroup with "
                f"master_detail={needs_master_detail} (required for dct {dct.code!r} type {dct.type})"
            )
        return dct, bg, Country.objects.first()

    # -- builders -----------------------------------------------------------
    def _create_ba(self, variant: str, suffix: str, ingest_source: str, tag: str) -> BusinessArea:
        ba = BusinessArea(
            code=f"D{tag}{suffix}",  # <= 10 chars, unique
            name=f"dedup-regression-ba-{variant}-{tag}",
            long_name=f"Dedup Regression {variant} {tag}",
            region_code="DR",
            region_name="DR",
            ingest_source=ingest_source,
            active=True,
            custom_fields={"dedup_harness": True, "dedup_harness_run": tag, "variant": variant},
        )
        ba.save()  # slug auto-generated via unique_slugify; full_clean runs
        if self.country:
            ba.office_country = self.country
            ba.save()
            ba.countries.add(self.country)
        return ba

    def _grant_access(self, ba: BusinessArea) -> None:
        # Accessible BAs come solely from RoleAssignment (user- or partner-based);
        # is_superuser does NOT bypass the BA list (User.business_areas). The
        # business_area_created signal only grants the UNICEF sub-partner / HQ, so
        # without an explicit user grant these BAs 404 in the frontend for whoever
        # runs the harness. Grant every active superuser a full-permission role.
        role = Role.objects.filter(name="Role with all permissions").first()
        if not role:
            raise CommandError("Missing reference data on env: Role 'Role with all permissions' not found")
        for user in User.objects.filter(is_superuser=True, is_active=True):
            RoleAssignment.objects.get_or_create(user=user, business_area=ba, program=None, defaults={"role": role})

    def _create_api_token(self, business_areas: list[BusinessArea]) -> APIToken:
        """Mint a HOPE API token for `root` so CW can authenticate to HOPE's REST API.

        Scoped to every BA built this run (valid_for is M2M -> set after save), all
        grants, valid from now for one year.
        """
        root = User.objects.filter(username="root").first()
        if not root:
            raise CommandError("Missing reference data on env: no User with username 'root' (needed for API token).")
        now = timezone.now()
        token = APIToken.objects.create(
            user=root,
            grants=[grant.value for grant in Grant],
            valid_from=now.date(),
            valid_to=(now + relativedelta(years=1)).date(),
        )
        token.valid_for.set(business_areas)
        return token

    def _create_program(self, ba: BusinessArea, tag: str, biometric: bool) -> Program:
        program = Program.objects.create(
            name=f"dedup-regression-{ba.slug}",
            code=f"{tag[:3]}1",  # max_length=4, unique per BA (fresh BA -> safe)
            business_area=ba,
            status=Program.ACTIVE,
            start_date=date(2024, 1, 1),
            end_date=date(2030, 12, 31),
            budget="100000.00",
            frequency_of_payments=Program.ONE_OFF,
            sector=Program.MULTI_PURPOSE,
            scope="UNICEF",
            cash_plus=False,
            population_goal=100,
            data_collecting_type=self.dct,
            beneficiary_group=self.bg,
            biometric_deduplication_enabled=biometric,  # non-CW off (biographic); CW on
        )
        ProgramCycle.objects.create(
            program=program,
            title=f"Cycle {tag}",
            status=ProgramCycle.ACTIVE,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )
        return program

    def _create_seed_rdi(self, ba: BusinessArea, program: Program, tag: str) -> RegistrationDataImport:
        """One synthetic MERGED RDI anchors the golden-record population."""
        return RegistrationDataImport.objects.create(
            name=f"seed-{tag}-{ba.slug}",
            status=RegistrationDataImport.MERGED,
            data_source=RegistrationDataImport.XLS,
            business_area=ba,
            program=program,
            imported_by=self.user,
            import_date=timezone.now(),
            number_of_individuals=len(POPULATION),
            number_of_households=len(POPULATION),
            screen_beneficiary=False,
        )

    def _create_golden_individual(  # noqa: PLR0913
        self,
        ba: BusinessArea,
        program: Program,
        rdi: RegistrationDataImport,
        given_name: str,
        family_name: str,
        birth_date: date,
        sex: str,
    ) -> Individual:
        """Create a MERGED golden-record individual + its household (golden_record_status defaults to UNIQUE)."""
        now = timezone.now()
        hh = Household(
            business_area=ba,
            program=program,
            registration_data_import=rdi,
            first_registration_date=now,
            last_registration_date=now,
            size=1,
            withdrawn=False,
            household_collection=HouseholdCollection.objects.create(),
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        ind = Individual.objects.create(
            business_area=ba,
            program=program,
            registration_data_import=rdi,
            given_name=given_name,
            family_name=family_name,
            full_name=f"{given_name} {family_name}",
            birth_date=birth_date,
            sex=sex,
            relationship=HEAD,
            first_registration_date=now,
            last_registration_date=now,
            individual_collection=IndividualCollection.objects.create(),
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        hh.head_of_household = ind
        hh.save()
        ind.household = hh
        ind.save()
        return ind
