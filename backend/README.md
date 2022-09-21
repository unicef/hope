# Development

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
