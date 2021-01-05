FROM python:3.7.3

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    build-essential \
    libcurl4-openssl-dev \
    libjpeg-dev \
    libgif-dev \
    libffi-dev \
    libpng-dev \
    libtiff-dev \
    libxml2-dev \
    libxslt-dev \
    xmlsec1 \
    vim \
    ntp \
    git-core \
    python-dev \
    python-setuptools \
    postgresql-client \
    libpq-dev \
    python-psycopg2 \
    python-gdal \
    gdal-bin \
    libgdal-dev \
    libgdal20

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

RUN wget -O /code/psql-cert.crt https://www.digicert.com/CACerts/BaltimoreCyberTrustRoot.crt.pem

ADD ./docker-entrypoint.sh /bin/
ENTRYPOINT ["docker-entrypoint.sh"]
