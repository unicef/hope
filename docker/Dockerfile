FROM alpine:3.19.1 as curl
RUN apk add curl && mkdir /data

FROM curl as waitforit
RUN curl -o /data/waitforit -sSL https://github.com/maxcnunes/waitforit/releases/download/v2.4.1/waitforit-linux_amd64 \
    && chmod +x /data/waitforit

FROM curl as certs
RUN curl -o /data/psql-cert.crt -L https://dl.cacerts.digicert.com/DigiCertGlobalRootCA.crt.pem

# Base image
FROM python:3.11.7-slim-bookworm as base

ARG UID=82

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    postgresql-client \
    libpq-dev \
    python3-psycopg2 \
    python3-gdal \
    gdal-bin \
    libcairo2 \
    libcairo2-dev \
    libffi-dev \
    libgdk-pixbuf2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    shared-mime-info \
    wkhtmltopdf \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && addgroup --system --gid "${UID}" hope \
  && adduser --system --uid "${UID}" --disabled-password --home /home/hope --shell /sbin.nologin --group hope --gecos hope \
  && mkdir -p /code /tmp /data \
  && mkdir -p -m 0700 /run/user/"${UID}" \
  && chown -R hope:hope /code /tmp /data /run/user/"${UID}"

ENV PYTHONPYCACHEPREFIX=/tmp/pycache \
    VIRTUAL_ENV=/opt/venv \
    POETRY_HOME=/opt/poetry \
    PATH=/opt/venv/bin:/opt/poetry/bin:${PATH} \
    XDG_RUNTIME_DIR=/run/user/"${UID}"

WORKDIR /code

COPY --from=waitforit /data/waitforit /usr/local/bin/waitforit

# Dist builder image
FROM base as builder

RUN python3 -m venv --copies $VIRTUAL_ENV &&\
    python3 -m venv --copies $POETRY_HOME &&\
    $POETRY_HOME/bin/pip install lockfile==0.12.2 &&\
    $POETRY_HOME/bin/pip install poetry==1.3.0 &&\
    poetry config virtualenvs.create false &&\
    poetry config cache-dir /var/cache/poetry

COPY backend/pyproject.toml backend/poetry.lock ./
RUN poetry install --without dev

# Dev image
FROM builder AS dev

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    chromium-driver \
    chromium \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN poetry install
COPY ./backend ./

COPY ./docker/entrypoint.sh /bin/
ENTRYPOINT ["entrypoint.sh"]

## Dist (backend only) image
FROM base AS be-dist

COPY --chown=hope:hope ./backend ./
COPY --chown=hope:hope --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
COPY --chown=hope:hope --from=certs /data/psql-cert.crt /code/psql-cert.crt

USER hope

COPY ./docker/entrypoint.sh /bin/
ENTRYPOINT ["entrypoint.sh"]


# Frontend builder
FROM node:16.20.0-buster-slim as frontend-builder

WORKDIR /fe-build
RUN mkdir -p /backend/hct_mis_api/apps/web/templates/web
COPY ./frontend/package.json ./frontend/yarn.lock ./
# Network timeout is needed by the cross-platform build
RUN yarn install --frozen-lockfile --network-timeout 600000
COPY ./frontend ./
RUN NODE_ENV="production" yarn build


FROM be-dist AS dist

COPY --chown=hope:hope --from=frontend-builder /backend/hct_mis_api/apps/web/ ./hct_mis_api/apps/web/
