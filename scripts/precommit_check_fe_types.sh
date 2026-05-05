#!/usr/bin/env bash
# Pre-commit heuristic: if BE REST-API-shaping files are staged, require a staged
# update under src/frontend/src/restgenerated/ in the same commit.
#
# This catches the common "forgot to regen FE types after BE filter/serializer
# change" mistake. It does NOT guarantee the generated output matches the new
# backend — that requires a live BE at :8080 (not available in a pre-commit).
#
# To regenerate: (BE running on :8080) cd src/frontend && bun run generate-rest-api-types

set -euo pipefail

BE_TRIGGER_RE='^src/hope/apps/.*/(filters|serializers|views)\.py$'
FE_GENERATED_PREFIX='src/frontend/src/restgenerated/'

staged_files="$(git diff --cached --name-only --diff-filter=ACMR)"

be_changed="$(printf '%s\n' "$staged_files" | grep -E "$BE_TRIGGER_RE" || true)"

if [[ -z "$be_changed" ]]; then
    exit 0
fi

fe_changed="$(printf '%s\n' "$staged_files" | grep -F "$FE_GENERATED_PREFIX" || true)"

if [[ -n "$fe_changed" ]]; then
    exit 0
fi

cat >&2 <<EOF
ERROR: Backend REST API files changed but no frontend types were regenerated.

Staged BE files that may change the REST API:
$(printf '  %s\n' $be_changed)

Expected staged changes under:
  ${FE_GENERATED_PREFIX}

To regenerate (requires backend running on localhost:8080):
  cd src/frontend && bun run generate-rest-api-types

If this change does not actually affect the REST API surface, bypass with:
  SKIP=fe-types-drift git commit ...
EOF
exit 1
