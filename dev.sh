#!/usr/bin/env bash
set -e
env |grep DATAB
pushd  src/frontend
yarn
echo "Starting Frontend DevServer"
yarn dev &               # Vite
PID_VITE=$!
popd
uv sync --no-install-package hope
echo "Starting Backend DevServer"
python manage.py runserver 127.0.0.1:8080 &  # Django
PID_DJANGO=$!
trap "kill $PID_VITE $PID_DJANGO" SIGINT
wait