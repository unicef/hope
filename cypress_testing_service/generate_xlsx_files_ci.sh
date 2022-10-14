#!/bin/bash

set -eu

curl -X POST http://proxy/api/cypress-xlsx/$1

cp /backend_generated/* cypress/fixtures/