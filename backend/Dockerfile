FROM python:3.7.3-alpine3.9

RUN apk add --upgrade --no-cache "postgresql-client" "postgresql-contrib" "postgresql-dev" bash curl
RUN apk add --upgrade --no-cache g++ linux-headers gcc make libffi-dev git wget jpeg-dev zlib-dev libpng-dev

RUN pip install --upgrade pip

ADD ./requirements/* /tmp/
WORKDIR /tmp

RUN pip install -r base.pip

ADD . /code/

WORKDIR /code/

EXPOSE 8000

ADD ./docker-entrypoint.sh /bin/
ENTRYPOINT ["docker-entrypoint.sh"]
