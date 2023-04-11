import time
from argparse import ArgumentParser
from typing import Any

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.db import OperationalError, connections

from hct_mis_api.apps.account.models import Role, User, UserRole
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import (
    generate_payment_plan,
    generate_real_cash_plans,
    generate_reconciled_payment_plan,
)
from hct_mis_api.apps.registration_datahub.management.commands.fix_unicef_id_imported_individuals_and_households import (
    update_mis_unicef_id_individual_and_household,
)


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--skip-drop",
            action="store_true",
            default=False,
            help="Skip migrating - just reload the data",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        db_connection = connections["default"]
        connected = False

        while not connected:
            try:
                db_connection.cursor()
                time.sleep(0.5)
            except OperationalError:
                connected = False
            else:
                connected = True

        if options["skip_drop"] is False:
            call_command("dropalldb")
            call_command("migratealldb")

        call_command("flush", "--noinput")
        call_command("flush", "--noinput", database="cash_assist_datahub_mis")
        call_command("flush", "--noinput", database="cash_assist_datahub_ca")
        call_command("flush", "--noinput", database="cash_assist_datahub_erp")
        call_command("flush", "--noinput", database="registration_datahub")

        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/core/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/account/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/registration_data/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/household/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/grievance/fixtures/data.json")
        call_command("loaddata", f"{settings.PROJECT_ROOT}/apps/accountability/fixtures/data.json")

        call_command(
            "loaddata",
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/fixtures/data.json",
            database="registration_datahub",
        )
        call_command(
            "loaddata",
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/fixtures/diiadata.json",
            database="registration_datahub",
        )
        call_command("loaddata", "hct_mis_api/apps/steficon/fixtures/data.json")

        call_command("search_index", "--rebuild", "-f")
        update_mis_unicef_id_individual_and_household()
        generate_payment_plan()
        generate_real_cash_plans()
        generate_reconciled_payment_plan()

        email_list = [
            "jan.romaniak@kellton.com",
            "jakub.krasnowski@kellton.com",
            "pavlo.mokiichuk@kellton.com",
            "kamil.swiechowski@kellton.com",
            "karolina.sliwinska@kellton.com",
            "katarzyna.lanecka@kellton.com",
            "konrad.marzec@kellton.com",
            "maciej.szewczyk@kellton.com",
            "marek.biczysko@kellton.com",
            "patryk.dabrowski@kellton.com",
            "zuzanna.okrutna@kellton.com",
            "gerba@unicef.org",
            "ddinicola@unicef.org",
            "sapostolico@unicef.org",
            "ntrncic@unicef.org",
            "aafaour@unicef.org",
            "aboncenne@unicef.org",
            "asrugano@unicef.org",
            "gkeriri@unicef.org",
            "jbassette@unicef.org",
            "jyablonski@unicef.org",
            "nmkuzi@unicef.org",
            "swaheed@unicef.org",
        ]
        pm_list = [
            "khaddad@unicef.org",
            "stoor@unicef.org",
            "jhalding@unicef.org",
            "ysokadjo@unicef.org",
            "nkuma@unicef.org",
            "hatify@unicef.org",
            "gfranco@unicef.org",
            "ilutska@unicef.org",
            "okozyrenko@unicef.org",
        ]

        role_with_all_perms = Role.objects.get(name="Role with all permissions")
        afghanistan = BusinessArea.objects.get(slug="afghanistan")

        for email in email_list + pm_list:
            user = User.objects.create_user(email, email, "password")
            UserRole.objects.create(
                user=user,
                role=role_with_all_perms,
                business_area=afghanistan,
            )
            if email in email_list:
                user.is_staff = True
                user.is_superuser = True
            user.set_unusable_password()
            user.save()
