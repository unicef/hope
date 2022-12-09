#!/bin/bash
set -e

mkdir -p ./mypy-results

mypy --junit-xml ./mypy-results/mypy.xml .
