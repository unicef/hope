#!/usr/bin/env bash
# Pre-commit hook: run `makemigrations --check` restricted to FIRST-PARTY apps.
#
# We discover first-party app labels from the filesystem (any directory under
# src/hope/ that contains an apps.py is a Django app owned by this repo). Passing
# these labels as positional args to makemigrations scopes the check and
# prevents third-party site-packages apps (admin, advanced_filters, etc.) from
# producing spurious "Alter field id" migrations that would fail --check on CI.
#
# Convention: the app label equals the last path segment of the app's directory.
# This matches every first-party apps.py we checked (e.g. `account/apps.py` sets
# `label = "account"`; `payment/apps.py` has `name = "hope.apps.payment"` which
# derives label `payment`). If a future app overrides `label` to something other
# than its directory name, add an explicit mapping here.

set -euo pipefail

# Collect unique first-party app labels.
labels=()
declare -A seen
while IFS= read -r apps_py; do
    # Strip the leading "src/hope/" and trailing "/apps.py", keep the last segment.
    rel="${apps_py#src/hope/}"
    dir="${rel%/apps.py}"
    label="${dir##*/}"
    if [[ -z "${seen[$label]:-}" ]]; then
        seen[$label]=1
        labels+=("$label")
    fi
done < <(find src/hope -type f -name apps.py | sort)

if [[ ${#labels[@]} -eq 0 ]]; then
    echo "ERROR: no first-party Django apps found under src/hope/" >&2
    exit 2
fi

exec uv run python manage.py makemigrations --check --dry-run --skip-checks "${labels[@]}"
