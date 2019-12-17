#!/usr/bin/env bash
set -e

if [ $# -eq 0 ]; then
    exec gunicorn hct_mis_api.wsgi -c /code/gunicorn_config.py
else
    case "$1" in
        "dev")
        python manage.py collectstatic --no-input
        python manage.py migrate
        python manage.py runserver 0.0.0.0:8000
        ;;
    *)
    exec "$@"
    ;;
    esac
fi
