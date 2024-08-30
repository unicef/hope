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
    python3-dev \
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
ENV PDM_NO_SELF=True
ENV PDM_PROJECT=$PDM_PACKAGES
ENV PYPACKAGES=$PDM_PACKAGES/__pypackages__/3.11
ENV PYTHONPYCACHEPREFIX=/tmp/pycache \
    PYTHONPATH=$PYPACKAGES/lib:$CODE:$PYTHONPATH \
    PATH=$PYPACKAGES/bin:$PATH \
    XDG_RUNTIME_DIR=/run/user/"${UID}"

WORKDIR $CODE

COPY --from=waitforit /data/waitforit /usr/local/bin/waitforit

# Dist builder image
FROM base as builder

RUN pip install --upgrade pip &&\
    pip install pdm==2.15.2 &&\
    pip install setuptools==71.1.0 &&\
    pdm config cache_dir /var/cache/pdm &&\
    pdm config python.use_venv false &&\
    pdm config venv.in_project true &&\
    pdm config check_update false

WORKDIR $PDM_PACKAGES
COPY backend/pyproject.toml backend/pdm.lock ./
RUN pdm sync --prod --no-editable --no-self --no-isolation

# Dev image
FROM builder AS dev

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ffmpeg \
    xorg \
    x11-apps \
    dbus \
    wget \
    unzip \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# RUN wget https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.63/linux64/chrome-linux64.zip
# RUN unzip ./chrome-linux64.zip -d ~/
# RUN mv ~/chrome-linux64 ~/chrome
# RUN ln -s ~/chrome/chrome /usr/local/bin/chrome
# RUN chmod +x ~/chrome
# RUN rm ./chrome-linux64.zip

# Pobieramy i instalujemy Chrome w wersji 120
# RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_arm64.deb
# RUN dpkg -i google-chrome-stable_current_arm64.deb
# RUN apt-get -fy install
# RUN rm google-chrome-stable_current_amd64.deb
# RUN chrome --version

# Pobieramy i instalujemy ChromeDriver kompatybilny z wersją Chrome 120
# RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') && \
#     wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROME_VERSION/chromedriver_linux64.zip" && \
#     unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
#     rm /tmp/chromedriver.zip

RUN pdm sync --no-editable --no-self --no-isolation

WORKDIR $CODE
COPY ./backend ./

COPY ./docker/entrypoint.sh /bin/
ENTRYPOINT ["entrypoint.sh"]

## Dist (backend only) image
FROM base AS be-dist

COPY --chown=hope:hope ./backend ./
COPY --chown=hope:hope --from=builder $PDM_PACKAGES $PDM_PACKAGES
COPY --chown=hope:hope --from=certs /data/psql-cert.crt /code/psql-cert.crt

USER hope

COPY ./docker/entrypoint.sh /bin/
ENTRYPOINT ["entrypoint.sh"]


# Frontend builder
FROM node:18.19.0-buster-slim AS frontend-builder

WORKDIR /fe-build
COPY ./frontend/package.json ./frontend/yarn.lock ./
# Network timeout is needed by the cross-platform build
RUN yarn install --frozen-lockfile --network-timeout 600000
COPY ./frontend ./
RUN NODE_ENV="production" NODE_OPTIONS="--max-old-space-size=4096" yarn build


FROM be-dist AS dist

COPY --chown=hope:hope --from=frontend-builder /fe-build/build ./hct_mis_api/apps/web/static/web
