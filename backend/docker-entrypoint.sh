#!/bin/bash
set -e

if [ $# -eq 0 ]; then
    export NEW_RELIC_CONFIG_FILE=/code/newrelic.ini
    export NEW_RELIC_ENVIRONMENT=$ENV
    exec newrelic-admin run-program gunicorn hct_mis_api.wsgi -c /code/gunicorn_config.py
else
    case "$1" in
        "dev")
            until pg_isready -h db -p 5432;
            do echo "waiting for database"; sleep 2; done;
            python manage.py collectstatic --no-input
            python manage.py migratealldb
            python manage.py runserver 0.0.0.0:8000
        ;;
        "celery-beat")
            waitforit -host=backend -port=8000 --timeout 300 && \
            celery -A hct_mis_api.apps.core.celery beat -l INFO --scheduler hct_mis_api.apps.core.models:CustomDatabaseScheduler
        ;;
        "celery-worker")
            watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A hct_mis_api.apps.core.celery worker -E -l info -Q default,priority
        ;;
        *)
            exec "$@"
        ;;
    esac
fi
