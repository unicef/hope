#!/bin/bash
set -e
until pg_isready -h db -p 5432;
  do echo "waiting for database"; sleep 2; done;
until pg_isready -h $POSTGRES_CASHASSIST_DATAHUB_HOST -p 5432;
  do echo "waiting for database"; sleep 2; done;
until pg_isready -h $POSTGRES_REGISTRATION_DATAHUB_HOST -p 5432;
  do echo "waiting for database"; sleep 2; done;
sh ./create_schemas.sh
python manage.py test  --settings hct_mis_api.settings.test

