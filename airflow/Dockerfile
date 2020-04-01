FROM puckel/docker-airflow

USER root

RUN apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        git \
        libgraphviz-dev \
        python-gdal \
        gdal-bin \
        libgdal-dev \
        libgdal20 \
        graphviz

ENV PATH="/usr/local/airflow/.local/bin:$PATH"

COPY requirements.txt /usr/local/airflow/requirements.txt
RUN pip install -r requirements.txt

ARG AIRFLOW_HOME=/usr/local/airflow
ENV AIRFLOW_HOME=${AIRFLOW_HOME}

COPY ./config/airflow.cfg /usr/local/airflow/airflow.cfg
