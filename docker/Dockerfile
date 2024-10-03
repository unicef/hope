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

ENV PDM_PACKAGES=/packages
ENV CODE=/code
ENV PDM_PROJECT=$PDM_PACKAGES
ENV PYPACKAGES=$PDM_PACKAGES/__pypackages__/3.11
ENV PYTHONPYCACHEPREFIX=/tmp/pycache \
    PYTHONPATH=$PYPACKAGES/lib:$PYTHONPATH \
    PATH=$PYPACKAGES/bin:$PATH \
    XDG_RUNTIME_DIR=/run/user/"${UID}"

WORKDIR $CODE

COPY --from=waitforit /data/waitforit /usr/local/bin/waitforit

# Dist builder image
FROM base as pdm
RUN pip install --upgrade pip &&\
    pip install pdm==2.15.2 &&\
    pip install setuptools==71.1.0 &&\
    pdm config cache_dir /var/cache/pdm &&\
    pdm config python.use_venv false &&\
    pdm config venv.in_project true &&\
    pdm config check_update false
WORKDIR $PDM_PACKAGES
COPY README.md LICENSE pyproject.toml pdm.lock ./




# Dev image
FROM pdm AS dev

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    python3-dev \
    chromium-driver \
    chromium \
    ffmpeg \
    xorg \
    x11-apps \
    dbus \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=$CODE/src:$CODE/test/:$PYTHONPATH
RUN pdm sync --no-editable --no-self --no-isolation

WORKDIR $CODE
COPY ./src/ ./src/
COPY ./tests ./tests
COPY ./manage.py ./manage.py
COPY .flake8 pyproject.toml pdm.lock ./
COPY ./docker/entrypoint.sh /bin/
ENTRYPOINT ["entrypoint.sh"]


# Frontend builder
FROM node:18.19.0-buster-slim AS frontend-builder

WORKDIR /fe-build
COPY ./src/frontend/package.json ./src/frontend/yarn.lock ./
# Network timeout is needed by the cross-platform build
RUN yarn install --frozen-lockfile --network-timeout 600000
COPY ./src/frontend ./
RUN NODE_ENV="production" NODE_OPTIONS="--max-old-space-size=4096" yarn build

# Dist builder image
FROM pdm as dist-builder
COPY ./src/ ./src/
COPY --chown=hope:hope --from=frontend-builder /fe-build/build $PDM_PACKAGES/src/hct_mis_api/apps/web/static/web
RUN pdm sync --prod --no-editable --no-isolation


## Dist (backend only) image
FROM base AS dist


COPY ./src/gunicorn_config.py /conf/gunicorn_config.py
COPY --chown=hope:hope --from=dist-builder $PDM_PACKAGES $PDM_PACKAGES
COPY --chown=hope:hope --from=certs /data/psql-cert.crt /certs/psql-cert.crt

USER hope

COPY ./docker/entrypoint.sh /bin/
ENTRYPOINT ["entrypoint.sh"]
