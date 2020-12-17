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
        acl

ARG AIRFLOW_HOME=/usr/local/airflow
ENV AIRFLOW_HOME=${AIRFLOW_HOME}

RUN chown -R airflow: ${AIRFLOW_HOME}

ENV PATH="/usr/local/airflow/.local/bin:$PATH"

ENV POETRY_VERSION=1.1.4

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH = "${PATH}:/root/.poetry/bin"

ADD pyproject.toml poetry.lock /usr/local/airflow/
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi


ADD ./dags/. /usr/local/airflow/dags
ADD ./connectors/. /usr/local/airflow/connectors

COPY ./config/airflow.cfg /usr/local/airflow/airflow.cfg

COPY ./init_local_user.py /usr/local/airflow/init_local_user.py
