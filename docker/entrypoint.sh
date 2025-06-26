#!/bin/bash
set -e

if [ $# -eq 0 ]; then
    exec gunicorn hct_mis_api.wsgi -c /conf/gunicorn_config.py
else
  case "$1" in
    "dev")
      python manage.py collectstatic --no-input --no-default-ignore
      python manage.py migrate
      python manage.py runserver 0.0.0.0:8000
      ;;
    "cy")
      python manage.py collectstatic --no-input --no-default-ignore
      python manage.py migrate
      python manage.py initcypress --skip-drop
      python manage.py runserver 0.0.0.0:8000
      ;;
    "celery-beat")
      celery -A hct_mis_api.apps.core.celery beat -l INFO --scheduler hct_mis_api.apps.core.models:CustomDatabaseScheduler
      ;;
    "celery-worker")
      watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A hct_mis_api.apps.core.celery worker -E -l info -Q default --max-tasks-per-child=4 --concurrency=4
      ;;
    "celery-flower")
      celery -A hct_mis_api.apps.core.celery flower --port=5555
      ;;
    *)
      exec "$@"
      ;;
  esac
fi
