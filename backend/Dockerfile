FROM python:3.9.12-slim-bullseye as base

RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,target=/root/.cache,sharing=private \
  --mount=type=cache,target=/var/lib/apt,sharing=private \
  apt-get update && \
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
  vim

WORKDIR /tmp

ENV WAITFORIT_VERSION="v2.4.1"
RUN curl -o /usr/local/bin/waitforit -sSL https://github.com/maxcnunes/waitforit/releases/download/$WAITFORIT_VERSION/waitforit-linux_amd64 && \
  chmod +x /usr/local/bin/waitforit

COPY ./docker-entrypoint.sh /bin/
ENTRYPOINT ["docker-entrypoint.sh"]

FROM base AS builder

ENV PATH = "${PATH}:/root/.local/bin/"
COPY pyproject.toml poetry.lock /tmp/

WORKDIR /code/
COPY . /code/

EXPOSE 8000
RUN curl -o /code/psql-cert.crt -L https://dl.cacerts.digicert.com/DigiCertGlobalRootCA.crt.pem

FROM builder as dev

RUN --mount=type=cache,target=/root/.cache,sharing=private \
  (curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.2.0 python -) \
  && poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

FROM builder as dist

RUN --mount=type=cache,target=/root/.cache,sharing=private \
  (curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.2.0 python -) \
  && poetry config virtualenvs.create false \
  && poetry install --without dev --no-interaction --no-ansi \
  && (curl -sSL https://install.python-poetry.org | POETRY_UNINSTALL=1 python -) \
  && rm -rf \
  /root/.local \
  /root/.config