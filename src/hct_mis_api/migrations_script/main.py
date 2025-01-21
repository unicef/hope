import csv
import os
from datetime import datetime

import django
from django.core.management import call_command
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")
django.setup()


def export_migration_info_to_csv(filename="migrations_info.csv"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"migrations_info_{timestamp}.csv"
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM django_migrations")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(column_names)
        writer.writerows(rows)
    print(f"Migration info exported to {filename}")


def clear_migration_table():
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM django_migrations")


def fake_migrations(excluded_migrations):
    call_command("migrate", "--fake")
    with connection.cursor() as cursor:
        for app, name in excluded_migrations:
            cursor.execute("DELETE FROM django_migrations WHERE app = %s AND name = %s", [app, name])


def apply_migrations():
    call_command("migrate")
    print("Migrations applied.")


if __name__ == "__main__":
    export_migration_info_to_csv()
    clear_migration_table()
    excluded_migrations = [
        ("targeting", "0002_migration"),
        ("household", "0003_migration"),
        ("household", "0004_migration"),
        ("grievance", "0004_migration"),
        ("payment", "0002_migration"),
        ("payment", "0003_migration"),
        ("payment", "0004_migration"),
        ("payment", "0005_migration"),
        ("payment", "0006_migration"),
        ("payment", "0007_migration"),
        ("payment", "0008_migration"),
        ("payment", "0009_migration"),
        ("payment", "0010_migration"),
        ("aurora", "0003_migration"),
        ("accountability", "0004_migration"),
        ("registration_data", "0002_migration"),
    ]
    fake_migrations(excluded_migrations)
    apply_migrations()
