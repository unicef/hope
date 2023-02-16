FROM python:3.9.12-slim-bullseye

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

ARG APP_ENV=prod
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.2.0 python -
ENV PATH = "${PATH}:/root/.local/bin/"
COPY pyproject.toml poetry.lock /tmp/
RUN --mount=type=cache,target=/root/.cache,sharing=private \
    poetry config virtualenvs.create false \
    && poetry install $(test "$APP_ENV" == prod && echo "--no-dev")  --no-interaction --no-ansi

ENV WAITFORIT_VERSION="v2.4.1"
RUN curl -o /usr/local/bin/waitforit -sSL https://github.com/maxcnunes/waitforit/releases/download/$WAITFORIT_VERSION/waitforit-linux_amd64 && \
  chmod +x /usr/local/bin/waitforit

COPY . /code/

WORKDIR /code/

EXPOSE 8000

RUN curl -o /code/psql-cert.crt -L https://dl.cacerts.digicert.com/DigiCertGlobalRootCA.crt.pem

COPY ./docker-entrypoint.sh /bin/
ENTRYPOINT ["docker-entrypoint.sh"]
