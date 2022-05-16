#!/bin/bash
set -e
until pg_isready -h db -p 5432;
  do echo "waiting for database"; sleep 2; done;
until pg_isready -h cash_assist_datahub_db -p 5432;
  do echo "waiting for database"; sleep 2; done;
until pg_isready -h mis_datahub_db -p 5432;
  do echo "waiting for database"; sleep 2; done;
until pg_isready -h erp_datahub_db -p 5432;
  do echo "waiting for database"; sleep 2; done;
until pg_isready -h registration_datahub_db -p 5432;
  do echo "waiting for database"; sleep 2; done;
python manage.py test  --settings hct_mis_api.settings.test --noinput --parallel

