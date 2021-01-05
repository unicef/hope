FROM puckel/docker-airflow

USER root

RUN apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        git \
        gcc \
        libgraphviz-dev \
        python-gdal \
        gdal-bin \
        libgdal-dev \
        libgdal20 \
        graphviz \
        acl \
        wget

ARG AIRFLOW_HOME=/usr/local/airflow
ENV AIRFLOW_HOME=${AIRFLOW_HOME}

RUN chown -R airflow: ${AIRFLOW_HOME}

ENV PATH="/usr/local/airflow/.local/bin:$PATH"

ENV POETRY_VERSION=1.1.4

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH = "${PATH}:/root/.poetry/bin"

ADD ./airflow/pyproject.toml ./airflow/poetry.lock /usr/local/airflow/
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

RUN mkdir /code

RUN wget -O /code/psql-cert.crt https://www.digicert.com/CACerts/BaltimoreCyberTrustRoot.crt.pem

ADD ./backend/. /usr/local/airflow/backend
ADD ./airflow/dags/. /usr/local/airflow/dags
ADD ./airflow/connectors/. /usr/local/airflow/connectors

COPY ./airflow/config/airflow.cfg /usr/local/airflow/airflow.cfg
