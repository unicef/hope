#!/bin/bash
set -e

if [ $# -eq 0 ]; then
    exec gunicorn hct_mis_api.wsgi -c /code/gunicorn_config.py
else
    case "$1" in
        "dev")
        until pg_isready -h db -p 5432;
          do echo "waiting for database"; sleep 2; done;
        until pg_isready -h $POSTGRES_CASHASSIST_DATAHUB_HOST -p 5432;
          do echo "waiting for database"; sleep 2; done;
        until pg_isready -h $POSTGRES_REGISTRATION_DATAHUB_HOST -p 5432;
          do echo "waiting for database"; sleep 2; done;
        sh ./create_schemas.sh
        python manage.py collectstatic --no-input
        python manage.py migratealldb
        python manage.py runserver 0.0.0.0:8000

        ;;
    *)
    exec "$@"
    ;;
    esac
fi
