# Base image
FROM python:3.12.7-slim-bookworm as base
ENV APP_PATH=/app
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
    screen \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && addgroup --system --gid "${UID}" hope \
  && adduser --system --uid "${UID}" --disabled-password --home /home/hope --shell /sbin.nologin --group hope --gecos hope \
  && mkdir -p $APP_PATH /tmp /data \
  && mkdir -p -m 0700 /run/user/"${UID}" \
  && chown -R hope:hope $APP_PATH /tmp /data /run/user/"${UID}"


ENV XDG_RUNTIME_DIR=/run/user/"${UID}"
ENV DJANGO_SETTINGS_MODULE=hct_mis_api.config.settings
WORKDIR $APP_PATH

# Dist builder image
FROM base as uv
RUN pip install --upgrade pip &&\
    pip install uv &&\
    pip install setuptools==71.1.0
COPY README.md LICENSE pyproject.toml uv.lock MANIFEST.in ./




# Dev image
FROM uv AS dev
ENV PYTHONPATH=$APP_PATH/src:$APP_PATH/test/:$PYTHONPATH
ENV PATH="$APP_PATH/.venv/bin:$PATH"
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
WORKDIR $APP_PATH
COPY ./src/ ./src/
RUN --mount=type=cache,target=/root/.uv-cache \
    uv sync --cache-dir=/root/.uv-cache \
        --python=/usr/local/bin/python \
        --python-preference=system \
        --no-editable --frozen --extra distribution --no-install-package hope
COPY ./tests ./tests
COPY ./src/data $APP_PATH/data
COPY ./manage.py ./manage.py
COPY .flake8 pyproject.toml uv.lock MANIFEST.in ./
COPY ./docker/entrypoint.sh /bin/
ENTRYPOINT ["entrypoint.sh"]


# Frontend builder
FROM node:20-buster-slim AS frontend-builder

WORKDIR /fe-build
COPY ./src/frontend/package.json ./src/frontend/yarn.lock ./
# Network timeout is needed by the cross-platform build
RUN yarn install --frozen-lockfile --network-timeout 600000
COPY ./src/frontend ./
RUN NODE_ENV="production" NODE_OPTIONS="--max-old-space-size=4096" yarn build

# Dist builder image
FROM uv as dist-builder
WORKDIR $APP_PATH
COPY ./src/ ./src/
COPY --chown=hope:hope --from=frontend-builder /fe-build/build $APP_PATH/src/hct_mis_api/apps/web/static/web
RUN uv sync --python=/usr/local/bin/python \
        --python-preference=system \
        --no-dev --no-editable --frozen


## Dist (backend only) image
FROM base AS dist
ENV PATH="$APP_PATH/.venv/bin:$PATH"

COPY ./src/gunicorn_config.py /conf/gunicorn_config.py
COPY --chown=hope:hope --from=dist-builder $APP_PATH/.venv $APP_PATH/.venv
COPY ./src/data $APP_PATH/data
USER hope

COPY ./docker/entrypoint.sh /bin/
ENTRYPOINT ["entrypoint.sh"]
