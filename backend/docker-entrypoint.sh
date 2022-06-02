#!/bin/bash
set -e

if [ $# -eq 0 ]; then
    echo 'Jan starts'
    export NEW_RELIC_CONFIG_FILE=/code/newrelic.ini
#    exec newrelic-admin run-program gunicorn hct_mis_api.wsgi -c /code/gunicorn_config.py
    python manage.py runserver 0.0.0.0:8000
else
    case "$1" in
        "dev")
        until pg_isready -h db -p 5432;
          do echo "waiting for database"; sleep 2; done;
        python manage.py collectstatic --no-input
        python manage.py migratealldb
        python manage.py runserver 0.0.0.0:8000

        ;;
    *)
    exec "$@"
    ;;
    esac
fi
