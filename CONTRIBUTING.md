Setup development environment
=============================

Prerequisites:
- This project uses PDM as package manager (see https://github.com/pdm-project/pdm).
- A Postgres DB v15+
- A Redis server
- An Elastic Search server


Technology Stack
================

- Python
- Django
- Django REST Framework
- GraphQL
- Postgres
- Celery
- Redis
- ElasticSearch
- Kubernates


To start developing:
====================

Pull Requests
-------------

Every pull requests should contain tests to coverage the functionality.
- Coverage of 95% on written lines is required in order to merge.
- Two reviews are needed before merging PRs


Get started
-----------

1. Install [uv](https://docs.astral.sh/)
2. $`uv create venv --python 3.13`
3. You may want to use direnv and configure your .envrc
4. Activate your venv (eg. $`$( source .venv/bin/activate)`).
5. Check your environment
   eg. $`python --version` -> see that it uses Python 3.13.*
   eg. $`which python` -> see that it matches you python executable in the venv you have created: $```echo `pwd`/.venv/bin/python```
5. Install the package: $`uv sync`
6. Add `export PYTHONPATH="$PYTHONPATH:./src"`
7. Check your environment: $`./manage.py env --check` and configure the missing variables.
   You can generate a list for your development environment with the command `./manage.py env --develop --config --pattern='export {key}={value}'`
8. Once the environment has been set up run the initial migrations `./manage.py migrate`
9. Make sure to set up environment variables:
```
DATABASE_URL=postgres://postgres:username@localhost:5414/hope?options=-c%20search_path=django,public
ADMIN_EMAIL=<a valid email>
ADMIN_PASSWORD=<your admin password>
DATABASE_PORT=<only if different than default 5432>
SECRET_KEY=--
CATCH_ALL_EMAIL=<you catch all email>
SESSION_COOKIE_DOMAIN=localhost
```
10. Test using runserver $`./manage.py runserver` and logging in the admin `http://locslhost:8000/admin`


Configure environment for .direnv
---------------------------------

If yoy want to use [direnv](https://direnv.net/) and automatic loading of environment variables from a _.env_ file:

    ./manage.py env --develop --config --pattern='{key}={value}' > .env
    echo "dotenv" > .envrc
    echo 'export PYTHONPATH="$PYTHONPATH:./src"' >> .envrc
    echo 'eval $(source .venv/bin/activate)' >> .envrc
    echo "unset PS1" >> .envrc

The first time after you have created or modified the _.envrc_ file you will have to authorize it using $`direnv allow`

NB: remember to configure your variables in the _.env_ file


Code quality
------------

To enhance readability of code and increase code standards we use the following
- ruff - https://docs.astral.sh/ruff/
