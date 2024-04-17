#!/bin/bash
set -e

old_version=$(cd backend && pdm show --version)
(cd backend && sed -i "s/version = \"$old_version\"/version = \"$1\"/" pyproject.toml)
(cd frontend && npm version $1)


current_version=$(cd backend && pdm show --version)

echo "Bumping version from $old_version to $current_version"

git add -A

git commit -m "Bump version $current_version"
git tag "$current_version"
git push origin "$current_version"
git push

echo "New version $current_version pushed to origin"

current_branch=$(git branch --show-current)
if [[ "$current_branch" == "develop" ]]; then
    gh pr create -a "@me" -t "Staging $current_version" --base staging -b ''
fi
