# Runtime base — minimal libs needed at prod runtime (weasyprint/cairo/pango/gdk-pixbuf)
FROM python:3.14-slim-trixie AS base-runtime
ENV APP_PATH=/app
ARG UID=82

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    fonts-dejavu-core \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && addgroup --system --gid "${UID}" hope \
  && adduser --system --uid "${UID}" --disabled-password --home /home/hope --shell /sbin/nologin --group hope --gecos hope \
  && mkdir -p $APP_PATH /tmp /data \
  && mkdir -p -m 0700 /run/user/"${UID}" \
  && chown -R hope:hope $APP_PATH /tmp /data /run/user/"${UID}"

ENV XDG_RUNTIME_DIR=/run/user/"${UID}"
ENV DJANGO_SETTINGS_MODULE=hope.config.settings
WORKDIR $APP_PATH


# Build base — adds compiler toolchain + dev headers. Used by uv/dist-builder/dev only.
FROM base-runtime AS base-build
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libjpeg-dev \
    zlib1g-dev \
    libcairo2-dev \
    libffi-dev \
    python3-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*


# uv installer stage
FROM base-build AS uv
RUN pip install --upgrade pip && pip install uv
COPY README.md LICENSE pyproject.toml uv.lock MANIFEST.in ./


# Dev image — selenium/e2e deps on top of uv
FROM uv AS dev
ENV PYTHONPATH=$APP_PATH/src:$APP_PATH/tests/:$PYTHONPATH
ENV PATH="$APP_PATH/.venv/bin:$PATH"
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
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
        --no-editable --frozen --group dev --no-install-package hope
COPY ./tests ./tests
COPY ./src/data $APP_PATH/data
COPY ./manage.py ./manage.py
COPY pyproject.toml uv.lock ruff.toml mypy.ini tox.ini MANIFEST.in ./
COPY ./docker/entrypoint.sh /bin/
ENTRYPOINT ["entrypoint.sh"]


# Frontend builder
FROM oven/bun:1.3-slim AS frontend-builder
WORKDIR /fe-build
COPY ./src/frontend/package.json ./src/frontend/bun.lock ./
RUN bun install --frozen-lockfile
COPY ./src/frontend ./
RUN NODE_ENV="production" bun run build


# Dist builder — builds the production venv
FROM uv AS dist-builder
WORKDIR $APP_PATH
COPY ./src/ ./src/
COPY --chown=hope:hope --from=frontend-builder /fe-build/build $APP_PATH/src/hope/apps/web/static/web
RUN uv sync --python=/usr/local/bin/python \
        --python-preference=system \
        --no-editable --frozen


# Dist — final production image. FROM base-runtime, not base-build, so no toolchain leaks in.
FROM base-runtime AS dist
ARG BUILD_DATE
ARG SOURCE_COMMIT
ARG BRANCH
ARG VERSION
ENV VERSION=$VERSION \
    BUILD_DATE=$BUILD_DATE \
    SOURCE_COMMIT=$SOURCE_COMMIT \
    PATH="$APP_PATH/.venv/bin:$PATH"

RUN printf '{"version": "%s", "commit": "%s", "date": "%s", "branch": "%s"}\n' \
    "$VERSION" "$SOURCE_COMMIT" "$BUILD_DATE" "$BRANCH" > /RELEASE

COPY ./src/gunicorn_config.py /conf/gunicorn_config.py
COPY --chown=hope:hope --from=dist-builder $APP_PATH/.venv $APP_PATH/.venv
COPY ./src/data $APP_PATH/data
USER hope

COPY ./docker/entrypoint.sh /bin/
ENTRYPOINT ["entrypoint.sh"]
