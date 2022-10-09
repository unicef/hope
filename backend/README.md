# Development

## VSCode setup

```sh
python3.9 -m venv venv
docker-compose build
docker-compose run --rm backend poetry export -f requirements.txt --output venv/requirements.txt
python3.9 -m pip install -r venv/requirements.txt --require-hashes
```

CMD + Shift + P => `Python: Select interpreter`
Provide path to `./backend/venv/bin/python3`

Oneliner to refresh your packages (from `backend` dir):

```sh
sh -c ". ./venv/bin/activate ; docker-compose run --rm backend poetry export -f requirements.txt --output venv/requirements.txt ; python3.9 -m pip install -r venv/requirements.txt --require-hashes"
```

## Testing

To run tests, you call `./manage.py test`. Example invocation:

```shell
docker-compose run --rm backend python3 manage.py test -v3 --keepdb --settings hct_mis_api.settings.test --parallel
```

## Linting

To run linting, you use `flake8`. Example invocation:

```shell
docker-compose run --rm backend flake8 .
```

## Formatting

To run formatting, you use `black`. Example invocation:

```shell
docker-compose run --rm backend black .
```

## Isort

To run isort, you use `isort`. Example invocation:

```shell
docker-compose run --rm backend isort .
```
