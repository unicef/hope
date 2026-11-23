from typing import Any

from django.apps import apps
from django.core.management.base import CommandError
from django.core.management.commands import migrate
from django.db import connections
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.recorder import MigrationRecorder

from hope.apps.core.baseline_guard import baseline_violations


class Command(migrate.Command):
    """Django's migrate behind the baseline guard; see docs/guide-dev/migrations-baseline.md."""

    def handle(self, *args: Any, **options: Any) -> None:
        connection = connections[options["database"]]
        # load=False: no graph is built, so an inconsistent database cannot crash before the guard reports it.
        loader = MigrationLoader(connection, load=False)
        loader.load_disk()
        first_party = {
            cfg.label for cfg in apps.get_app_configs() if cfg.name == "hope" or cfg.name.startswith("hope.")
        }
        violations = baseline_violations(
            loader.disk_migrations,
            MigrationRecorder(connection).applied_migrations(),
            first_party - loader.unmigrated_apps,
        )
        if violations:
            raise CommandError("Refusing to migrate, nothing was changed.\n" + "\n".join(violations))
        super().handle(*args, **options)
