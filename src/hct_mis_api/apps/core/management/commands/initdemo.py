"""
Django Management Command: initdemo

This command initializes demo data for the application by performing the following steps:

1. **Database Setup**:
    - Waits for the default database connection to be available.
    - Optionally drops existing databases unless the `--skip-drop` flag is used.
    - Migrates the databases to apply the latest schema.
    - Flushes specified databases to remove existing data.

2. **Fixture Loading**:
    - Loads a series of JSON fixtures into the databases to populate them with initial data.
    - Rebuilds the Elasticsearch search index to ensure it's in sync with the loaded data.

3. **Data Generation**:
    - Generates additional data such as delivery mechanisms, payment plans, and reconciled payment plans.
    - Updates Financial Service Providers (FSPs) with the latest information.

4. **User Creation**:
    - Creates users based on provided email lists, assigning appropriate roles and permissions.
    - Users can be added as staff, superusers, or testers based on input.

5. **Logging and Error Handling**:
    - Logs key actions and errors to assist with debugging and monitoring the initialization process.

**Usage Examples**:

- Initialize demo data with default settings:
  ```bash
  python manage.py initdemo
  ```

- Initialize demo data without dropping existing databases:
  ```bash
  python manage.py initdemo --skip-drop
  ```

- Initialize demo data and add specific staff and tester users:
  ```bash
  python manage.py initdemo --email-list="admin@example.com,user@example.com" --tester-list="tester1@example.com,tester2@example.com"
  ```

**Environment Variables**:

- `INITDEMO_EMAIL_LIST`: Comma-separated list of emails to be added as staff and superusers.
- `INITDEMO_TESTER_LIST`: Comma-separated list of emails to be added as testers.
"""

import logging
import os
import time
from argparse import ArgumentParser
from typing import Any, List

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.db import OperationalError, connections
from django.utils import timezone

import elasticsearch

from hct_mis_api.apps.account.models import Partner, Role, User, UserRole
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import (
    generate_delivery_mechanisms,
    generate_payment_plan,
    generate_real_cash_plans,
    generate_reconciled_payment_plan,
    update_fsps,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Initialize demo data for the application."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--skip-drop",
            action="store_true",
            default=False,
            help="Skip migrating - just reload the data",
        )
        parser.add_argument(
            "--email-list",
            type=str,
            help="Comma-separated list of emails to be added as staff and superusers",
        )
        parser.add_argument(
            "--tester-list",
            type=str,
            help="Comma-separated list of emails to be added as testers",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        start_time = timezone.now()
        db_connection = connections["default"]
        connected = False

        self.stdout.write("Waiting for database connection...")
        while not connected:
            try:
                db_connection.cursor()
                connected = True
            except OperationalError:
                connected = False
                time.sleep(0.5)

        if not options["skip_drop"]:
            self.stdout.write("Dropping existing databases...")
            call_command("dropalldb")
            self.stdout.write("Migrating databases...")
            call_command("migratealldb")

        # Flush databases
        self.stdout.write("Flushing databases...")
        call_command("flush", "--noinput")

        # Load fixtures
        fixtures = [
            "apps/geo/fixtures/data.json",
            "apps/core/fixtures/data.json",
            "apps/account/fixtures/data.json",
            "apps/core/fixtures/businessareapartnerthrough.json",
            "apps/program/fixtures/data.json",
            "apps/registration_data/fixtures/data.json",
            "apps/household/fixtures/documenttype.json",
            "apps/household/fixtures/data.json",
            "apps/accountability/fixtures/data.json",
            "apps/steficon/fixtures/data.json",
            "contrib/aurora/fixtures/data.json",
        ]
        self.stdout.write("Loading fixtures...")
        for fixture in fixtures:
            self.stdout.write(f"Loading fixture: {fixture}")
            call_command("loaddata", f"{settings.PROJECT_ROOT}/{fixture}")

        try:
            self.stdout.write("Rebuilding search index...")
            call_command("search_index", "--rebuild", "-f")
        except elasticsearch.exceptions.RequestError as e:
            logger.error(f"Elasticsearch RequestError: {e}")

        # Generate additional data
        self.stdout.write("Generating delivery mechanisms...")
        generate_delivery_mechanisms()
        self.stdout.write("Generating payment plan...")
        generate_payment_plan()
        self.stdout.write("Generating real cash plans...")
        generate_real_cash_plans()
        self.stdout.write("Generating reconciled payment plan...")
        generate_reconciled_payment_plan()
        self.stdout.write("Updating FSPs...")
        update_fsps()

        # Load more fixtures
        additional_fixtures = [
            "apps/core/fixtures/pdu.json",
            "apps/program/fixtures/programpartnerthrough.json",
            "apps/grievance/fixtures/data.json",
        ]
        self.stdout.write("Loading additional fixtures...")
        for fixture in additional_fixtures:
            self.stdout.write(f"Loading fixture: {fixture}")
            call_command("loaddata", f"{settings.PROJECT_ROOT}/{fixture}")

        # Retrieve email lists from environment variables or command-line arguments
        email_list_env = os.getenv("INITDEMO_EMAIL_LIST")
        tester_list_env = os.getenv("INITDEMO_TESTER_LIST")

        email_list = (
            options["email_list"].split(",")
            if options.get("email_list")
            else email_list_env.split(",")
            if email_list_env
            else []
        )

        tester_list = (
            options["tester_list"].split(",")
            if options.get("tester_list")
            else tester_list_env.split(",")
            if tester_list_env
            else []
        )

        if email_list or tester_list:
            role_with_all_perms = Role.objects.get(name="Role with all permissions")
            afghanistan = BusinessArea.objects.get(slug="afghanistan")
            partner = Partner.objects.get(name="UNICEF")

            combined_email_list: List[str] = [email.strip() for email in email_list + tester_list if email.strip()]

            if combined_email_list:
                self.stdout.write("Creating users...")
                for email in combined_email_list:
                    try:
                        user = User.objects.create_user(email, email, "password", partner=partner)
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
                        self.stdout.write(self.style.SUCCESS(f"Created user: {email}"))
                    except Exception as e:
                        logger.error(f"Failed to create user {email}: {e}")
                        self.stderr.write(self.style.ERROR(f"Failed to create user {email}: {e}"))
        else:
            self.stdout.write("No email lists provided. Skipping user creation.")

        self.stdout.write(self.style.SUCCESS(f"Done in {timezone.now() - start_time}"))
