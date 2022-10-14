#!/bin/bash

cypress_run_local () {
  # Timeout in milliseconds ( 10 min == 10 * 60 * 1000)
  echo "Waiting for frontend" && wait-on http://proxy/ -t 600000 -i 1000
  echo "Waiting for backend" && wait-on http://proxy/api/_health -t 600000 -i 1000
  yarn cypress run
}

if [ ${#} -eq 0 ]; then
  echo "Running local mode..."
  cypress_run_local
else
  if [ $1 == "ci" ]; then
  	echo "Runing in CI mode..."
    # TODO
  fi
fi