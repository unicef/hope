{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "kobo.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "kobo.fullname" -}}
{{- printf "%s" .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "kobo.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Construct the `labels.app` for used by all resources in this chart.
*/}}
{{- define "kobo.labels.app" -}}
{{- .Values.nameOverride | default .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Construct the `labels.chart` for used by all resources in this chart.
*/}}
{{- define "kobo.labels.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "kobo.labels" -}}
helm.sh/chart: {{ include "kobo.chart" . }}
{{ include "kobo.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "kobo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kobo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Create the name of the service account to use
*/}}
{{- define "kobo.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
    {{ default (include "kobo.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
    {{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}

{{/*
Create a default fully qualified postgresql name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "kobo.postgresql.fullname" -}}
{{- $name := default "postgresql" .Values.postgresql.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified redis name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "kobo.redismain.fullname" -}}
{{- $name := default "redis-main" .Values.redismain.fullnameOverride -}}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "kobo.rediscache.fullname" -}}
{{- $name := default "redis-cache" .Values.rediscache.fullnameOverride -}}
{{- printf "%s" $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Get the Postgresql credentials secret.
*/}}
{{- define "kobo.postgresql.secretName" -}}
{{- if and (.Values.postgresql.enabled) (not .Values.postgresql.existingSecret) -}}
    {{- printf "%s" (include "kobo.postgresql.fullname" .) -}}
{{- else if and (.Values.postgresql.enabled) (.Values.postgresql.existingSecret) -}}
    {{- printf "%s" .Values.postgresql.existingSecret -}}
{{- else }}
    {{- if .Values.externalDatabase.existingSecret -}}
        {{- printf "%s" .Values.externalDatabase.existingSecret -}}
    {{- else -}}
        {{ printf "%s-%s" .Release.Name "externaldb" }}
    {{- end -}}
{{- end -}}
{{- end -}}


{{- define "kobo.mongodb.fullname" -}}
{{- $name := default "mongodb" .Values.postgresql.nameOverride -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}


{{/*
Get the MongoDB credentials secret.
*/}}
{{- define "kobo.mongodb.secretName" -}}
{{- if and (.Values.mongodb.enabled) (not .Values.mongodb.existingSecret) -}}
    {{- printf "%s" (include "kobo.mongodb.fullname" .) -}}
{{- else if and (.Values.mongodb.enabled) (.Values.mongodb.existingSecret) -}}
    {{- printf "%s" .Values.mongodb.existingSecret -}}
{{- else }}
    {{- if .Values.monogodb.externalDatabase.existingSecret -}}
        {{- printf "%s" .Values.mongodb.externalDatabase.existingSecret -}}
    {{- else -}}
        {{ printf "%s-%s" .Release.Name "externaldb" }}
    {{- end -}}
{{- end -}}
{{- end -}}


{{/*
Get the Redis-main credentials secret.
*/}}
{{- define "kobo.redismain.secretName" -}}
{{- if and (.Values.redismain.enabled) (not .Values.redismain.existingSecret) -}}
    {{- printf "%s" (include "kobo.redismain.fullname" .) -}}
{{- else if and (.Values.redismain.enabled) (.Values.redismain.existingSecret) -}}
    {{- printf "%s" .Values.redismain.existingSecret -}}
{{- else }}
    {{- if .Values.externalDatabase.existingSecret -}}
        {{- printf "%s" .Values.externalDatabase.existingSecret -}}
    {{- else -}}
        {{ printf "%s-%s" .Release.Name "externaldb" }}
    {{- end -}}
{{- end -}}
{{- end -}}

{{/*
  Get the Kobo credentials secret
*/}}
{{- define "kobo.secretName" -}}
{{- if (not .Values.kobotoolbox.existingSecret) -}}
  {{- printf "%s" (include "kobo.fullname" .) -}}
{{- else }}
  {{- printf "%s" .Values.kobotoolbox.existingSecret }}
{{- end -}}
{{- end }}


{{/*
Get the Redis-cache credentials secret.
*/}}
{{- define "kobo.rediscache.secretName" -}}
{{- if and (.Values.rediscache.enabled) (not .Values.rediscache.existingSecret) -}}
    {{- printf "%s" (include "kobo.rediscache.fullname" .) -}}
{{- else if and (.Values.rediscache.enabled) (.Values.rediscache.existingSecret) -}}
    {{- printf "%s" .Values.rediscache.existingSecret -}}
{{- else }}
    {{- if .Values.externalDatabase.existingSecret -}}
        {{- printf "%s" .Values.externalDatabase.existingSecret -}}
    {{- else -}}
        {{ printf "%s-%s" .Release.Name "externaldb" }}
    {{- end -}}
{{- end -}}
{{- end -}}


{{/*
    Map KPI env secrets
*/}}
{{- define "kobo.mapenvsecrets" -}}
{{- /* POSTGRESQL */ -}}
{{- if .Values.postgresql.enabled }}
{{- if .Values.postgresql.existingSecret }}
- name: POSTGRES_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ .Values.postgresql.existingSecret }}
      key: {{ .Values.postgresql.existingSecretKey }}
{{- else }}
- name: POSTGRES_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ include "kobo.postgresql.fullname" . }}
      key: postgresql-password
{{- end -}}
{{- else }}
{{- if .Values.postgresql.externalDatabase.passwordSecret }}
- name: POSTGRES_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ .Values.postgresql.externalDatabase.passwordSecret }}
      key: {{ .Values.postgresql.externalDatabase.passwordSecretKey }}
{{- else }}
- name: POSTGRES_PASSWORD
  value: ""
{{- end }}
{{- end }}
{{- /* MONGODB */ -}}
{{- if .Values.mongodb.enabled }}
{{- if .Values.mongodb.existingSecret }}
- name: KPI_MONGO_PASS
  valueFrom:
    secretKeyRef:
      name: {{ .Values.mongodb.existingSecret }}
      key: {{ .Values.mongodb.existingSecretKey }}
- name: KOBOCAT_MONGO_PASS
  valueFrom:
    secretKeyRef:
      name: {{ .Values.mongodb.existingSecret }}
      key: {{ .Values.mongodb.existingSecretKey }}
- name: MONGO_INITDB_ROOT_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ .Values.mongodb.existingSecret }}
      key:  {{ .Values.mongodb.existingSecretRootKey }}
- name: KOBO_MONGO_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ .Values.mongodb.existingSecret }}
      key: {{ .Values.mongodb.existingSecretKey }}
{{- else }}
- name: KPI_MONGO_PASS
  valueFrom:
    secretKeyRef:
      name: {{ template "kobo.mongodb.secretName" . }}
      key: mongodb-password
- name: KOBOCAT_MONGO_PASS
  valueFrom:
    secretKeyRef:
      name: {{ template "kobo.mongodb.secretName" . }}
      key: mongodb-password
- name: MONGO_INITDB_ROOT_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ template "kobo.mongodb.secretName" . }}
      key: mongodb-root-password
- name: KOBO_MONGO_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ template "kobo.mongodb.secretName" . }}
      key: mongodb-password
{{- end }}
{{- else }}
{{- if .Values.mongodb.externalDatabase.existingSecret }}
- name: KPI_MONGO_PASS
  valueFrom:
    secretKeyRef:
      name: {{ .Values.mongodb.externalDatabase.existingSecret }}
      key: {{ .Values.mongodb.externalDatabase.passwordSecretKey }}
- name: KOBOCAT_MONGO_PASS
  valueFrom:
    secretKeyRef:
      name: {{ .Values.mongodb.externalDatabase.existingSecret }}
      key: {{ .Values.mongodb.externalDatabase.passwordSecretKey }}
- name: MONGO_INITDB_ROOT_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ .Values.mongodb.externalDatabase.existingSecret }}
      key: {{ .Values.mongodb.externalDatabase.rootPasswordSecretKey }}
- name: KOBO_MONGO_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ .Values.mongodb.externalDatabase.existingSecret }}
      key: {{ .Values.mongodb.externalDatabase.passwordSecretKey }}
{{- else }}
- name: KPI_MONGO_PASS
  value: ""
- name: MONGO_INITDB_ROOT_PASSWORD
  value: ""
- name: KOBO_MONGO_PASSWORD
  value: ""
{{- end }}
{{- end -}}
{{/* KOBO */}}
- name: KOBO_SUPERUSER_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ include "kobo.secretName" . }}
      {{- if .Values.kobotoolbox.exisitingSecret }}
      key: {{ .Values.kobotoolbox.exisitingSecretKey}}
      {{- else }}
      key: password
      {{- end }} 
- name: KOBO_SUPERUSER_USERNAME
  valueFrom:
    secretKeyRef:
      name: {{ include "kobo.secretName" . }}
      key: username
- name: DJANGO_SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "kobo.secretName" . }}
      key: djangoSecretKey
- name: SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: {{ include "kobo.secretName" . }}
      key: djangoSecretKey
{{/* REDIS */}}
- name: REDIS_PASSWORD
  valueFrom:
      secretKeyRef:
        name: {{ template "kobo.redismain.secretName" .}}
        key: redis-password
{{/* ENKETO */}}
- name: ENKETO_API_TOKEN
  valueFrom:
    secretKeyRef:
      name: {{ include "kobo.fullname" . }}-enketo
      key: key
{{- end }}

