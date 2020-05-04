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

COPY requirements.txt /usr/local/airflow/requirements.txt
RUN pip install -r requirements.txt

ADD ../backend/. /usr/local/airflow/backend

COPY ./config/airflow.cfg /usr/local/airflow/airflow.cfg
