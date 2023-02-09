#!/bin/bash

set -e

case "$1" in
    "test")
        echo "Waiting for backend to be ready"
        waitforit -host=backend -port=8000 --timeout 300
        echo "Waiting for frontend to be ready"
        waitforit -host=frontend -port=80 --timeout 300
        echo "Waiting for proxy to be ready"
        waitforit -host=proxy -port=80 --timeout 300

        yarn cypress run --headless \
            --config baseUrl=http://proxy \
            --reporter junit \
            --reporter-options "mochaFile=cypress/results/results-[hash].xml,toConsole=true"
        ;;
    *)
        exec "$@"
        ;;
esac
