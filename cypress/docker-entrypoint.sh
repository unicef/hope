#!/bin/bash

set -e

wait_for_stuff() {
    echo "Waiting for backend to be ready"
    waitforit -host=backend -port=8000 --timeout 300
    echo "Waiting for frontend to be ready"
    waitforit -host=frontend -port=80 --timeout 300
    echo "Waiting for proxy to be ready"
    waitforit -host=proxy -port=80 --timeout 300
    echo "Staring cypress tests..."
}

case "$1" in
    "ci-test-sequential")
        wait_for_stuff
        exec npm run sequential || npm run posttest
        ;;
    "ci-test-parallel")
        wait_for_stuff
        exec npm run parallel || npm run posttest
        ;;
    *)
        exec "$@"
        ;;
esac
