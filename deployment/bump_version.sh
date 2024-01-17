#!/bin/bash
set -e

get_normal_new_version() {
    version_string=$1
    version_regex="([0-9]+).([0-9]+).([0-9]+).*"
    [[ $version_string =~ $version_regex ]]
    old_year=${BASH_REMATCH[1]}
    old_month=${BASH_REMATCH[2]}
    old_minor=${BASH_REMATCH[3]}

    current_year=$(date +'%Y')
    current_month=$(date +'%-m')

    if [ "$old_year" == "$current_year" ] && [ "$current_month" == "$old_month" ]; then
        current_minor=$((old_minor + 1))
    else
        current_minor=1
    fi

    echo "${current_year}.${current_month}.${current_minor}"
}

old_version=$(cd backend && poetry version --short)
new_version=$(get_normal_new_version "$old_version")

(cd backend && poetry version "$new_version")
(cd frontend && npm version "$new_version")

git add -A

current_version=$(cd backend && poetry version --short)
git commit -m "Bump version $current_version"
git tag "$current_version"
git push --tags
git push

echo "New version $current_version pushed to origin"

current_branch=$(git branch --show-current)
if [[ "$current_branch" == "develop" ]]; then
    gh pr create -a "@me" -t "Staging $current_version" --base staging -b ''
fi
