FROM python:3.9.12-slim-bullseye

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  build-essential \
  libjpeg-dev \
  zlib1g-dev \
  git-core \
  postgresql-client \
  libpq-dev \
  python3-psycopg2 \
  python3-gdal \
  gdal-bin \
  curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

ARG APP_ENV=prod
ENV POETRY_VERSION=1.1.4
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH = "${PATH}:/root/.poetry/bin"

ADD pyproject.toml poetry.lock /tmp/
RUN poetry config virtualenvs.create false \
  && poetry install $(test "$APP_ENV" == prod && echo "--no-dev")  --no-interaction --no-ansi

ENV WAITFORIT_VERSION="v2.4.1"
RUN curl -o /usr/local/bin/waitforit -sSL https://github.com/maxcnunes/waitforit/releases/download/$WAITFORIT_VERSION/waitforit-linux_amd64 && \
  chmod +x /usr/local/bin/waitforit

ADD . /code/

WORKDIR /code/

EXPOSE 8000

RUN curl -o /code/psql-cert.crt -L https://cacerts.digicert.com/BaltimoreCyberTrustRoot.crt.pem

ADD ./docker-entrypoint.sh /bin/
ENTRYPOINT ["docker-entrypoint.sh"]