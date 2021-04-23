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
cd ..
git add -A
VERSION=$(./get_version.py)
git commit -m "Bump version $VERSION"
git tag $VERSION
git push origin --tags
