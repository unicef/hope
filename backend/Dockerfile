FROM python:3.7.3-alpine3.9

ARG env
ENV ENV ${env:-dev}

ARG requirement_file
ENV REQUIREMENT_FILE ${requirement_file:-dev.pip}

ARG GIT_VERSION
ENV GIT_VERSION ${GIT_VERSION:-UNKNOWN}

RUN apk update
RUN apk add --upgrade --no-cache "postgresql-client" "postgresql-contrib" "postgresql-dev" bash curl
RUN apk add --upgrade --no-cache g++ linux-headers gcc make libffi-dev git wget jpeg-dev zlib-dev libpng-dev graphviz-dev

# Install Python tools
RUN pip install --upgrade \
    virtualenv \
    fabric \
    wheel \
    --trusted-host pypi.python.org

# http://gis.stackexchange.com/a/74060
ENV CPLUS_INCLUDE_PATH /usr/include/gdal
ENV C_INCLUDE_PATH /usr/include/gdal

ADD ./requirements/* /tmp/

# Install PyPi dependencies
WORKDIR /tmp
RUN pip install --upgrade pip && pip install -r $REQUIREMENT_FILE --trusted-host pypi.python.org

ADD . /code/

RUN mkdir -p /data/staticserve
RUN mkdir -p /data/uploads

RUN chmod -R a+rw /data

ADD worker-entrypoint.sh /
RUN chmod +x /worker-entrypoint.sh

ADD entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENV PYTHONUNBUFFERED 1
WORKDIR /code/

COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

EXPOSE 8000

CMD /./entrypoint.sh
