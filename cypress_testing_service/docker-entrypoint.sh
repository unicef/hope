#!/bin/bash

cypress_run_local () {
  echo "Waiting for frontend" && wait-on http://frontend:3000/
  echo "Waiting for backend" && wait-on http://backend:8000/api/_health

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