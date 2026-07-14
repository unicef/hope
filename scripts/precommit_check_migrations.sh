#!/usr/bin/env bash
set -euo pipefail

COMPOSE=(docker compose -f development_tools/compose.yml -f development_tools/compose.override.yml)

# Computed on the host (which has .git); passed into the container so the
# Django command never needs git itself. Empty value = no untracked files.
UNTRACKED_MIGRATIONS=$(git ls-files --others --exclude-standard -- src/hope/ 2>/dev/null || true)
export UNTRACKED_MIGRATIONS

if [[ -n "${LINT_NOT_ON_DOCKER:-}" ]]; then
    if command -v uv >/dev/null 2>&1; then
        exec uv run python manage.py check_missing_migrations
    fi
elif "${COMPOSE[@]}" ps --status running --services 2>/dev/null | grep -qx backend; then
    exec "${COMPOSE[@]}" exec -T -e UNTRACKED_MIGRATIONS backend python manage.py check_missing_migrations
elif command -v uv >/dev/null 2>&1; then
    exec uv run python manage.py check_missing_migrations
fi

cat >&2 <<EOF
ERROR: cannot run Django missing-migrations check.

Need ONE of:
  - backend container running:
      make services && docker compose -f development_tools/compose.yml \\
          -f development_tools/compose.override.yml up -d backend
  - uv installed on PATH (local venv workflow)

Bypass for this commit:
  SKIP=django-makemigrations-check git commit ...
EOF
exit 1
