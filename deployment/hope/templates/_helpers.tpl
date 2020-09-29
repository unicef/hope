{{/*
Expand the name of the chart.
*/}}
{{- define "hope.name" -}}
{{- default .Chart.Name .Values.global.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "hope.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.global.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "hope.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "hope.labels" -}}
helm.sh/chart: {{ include "hope.chart" . }}
{{ include "hope.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "hope.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hope.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "hope.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "hope.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

Create a default fully qualified postgresql name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "hope.postgresql.fullname" -}}
{{- $name := default "postgresql" .Values.postgresql.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

Create a default fully qualified registrationdatahubpostgresql name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "hope.registrationdatahubpostgresql.fullname" -}}
{{- $name := default "registrationdatahubpostgresql" .Values.registrationdatahubpostgresql.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

Create a default fully qualified cashassistdatahubpostgresql name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "hope.cashassistdatahubpostgresql.fullname" -}}
{{- $name := default "cashassistdatahubpostgresql" .Values.cashassistdatahubpostgresql.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

Create a default fully qualified Elasticsearch name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "hope.elasticsearch.fullname" -}}
{{- $name := default "elasticsearch" .Values.elasticsearch.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Get the Elasticsearch envs.
*/}}
{{- define "hope.elasticsearch.config" -}}
{{- if .Values.elasticsearch.enabled -}}
ELASTICSEARCH_HOST: {{ template "hope.elasticsearch.fullname" . }}-coordinating-only:9200
{{- else }}
ELASTICSEARCH_HOST: {{ .Values.externalElasticsearch.host }}
{{- end -}}
{{- end -}}

{{/*
Get the Main PostgreSQL envs.
*/}}
{{- define "hope.postgresql.config" -}}
{{- if .Values.postgresql.enabled -}}
POSTGRES_DB: {{ .Values.postgresql.postgresqlDatabase }}
POSTGRES_USER: {{ .Values.postgresql.postgresqlUsername }}
POSTGRES_HOST: {{ template "hope.postgresql.fullname" . }}
{{- else }}
POSTGRES_DB: {{ .Values.postgresql.externalDatabase.name }}
POSTGRES_USER: {{ .Values.postgresql.externalDatabase.user }}
POSTGRES_HOST: {{ .Values.postgresql.externalDatabase.host }}
{{- end -}}
{{- end -}}

{{/*
Get the Main PostgreSQL password.
*/}}
{{- define "hope.postgresql.password" -}}
{{- if .Values.postgresql.enabled -}}
POSTGRES_PASSWORD: {{ .Values.postgresql.postgresqlPassword | b64enc | quote }}
{{- else }}
POSTGRES_PASSWORD: {{ .Values.postgresql.externalDatabase.password | b64enc | quote }}
{{- end -}}
{{- end -}}

{{/*
Get the Main PostgreSQL envs for airflow.
*/}}
{{- define "hope.postgresql.airflow.config" -}}
{{- if .Values.postgresql.enabled -}}
AIRFLOW_DATABASE_NAME: {{ .Values.postgresql.postgresqlDatabase }}
AIRFLOW_DATABASE_USERNAME: {{ .Values.postgresql.postgresqlUsername }}
AIRFLOW_DATABASE_HOST: {{ template "hope.postgresql.fullname" . }}
POSTGRES_PORT: "5432"
AIRFLOW_DATABASE_PORT: "5432"
AIRFLOW_POSTGRES_PORT: "5432"
{{- else }}
AIRFLOW_DATABASE_NAME: {{ .Values.postgresql.externalDatabase.name }}
AIRFLOW_DATABASE_USERNAME: {{ .Values.postgresql.externalDatabase.user }}
AIRFLOW_DATABASE_HOST: {{ .Values.postgresql.externalDatabase.host }}
POSTGRES_PORT: "5432"
AIRFLOW_DATABASE_PORT: "5432"
AIRFLOW_POSTGRES_PORT: "5432"
{{- end -}}
{{- end -}}

{{/*
Get the Main PostgreSQL password for airflow.
*/}}
{{- define "hope.postgresql.airflow.password" -}}
{{- if .Values.postgresql.enabled -}}
{{- $fullName := include "hope.postgresql.fullname" . -}}
{{- $temp :=  printf "postgresql+psycopg2://%s:%s@%s:5432/%s" .Values.postgresql.postgresqlUsername .Values.postgresql.postgresqlPassword $fullName .Values.postgresql.postgresqlAirflowDatabase }}
{{- $tempWorker :=  printf "db+postgresql://%s:%s@%s:5432/%s" .Values.postgresql.postgresqlUsername .Values.postgresql.postgresqlPassword $fullName .Values.postgresql.postgresqlAirflowDatabase }}
AIRFLOW_DATABASE_PASSWORD: {{ .Values.postgresql.postgresqlPassword | b64enc | quote }}
AIRFLOW__CORE__SQL_ALCHEMY_CONN: {{ $temp | b64enc | quote }}
AIRFLOW__CELERY__RESULT_BACKEND: {{ $tempWorker | b64enc | quote }}
{{- else }}
{{- $temp :=  printf "postgresql+psycopg2://%s:%s@%s:5432/%s" .Values.postgresql.externalDatabase.user .Values.postgresql.externalDatabase.host .Values.postgresql.externalDatabase.host .Values.postgresql.externalDatabase.airflowName }}
{{- $tempWorker :=  printf "db+postgresql://%s:%s@%s:5432/%s" .Values.postgresql.externalDatabase.user .Values.postgresql.externalDatabase.host .Values.postgresql.externalDatabase.host .Values.postgresql.externalDatabase.airflowName }}
AIRFLOW_DATABASE_PASSWORD: {{ .Values.postgresql.externalDatabase.password | b64enc | quote }}
AIRFLOW__CORE__SQL_ALCHEMY_CONN: {{ $temp | b64enc | quote }}
AIRFLOW__CELERY__RESULT_BACKEND: {{ $tempWorker | b64enc | quote }}
{{- end -}}
{{- end -}}


{{/*
Get the registrationdatahubpostgresql envs.
*/}}
{{- define "hope.registrationdatahubpostgresql.config" -}}
{{- if .Values.registrationdatahubpostgresql.enabled -}}
POSTGRES_REGISTRATION_DATAHUB_DB: {{ .Values.registrationdatahubpostgresql.postgresqlDatabase }}
POSTGRES_REGISTRATION_DATAHUB_USER: {{ .Values.registrationdatahubpostgresql.postgresqlUsername }}
POSTGRES_REGISTRATION_DATAHUB_HOST: {{ template "hope.registrationdatahubpostgresql.fullname" .}}
{{- else }}
POSTGRES_REGISTRATION_DATAHUB_DB: {{ .Values.registrationdatahubpostgresql.externalDatabase.name }}
POSTGRES_REGISTRATION_DATAHUB_USER: {{ .Values.registrationdatahubpostgresql.externalDatabase.user }}
POSTGRES_REGISTRATION_DATAHUB_HOST: {{ .Values.registrationdatahubpostgresql.externalDatabase.host }}
{{- end -}}
{{- end -}}

{{/*
Get the registrationdatahubpostgresql password.
*/}}
{{- define "hope.registrationdatahubpostgresql.password" -}}
{{- if .Values.registrationdatahubpostgresql.enabled -}}
POSTGRES_REGISTRATION_DATAHUB_PASSWORD: {{ .Values.registrationdatahubpostgresql.postgresqlPassword | b64enc | quote }}
{{- else }}
POSTGRES_REGISTRATION_DATAHUB_PASSWORD: {{ .Values.registrationdatahubpostgresql.externalDatabase.password | b64enc | quote }}
{{- end -}}
{{- end -}}


{{/*
Get the cashassistdatahubpostgresql envs.
*/}}
{{- define "hope.cashassistdatahubpostgresql.config" -}}
{{- if .Values.cashassistdatahubpostgresql.enabled -}}
POSTGRES_CASHASSIST_DATAHUB_DB: {{ .Values.cashassistdatahubpostgresql.postgresqlDatabase }}
POSTGRES_CASHASSIST_DATAHUB_USER: {{ .Values.cashassistdatahubpostgresql.postgresqlUsername }}
POSTGRES_CASHASSIST_DATAHUB_HOST: {{ template "hope.cashassistdatahubpostgresql.fullname" .}}
{{- else }}
POSTGRES_CASHASSIST_DATAHUB_DB: {{ .Values.cashassistdatahubpostgresql.externalDatabase.name }}
POSTGRES_CASHASSIST_DATAHUB_USER: {{ .Values.cashassistdatahubpostgresql.externalDatabase.user }}
POSTGRES_CASHASSIST_DATAHUB_HOST: {{ .Values.cashassistdatahubpostgresql.externalDatabase.host }}
{{- end -}}
{{- end -}}

{{/*
Get the cashassistdatahubpostgresql password.
*/}}
{{- define "hope.cashassistdatahubpostgresql.password" -}}
{{- if .Values.cashassistdatahubpostgresql.enabled -}}
POSTGRES_CASHASSIST_DATAHUB_PASSWORD: {{ .Values.cashassistdatahubpostgresql.postgresqlPassword | b64enc | quote }}
{{- else }}
POSTGRES_CASHASSIST_DATAHUB_PASSWORD: {{ .Values.cashassistdatahubpostgresql.externalDatabase.password | b64enc | quote }}
{{- end -}}
{{- end -}}

{{/*
Return the proper Airflow Worker image name
*/}}
{{- define "airflow.workerImage" -}}
{{- $repositoryName := .Values.airflow.image.repository -}}
{{- $tag := .Values.airflow.image.tag | toString -}}
{{/*
Helm 2.11 supports the assignment of a value to a variable defined in a different scope,
but Helm 2.9 and 2.10 doesn't support it, so we need to implement this if-else logic.
Also, we can't use a single if because lazy evaluation is not an option
*/}}
{{- if .Values.global }}
    {{- if .Values.global.imageRegistry }}
        {{- printf "%s:%s" $repositoryName $tag -}}
    {{- else -}}
        {{- printf "%s:%s" $repositoryName $tag -}}
    {{- end -}}
{{- else -}}
    {{- printf "%s:%s" $repositoryName $tag -}}
{{- end -}}
{{- end -}}


{{/*
Return the proper Airflow Scheduler image name
*/}}
{{- define "airflow.schedulerImage" -}}
{{- $repositoryName := .Values.airflow.image.repository -}}
{{- $tag := .Values.airflow.image.tag | toString -}}
{{/*
Helm 2.11 supports the assignment of a value to a variable defined in a different scope,
but Helm 2.9 and 2.10 doesn't support it, so we need to implement this if-else logic.
Also, we can't use a single if because lazy evaluation is not an option
*/}}
{{- if .Values.global }}
    {{- if .Values.global.imageRegistry }}
        {{- printf "%s:%s" $repositoryName $tag -}}
    {{- else -}}
        {{- printf "%s:%s" $repositoryName $tag -}}
    {{- end -}}
{{- else -}}
    {{- printf "%s:%s" $repositoryName $tag -}}
{{- end -}}
{{- end -}}

{{/*
Return the proper Airflow image name
*/}}
{{- define "airflow.image" -}}
{{- $repositoryName := .Values.airflow.image.repository -}}
{{- $tag := .Values.airflow.image.tag | toString -}}
{{/*
Helm 2.11 supports the assignment of a value to a variable defined in a different scope,
but Helm 2.9 and 2.10 doesn't support it, so we need to implement this if-else logic.
Also, we can't use a single if because lazy evaluation is not an option
*/}}
{{- if .Values.global }}
    {{- if .Values.global.imageRegistry }}
        {{- printf "%s:%s" $repositoryName $tag -}}
    {{- else -}}
        {{- printf "%s:%s" $repositoryName $tag -}}
    {{- end -}}
{{- else -}}
    {{- printf "%s:%s" $repositoryName $tag -}}
{{- end -}}
{{- end -}}

