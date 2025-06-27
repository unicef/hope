from argparse import ArgumentParser
from typing import Any

from django.conf import settings
from django.core.management import BaseCommand, call_command

from hct_mis_api.apps.account.models import Partner, Role, User, UserRole
from hct_mis_api.apps.core.management.commands.reset_business_area_sequences import (
    reset_business_area_sequences,
)
from hct_mis_api.apps.core.models import BusinessArea


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
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/account/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/program/fixtures/data-cypress.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data-cypress.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/documenttype.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data-cypress.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/targeting/fixtures/data-cypress.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/steficon/fixtures/data-cypress.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/payment/fixtures/data-cypress.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/grievance/fixtures/data-cypress.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/accountability/fixtures/data-cypress.json")

        partner = Partner.objects.get(name="UNICEF")

        UserRole.objects.create(
            user=User.objects.create_superuser(
                "cypress-username",
                "cypress@cypress.com",
                "cypress-password",
                first_name="Cypress",
                last_name="User",
                status="ACTIVE",
                partner=partner,
            ),
            role=Role.objects.get(name="Role with all permissions"),
            business_area=BusinessArea.objects.get(name="Afghanistan"),
        )

        call_command("search_index", "--rebuild", "-f")
