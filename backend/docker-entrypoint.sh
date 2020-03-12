#!/usr/bin/env bash
set -e

if [ $# -eq 0 ]; then
    exec gunicorn hct_mis_api.wsgi -c /code/gunicorn_config.py
else
    case "$1" in
        "dev")
        until pg_isready -h db -p 5432;
          do echo "waiting for database"; sleep 2; done;
        python manage.py collectstatic --no-input
        python manage.py makemigrations
        python manage.py migrate
        python manage.py loadbusinessareas
        python manage.py migratealldb
        python manage.py generatefixtures
        python manage.py runserver 0.0.0.0:8000

        ;;
    *)
    exec "$@"
    ;;
    esac
fi


