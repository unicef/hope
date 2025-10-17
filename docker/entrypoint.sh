#!/bin/bash
set -e

if [ $# -eq 0 ]; then
    exec gunicorn hope.wsgi -c /conf/gunicorn_config.py
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
      celery -A hope.apps.core.celery beat -l INFO --scheduler hope.apps.core.models:CustomDatabaseScheduler
      ;;
    "celery-worker")
      watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A hope.apps.core.celery worker -E -l info --max-tasks-per-child=4 --concurrency=4
      ;;
    "celery-flower")
      celery -A hope.apps.core.celery flower --port=5555
      ;;
    *)
      exec "$@"
      ;;
  esac
fi
