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

1. Install [pdm](https://github.com/pdm-project/pdm#installation)
2. $`pdm venv create`
3. Register the created venv for the project with `pdm use` 
4. Activate your venv (eg. $`$(pdm venv activate)`).
5. Check your environment
   eg. $`python --version` -> see that it uses Python 3.12.*
   eg. $`which python` -> see that it matches you python executable in the venv you have created: $```echo `pwd`/.venv/bin/python```
6. Install the package: $`pdm install`
7. Add `export PYTHONPATH="$PYTHONPATH:./src"`
8. Check your environment: $`./manage.py env --check` and configure the missing variables.
   You can generate a list for your development environment with the command `./manage.py env --develop --config --pattern='export {key}={value}'`
9. Once the environment has been set up run the initial migrations `./manage.py migrate`
10. Make sure to set up environment variables:
```
DATABASE_URL=postgres://postgres:username@localhost:5414/hope?options=-c%20search_path=django,public
ADMIN_EMAIL=<a valid email>
ADMIN_PASSWORD=<your admin password>
DATABASE_PORT=<only if different than default 5432>
SECRET_KEY=--
CATCH_ALL_EMAIL=<you catch all email>
SESSION_COOKIE_DOMAIN=localhost
```
11. Test using runserver $`./manage.py runserver` and logging in the admin `http://locslhost:8000/admin`


Configure environment for .direnv
---------------------------------

If yoy want to use [direnv](https://direnv.net/) and automatic loading of environment variables from a _.env_ file:
    
    ./manage.py env --develop --config --pattern='{key}={value}' > .env
    echo "dotenv" > .envrc
    echo 'export PYTHONPATH="$PYTHONPATH:./src"' >> .envrc
    echo 'eval $(pdm venv activate)' >> .envrc
    echo "unset PS1" >> .envrc

The first time after you have created or modified the _.envrc_ file you will have to authorize it using $`direnv allow`

NB: remember to configure your variables in the _.env_ file


Code quality
------------

To enhance readability of code and increase code standars we use the following  
- pep8 - https://peps.python.org/pep-0008/
- flake8 - https://flake8.pycqa.org/en/latest/
- isort - https://pycqa.github.io/isort/
- black - https://black.readthedocs.io/en/stable/
- mypy - https://mypy-lang.org/




