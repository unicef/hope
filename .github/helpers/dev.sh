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
      pytest \
        -n auto \
        --reruns 3 \
        --reruns-delay 1 \
        --cov-report xml:test-coverage/coverage.xml \
        --randomly-seed=42 \
        --create-db \
        ./tests/unit/
      ;;
    "lint")
      mkdir -p ./lint-results
      tox -e lint
      ;;
    *)
      exec "$@"
      ;;
  esac
fi
