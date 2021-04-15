#!/bin/bash
if (( $# != 1 )); then
    >&2 echo "Illegal number of arguments"
    exit 1
fi
cd backend
poetry version $1
cd ..
cd frontend
npm version $1