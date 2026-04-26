import re
import subprocess
from typing import Any

from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

# Matches files directly inside a migrations/ package, e.g. src/hope/apps/foo/migrations/0001_init.py.
# Excludes anything nested deeper than one level below migrations/.
_MIGRATION_FILE_RE = re.compile(r"/migrations/[^/]+\.py$")


class Command(BaseCommand):
    help = (
        "Verify first-party Django migrations are up to date and tracked in git. "
        "Scopes `makemigrations --check` to hope.* app labels (so third-party apps "
        "can't produce spurious diffs) and also fails if any migration file exists "
        "on disk without being tracked in git."
    )

    def handle(self, *args: Any, **options: Any) -> None:
        labels = sorted(
            {cfg.label for cfg in apps.get_app_configs() if cfg.name == "hope" or cfg.name.startswith("hope.")}
        )
        if not labels:
            raise CommandError("no first-party Django apps found in INSTALLED_APPS")

        call_command(
            "makemigrations",
            "--check",
            "--dry-run",
            "--skip-checks",
            *labels,
        )

        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "--", "src/hope/"],  # noqa: S607
            check=True,
            capture_output=True,
            text=True,
        )
        untracked = [line for line in result.stdout.splitlines() if _MIGRATION_FILE_RE.search(line)]
        if untracked:
            raise CommandError(
                "migration files present on disk but not tracked in git:\n"
                + "\n".join(untracked)
                + "\nRun 'git add' on these files (or delete them) before committing."
            )
