FROM python:3.9.1-slim-buster


RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    git-core \
    postgresql-client \
    libpq-dev \
    python-psycopg2 \
    python-gdal \
    gdal-bin \
    curl
RUN apt-get clean
WORKDIR /tmp

ARG APP_ENV=prod
ENV POETRY_VERSION=1.1.4
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH = "${PATH}:/root/.poetry/bin"

ADD pyproject.toml poetry.lock /tmp/
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$APP_ENV" == prod && echo "--no-dev")  --no-interaction --no-ansi

ADD . /code/

WORKDIR /code/

EXPOSE 8000

RUN curl -o /code/psql-cert.crt -L https://cacerts.digicert.com/BaltimoreCyberTrustRoot.crt.pem

ADD ./docker-entrypoint.sh /bin/
ENTRYPOINT ["docker-entrypoint.sh"]
