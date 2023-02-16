#!/bin/bash

set -e

case "$1" in
    "ci-test")
        echo "Waiting for backend to be ready"
        waitforit -host=backend -port=8000 --timeout 300
        echo "Waiting for frontend to be ready"
        waitforit -host=frontend -port=80 --timeout 300
        echo "Waiting for proxy to be ready"
        waitforit -host=proxy -port=80 --timeout 300
        echo "Staring cypress tests..."
        exec yarn cypress run --headless --config \
          baseUrl=http://proxy,video=false \
          --reporter junit --reporter-options \
          "mochaFile=/code/cypress/results/results-[hash].xml,toConsole=true"
        ;;
    *)
        exec "$@"
        ;;
esac
