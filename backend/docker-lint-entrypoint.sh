#!/bin/bash
set -e

mkdir -p ./lint-results

flake8 --format=junit-xml . > ./lint-results/flake8.xml