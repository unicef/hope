#!/usr/bin/env bash
set -e

# ─── Home-brew GLib / GObject / Pango paths ───
export HOMEBREW_PREFIX="$(brew --prefix)"
export GLIB_PREFIX="$(brew --prefix glib)"
export DYLD_FALLBACK_LIBRARY_PATH="$HOMEBREW_PREFIX/lib:${DYLD_FALLBACK_LIBRARY_PATH:-}"
export GI_TYPELIB_PATH="$(brew --prefix gobject-introspection)/lib/girepository-1.0:$(brew --prefix pango)/lib/girepository-1.0:${GI_TYPELIB_PATH:-}"
# ───────────────────────────────────────────────

# ---------- Front-end (Vite) ----------
pushd src/frontend > /dev/null
yarn
echo "▶︎  Starting Frontend DevServer (Vite)"
yarn dev &                       # runs in background
PID_VITE=$!
popd > /dev/null

# ---------- Back-end (Django) ----------
uv sync --no-install-package hope
echo "▶︎  Starting Backend DevServer (Django)"
python manage.py runserver 127.0.0.1:8080 &   # background
PID_DJANGO=$!

# ---------- Celery Beat ----------
echo "▶︎  Starting Celery Beat"
celery -A hct_mis_api.apps.core.celery beat \
       -l INFO \
       --scheduler hct_mis_api.apps.core.models:CustomDatabaseScheduler &   # background
PID_BEAT=$!

# ---------- Celery Worker (auto-restart) ----------
echo "▶︎  Starting Celery Worker (watchmedo auto-restart)"
watchmedo auto-restart \
         --directory=./ \
         --pattern='*.py' \
         --recursive -- \
         celery -A hct_mis_api.apps.core.celery worker \
                -E -l info \
                -Q default,priority \
                --max-tasks-per-child=4 \
                --concurrency=4 &          # background
PID_WORKER=$!

# ---------- Graceful shutdown ----------
trap 'echo ""; echo "⇢  Stopping all services…"; \
      kill $PID_VITE $PID_DJANGO $PID_BEAT $PID_WORKER' SIGINT SIGTERM

# Wait for any child to exit; the trap handles cleanup.
wait
