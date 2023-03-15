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
Create a default fully qualified postgresql name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "hope.postgresql.fullname" -}}
{{- $name := default "postgresql" .Values.postgresql.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified registrationdatahubpostgresql name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "hope.registrationdatahubpostgresql.fullname" -}}
{{- $name := default "registrationdatahubpostgresql" .Values.registrationdatahubpostgresql.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified cashassistdatahubpostgresql name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "hope.cashassistdatahubpostgresql.fullname" -}}
{{- $name := default "cashassistdatahubpostgresql" .Values.cashassistdatahubpostgresql.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Get the Main PostgreSQL envs.
*/}}
{{- define "hope.postgresql.config" -}}
{{- if .Values.postgresql.enabled -}}
POSTGRES_DB: {{ .Values.postgresql.auth.database }}
POSTGRES_USER: {{ .Values.postgresql.auth.username }}
POSTGRES_HOST: {{ template "hope.postgresql.fullname" . }}
{{- end -}}
{{- end -}}

{{/*
Get the Main PostgreSQL password.
*/}}
{{- define "hope.postgresql.password" -}}
{{- if .Values.postgresql.enabled -}}
POSTGRES_PASSWORD: {{ .Values.postgresql.auth.password | b64enc | quote }}
{{- end -}}
{{- end -}}


{{/*
Get the registrationdatahubpostgresql envs.
*/}}
{{- define "hope.registrationdatahubpostgresql.config" -}}
{{- if .Values.registrationdatahubpostgresql.enabled -}}
POSTGRES_REGISTRATION_DATAHUB_DB: {{ .Values.registrationdatahubpostgresql.auth.database }}
POSTGRES_REGISTRATION_DATAHUB_USER: {{ .Values.registrationdatahubpostgresql.auth.username }}
POSTGRES_REGISTRATION_DATAHUB_HOST: {{ template "hope.registrationdatahubpostgresql.fullname" .}}
{{- end -}}
{{- end -}}

{{/*
Get the registrationdatahubpostgresql password.
*/}}
{{- define "hope.registrationdatahubpostgresql.password" -}}
{{- if .Values.registrationdatahubpostgresql.enabled -}}
POSTGRES_REGISTRATION_DATAHUB_PASSWORD: {{ .Values.registrationdatahubpostgresql.externalDatabase.password | b64enc | quote }}
{{- end -}}
{{- end -}}


{{/*
Get the cashassistdatahubpostgresql envs.
*/}}
{{- define "hope.cashassistdatahubpostgresql.config" -}}
{{- if .Values.cashassistdatahubpostgresql.enabled -}}
POSTGRES_CASHASSIST_DATAHUB_DB: {{ .Values.cashassistdatahubpostgresql.auth.database }}
POSTGRES_CASHASSIST_DATAHUB_USER: {{ .Values.cashassistdatahubpostgresql.auth.username }}
POSTGRES_CASHASSIST_DATAHUB_HOST: {{ template "hope.cashassistdatahubpostgresql.fullname" .}}
{{- end -}}
{{- end -}}

{{/*
Get the cashassistdatahubpostgresql password.
*/}}
{{- define "hope.cashassistdatahubpostgresql.password" -}}
{{- if .Values.cashassistdatahubpostgresql.enabled -}}
POSTGRES_CASHASSIST_DATAHUB_PASSWORD: {{ .Values.cashassistdatahubpostgresql.auth.password | b64enc | quote }}
{{- end -}}
{{- end -}}

