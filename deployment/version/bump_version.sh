#!/bin/bash
set -e
if (( $# != 1 )); then
    >&2 echo "Illegal number of arguments"
    exit 1
fi
cd backend
poetry version $1 > /dev/null
cd ..
cd frontend
npm version $1 > /dev/null
cd ..
git add -A &> /dev/null
VERSION=$(./get_version.py)
git commit -m "Bump version $VERSION" &> /dev/null
git tag $VERSION &> /dev/null
git push origin --tags &> /dev/null
git push origin &> /dev/null
echo "New version $VERSION pushed to origin"