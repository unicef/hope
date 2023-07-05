from argparse import ArgumentParser
from typing import Any

from django.core.management import BaseCommand, call_command

from hct_mis_api.apps.account.models import Role, User, UserRole
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
            call_command("migratealldb")

        call_command("flush", "--noinput")
        call_command("flush", "--noinput", database="cash_assist_datahub_mis")
        call_command("flush", "--noinput", database="cash_assist_datahub_ca")
        call_command("flush", "--noinput", database="cash_assist_datahub_erp")
        call_command("flush", "--noinput", database="registration_datahub")

        call_command("loaddata", "hct_mis_api/apps/geo/fixtures/data.json")
        call_command("loaddata", "hct_mis_api/apps/core/fixtures/data.json")
        call_command("loaddata", "hct_mis_api/apps/account/fixtures/data.json")
        call_command("loaddata", "hct_mis_api/apps/registration_data/fixtures/data-cypress.json")
        call_command(
            "loaddata",
            "hct_mis_api/apps/registration_datahub/fixtures/data-cypress.json",
            database="registration_datahub",
        )
        call_command("loaddata", "hct_mis_api/apps/household/fixtures/data-cypress.json")
        call_command("loaddata", "hct_mis_api/apps/program/fixtures/data-cypress.json")
        call_command("loaddata", "hct_mis_api/apps/targeting/fixtures/data-cypress.json")
        call_command("loaddata", "hct_mis_api/apps/steficon/fixtures/data-cypress.json")
        call_command("loaddata", "hct_mis_api/apps/payment/fixtures/data-cypress.json")
        call_command("loaddata", "hct_mis_api/apps/grievance/fixtures/data-cypress.json")
        call_command("loaddata", "hct_mis_api/apps/accountability/fixtures/data-cypress.json")

        UserRole.objects.create(
            user=User.objects.create_superuser(
                "cypress-username",
                "cypress@cypress.com",
                "cypress-password",
                first_name="Cypress",
                last_name="User",
                status="ACTIVE",
            ),
            role=Role.objects.get(name="Role with all permissions"),
            business_area=BusinessArea.objects.get(name="Afghanistan"),
        )

        call_command("search_index", "--rebuild", "-f")
