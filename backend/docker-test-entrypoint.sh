#!/bin/bash
set -e
until pg_isready -h db -p 5432;
  do echo "waiting for database"; sleep 1; done;
until pg_isready -h $POSTGRES_CASHASSIST_DATAHUB_HOST -p 5432;
  do echo "waiting for database"; sleep 1; done;
until pg_isready -h $POSTGRES_REGISTRATION_DATAHUB_HOST -p 5432;
  do echo "waiting for database"; sleep 1; done;
python manage.py test  --settings hct_mis_api.settings.test

