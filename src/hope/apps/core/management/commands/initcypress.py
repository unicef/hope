from argparse import ArgumentParser
from typing import Any

from django.conf import settings
from django.core.management import BaseCommand, call_command
from extras.test_utils.factories.account import generate_unicef_partners

from hope.models.user import User
from hope.models.role_assignment import RoleAssignment
from hope.models.role import Role
from hope.models.partner import Partner
from hope.apps.core.management.commands.reset_business_area_sequences import (
    reset_business_area_sequences,
)
from hope.models.core import BusinessArea


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--skip-drop",
            action="store_true",
            default=False,
            help="Skip migrating - just reload the data",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if options["skip_drop"] is False:
            call_command("dropalldb")
            call_command("migrate")

        reset_business_area_sequences()
        call_command("flush", "--noinput")
        generate_unicef_partners()
        call_command("generateroles")
        call_command("init-geo-fixtures")
        call_command("init-core-fixtures")
        # add more fixtures if needed

        partner = Partner.objects.get(name="UNICEF")
        unicef_hq = Partner.objects.get(name=settings.UNICEF_HQ_PARTNER, parent=partner)

        RoleAssignment.objects.create(
            user=User.objects.create_superuser(
                "cypress-username",
                "cypress@cypress.com",
                "cypress-password",
                first_name="Cypress",
                last_name="User",
                status="ACTIVE",
                partner=unicef_hq,
            ),
            role=Role.objects.get(name="Role with all permissions"),
            business_area=BusinessArea.objects.get(name="Afghanistan"),
        )

        call_command("search_index", "--rebuild", "-f")
