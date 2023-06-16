#!/bin/bash
set -e

wait_for_db() {
  until pg_isready -h $1 -p 5432;
  do echo "waiting for database ${1}"; sleep 2; done;
}

if [ $# -eq 0 ]; then
    export NEW_RELIC_CONFIG_FILE=/code/newrelic.ini
    export NEW_RELIC_ENVIRONMENT=$ENV
    exec newrelic-admin run-program gunicorn hct_mis_api.wsgi -c /code/gunicorn_config.py
else
  case "$1" in
    "dev")
      wait_for_db db
      python manage.py collectstatic --no-input
      python manage.py migratealldb
      python manage.py runserver 0.0.0.0:8000
      ;;
    "cy")
      wait_for_db db
      python manage.py collectstatic --no-input
      python manage.py migratealldb
      python manage.py initcypress --skip-drop
      python manage.py runserver 0.0.0.0:8000
      ;;
    "test")
      export DEBUG=1
      export LOGGING_DISABLED=1
      export CACHE_ENABLED=0
      export ELASTICSEARCH_INDEX_PREFIX="test_"
      export EXCHANGE_RATE_CACHE_EXPIRY=0
      export CELERY_TASK_ALWAYS_EAGER=True
      export SESSION_COOKIE_SECURE=False
      export CSRF_COOKIE_SECURE=False
      export SECURE_HSTS_SECONDS=0
      export SOCIAL_AUTH_REDIRECT_IS_HTTPS=False
      export EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"
      wait_for_db db
      wait_for_db cash_assist_datahub_db
      wait_for_db mis_datahub_db
      wait_for_db erp_datahub_db
      wait_for_db registration_datahub_db
      python manage.py test --settings hct_mis_api.settings.test --noinput --parallel
      ;;
    "lint")
      mkdir -p ./lint-results
      flake8 --format=junit-xml . > ./lint-results/flake8.xml
      ;;
    "mypy")
      mkdir -p ./mypy-results
      mypy --junit-xml ./mypy-results/mypy.xml .
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
