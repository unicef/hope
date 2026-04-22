#!/usr/bin/env bash
# Pre-commit hook: ensure first-party Django migrations are both up-to-date
# and tracked in git.
#
# We scope `makemigrations --check` to first-party app labels so third-party
# site-packages apps (admin, advanced_filters, ...) can't raise spurious
# migration diffs that would fail --check on CI. Labels come from Django's
# app registry — authoritative, not dependent on filesystem conventions like
# the presence of apps.py.
#
# We then verify no first-party migration file exists on disk without being
# tracked in git: `--check` passes whenever the file is on disk, so a dev who
# runs makemigrations locally but forgets `git add` would otherwise slip
# through. This second check catches that.

set -euo pipefail

uv run python manage.py shell --no-startup -c "
from django.apps import apps
from django.core.management import call_command

labels = sorted({
    a.label
    for a in apps.get_app_configs()
    if a.name == 'hope' or a.name.startswith('hope.')
})
if not labels:
    raise SystemExit('ERROR: no first-party Django apps found in INSTALLED_APPS')

call_command('makemigrations', '--check', '--dry-run', '--skip-checks', *labels)
"

untracked_migrations="$(
    git ls-files --others --exclude-standard -- 'src/hope/' \
        | grep -E '/migrations/[^/]+\.py$' || true
)"
if [[ -n "$untracked_migrations" ]]; then
    {
        echo "ERROR: migration files present on disk but not tracked in git:"
        echo "$untracked_migrations"
        echo "Run 'git add' on these files (or delete them) before committing."
    } >&2
    exit 1
fi
