"""
Management command to update program_registration_id for households in an active program
in the Afghanistan business area with random 8-character strings.
"""

import secrets
import string
from django.core.management.base import BaseCommand
from django.db.models import Q

from hope.models import Household, Program
from hope.models.business_area import BusinessArea


class Command(BaseCommand):
    help = (
        "Update program_registration_id for the first 100 households in an active program "
        "in Afghanistan business area with random 8-character strings"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--business-area",
            type=str,
            default="AF",
            help="Business area slug (default: AF for Afghanistan)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without making changes",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Number of households to update (default: 100)",
        )

    def generate_random_string(self, length=8):
        """Generate a random 8-character string (alphanumeric)."""
        return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

    def handle(self, *args, **options):
        business_area_slug = options["business_area"]
        dry_run = options["dry_run"]
        limit = options["limit"]

        try:
            business_area = BusinessArea.objects.get(slug=business_area_slug)
        except BusinessArea.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Business area with slug '{business_area_slug}' not found")
            )
            return

        # Find active programs in the business area
        active_programs = Program.objects.filter(
            business_area=business_area,
            status=Program.ACTIVE,
        )

        if not active_programs.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"No active programs found in business area '{business_area_slug}'"
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Found {active_programs.count()} active program(s) in '{business_area_slug}'"
            )
        )

        # Get households from active programs
        households = Household.objects.filter(
            program__in=active_programs,
            withdrawn=False,
        ).order_by("created_at")[:limit]

        if not households.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"No households found in active programs in '{business_area_slug}'"
                )
            )
            return

        updated_count = 0
        failed_count = 0

        self.stdout.write(f"\nProcessing {households.count()} households...")
        self.stdout.write("-" * 80)

        for household in households:
            old_id = household.program_registration_id
            new_id = self.generate_random_string(8)

            if dry_run:
                self.stdout.write(
                    f"[DRY RUN] HH {household.unicef_id}: "
                    f"'{old_id}' -> '{new_id}'"
                )
                updated_count += 1
            else:
                try:
                    household.program_registration_id = new_id
                    household.save(update_fields=["program_registration_id"])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ HH {household.unicef_id}: "
                            f"'{old_id}' -> '{new_id}'"
                        )
                    )
                    updated_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ HH {household.unicef_id}: Failed - {str(e)}"
                        )
                    )
                    failed_count += 1

        self.stdout.write("-" * 80)
        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted! Updated: {updated_count}, Failed: {failed_count}"
            )
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n[DRY RUN MODE] - No changes were made to the database")
            )
