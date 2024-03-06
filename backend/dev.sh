#!/bin/bash
set -e

wait_for_db() {
  until pg_isready -h $1 -p 5432;
  do echo "waiting for database ${1}"; sleep 2; done;
}

if [ $# -eq 0 ]; then
  echo "No arguments supplied"
  exit 1
else
  case "$1" in
    "test")
      wait_for_db db
      # pytest hct_mis_api -n logical
      coverage run --parallel-mode ./manage.py test --settings hct_mis_api.settings_test --noinput --parallel -v3
      coverage combine
      coverage xml
      ;;
    "lint")
      mkdir -p ./lint-results
      flake8 --format=junit-xml . > ./lint-results/flake8.xml
      ;;
    "mypy")
      mkdir -p ./mypy-results
      mypy --junit-xml ./mypy-results/mypy.xml .
      ;;
    *)
      exec "$@"
      ;;
  esac
fi
