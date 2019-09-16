#!/usr/bin/env bash
/usr/local/bin/wait-for-it.sh db:5432 -t 30 && python /code/manage.py collectstatic --noinput && python /code/manage.py migrate --noinput && gunicorn hct_mis_api.wsgi -c /code/gunicorn_config.py
