# Base image
FROM python:3.9.12-slim-bullseye as base

RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,target=/root/.cache,sharing=private \
  --mount=type=cache,target=/var/lib/apt,sharing=private \
  apt-get update &&\
  apt-get install -y --no-install-recommends \
  build-essential \
  libjpeg-dev \
  zlib1g-dev \
  postgresql-client \
  libpq-dev \
  python3-psycopg2 \
  python3-gdal \
  gdal-bin \
  curl \
  python3-dev \
  gcc \
  vim &&\
  addgroup --system --gid 82 hope &&\
  adduser --system --uid 82 --disabled-password --home /home/hope --shell /sbin.nologin --group hope --gecos hope &&\
  mkdir -p /code /tmp /data &&\
  chown -R hope:hope /code /tmp /data

ENV WAITFORIT_VERSION="v2.4.1" \
  PYTHONPYCACHEPREFIX=/tmp/pycache \
  VIRTUAL_ENV=/opt/venv \
  POETRY_HOME=/opt/poetry \
  PATH=/opt/venv/bin:/opt/poetry/bin:${PATH}

WORKDIR /code

RUN curl -o /usr/local/bin/waitforit -sSL https://github.com/maxcnunes/waitforit/releases/download/$WAITFORIT_VERSION/waitforit-linux_amd64 &&\
  chmod +x /usr/local/bin/waitforit

COPY ./docker-entrypoint.sh /bin/
ENTRYPOINT ["docker-entrypoint.sh"]

RUN curl -o /code/psql-cert.crt -L https://dl.cacerts.digicert.com/DigiCertGlobalRootCA.crt.pem

# Dist builder image
FROM base as builder

RUN python3 -m venv --copies $VIRTUAL_ENV &&\
  python3 -m venv --copies $POETRY_HOME &&\
  $POETRY_HOME/bin/pip install lockfile==0.12.2 &&\
  $POETRY_HOME/bin/pip install poetry==1.3.0 &&\
  poetry config virtualenvs.create false &&\
  poetry config cache-dir /var/cache/poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev
RUN mkdir test-coverage
CMD coverage xml -o ./test-coverage/coverage.xml

# Dev image
FROM builder AS dev

RUN poetry install
RUN mkdir test-coverage
CMD coverage xml -o ./test-coverage/coverage.xml
COPY ./ ./

# Dist image
FROM base AS dist

COPY --chown=hope:hope ./ ./
COPY --chown=hope:hope --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
USER hope
