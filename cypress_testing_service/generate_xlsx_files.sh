#!/bin/bash

set -eu

docker-compose run --rm backend ./manage.py generate_rdi_xlsx_files $@

cp ../backend/generated/* cypress/fixtures/