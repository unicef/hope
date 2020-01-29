FROM python:3.7.3

RUN apt-get update && \
    # fix certificates for easy_install "certificate verify failed"
    apt-get install --assume-yes --reinstall ca-certificates
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
    ntp
RUN apt-get install -y --no-install-recommends \
    git-core
RUN apt-get install -y --no-install-recommends \
    python-dev \
    python-setuptools
RUN apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    python-psycopg2
RUN apt-get install -y --no-install-recommends \
    python-gdal \
    gdal-bin \
    libgdal-dev \
    libgdal20
RUN pip install --upgrade pip

ADD ./requirements/* /tmp/

WORKDIR /tmp

RUN pip install -r base.pip

ADD . /code/

WORKDIR /code/

EXPOSE 8000

ADD ./docker-entrypoint.sh /bin/
ENTRYPOINT ["docker-entrypoint.sh"]
