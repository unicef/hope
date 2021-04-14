# KOBOTOOLBOX

[KoBoToolbox](https://www.kobotoolbox.org/) is a suite of tools for field data collection for use in challenging environments.

## TL;DR

```bash
$ helm repo add unicef https://unicef.github.io/charts
$ helm install my-release unicef/kobo
```

## Introduction

This chart bootstraps an [KoBoToolbox](https://github.com/kobotoolbox/kobo-docker) deployment on a [Kubernetes](http://kubernetes.io) cluster using the [Helm](https://helm.sh) package manager.

## Prerequisites
- Kubernetes 1.14+
- Helm 3.0+

## Installing the Chart

To install the chart with the release name `my-release`:

```bash
$ helm repo add unicef https://unicef.github.io/charts
$ helm install my-release unicef/kobo
```

These commands deploy KoBoToolbox on the Kubernetes cluster in the default configuration. The [Parameters](#parameters) section lists the parameters that can be configured during installation.

> **Tip**: List all releases using `helm list`

## Uninstalling the Chart

To uninstall/delete the `my-release` deployment:

```bash
$ helm delete my-release
```

The command removes all the Kubernetes components associated with the chart and deletes the release.

## Parameters

The following tables lists the configurable parameters of the KoBoToolbox chart and their default values.

### Global parameters

| Parameter             | Description                                   | Default |
|:----------------------|:----------------------------------------------|:--------|
| `global.storageClass` | Global storage class for dynamic provisioning | `nil`   |

### KoBoToolbox parameters
| Parameter                        | Description                                                          | Default                           |
|:---------------------------------|:---------------------------------------------------------------------|:----------------------------------|
| `kobotoolbox.superuserName`      | Superuser name to access KoboToolBox                                 | `superuser`                       |
| `kobotoolbox.superuserPassword`  | Superuser password to access KoboToolBox                             | `random alphanumeric string (10)` |
| `kobotoolbox.exisitingSecret`    | Name of an existing secret containing KoboToolbox superuser password | `nil`                             |
| `kobotoolbox.exisitingSecretKey` | Key of existingSecret containing password to access KoboToolBox      | `kobo-password`                   |

### SMTP parameters
| Parameter    | Description                  | Default            |
|:-------------|:-----------------------------|:-------------------|
| `smtp.host`  | SMTP Host for sending emails | `nil`              |
| `smtp.email` | Address for sending emails   | `change@email.com` |


### Ingress parameters
| Parameter             | Description                                               | Default             |
|:----------------------|:----------------------------------------------------------|:--------------------|
| `ingress.scheme`      | Defines HTTP/HTTPS scheme for generating KoboToolbox URLs | `http`              |
| `ingress.host`        | Root domain for KoboToolbox                               | `kobotoolbox.local` |
| `ingress.annotations` | Additional annotations for KoboToolbox ingress            | `{}`                |
| `ingress.tls`         | Utilize TLS backend in ingress                            | `false`             |
| `ingress.tlsSecret`   | TLS Secret Name                                           | `nil`               |

### Postgresql parameteres
| Parameter                                       | Description                                                   | Default                           |
|:------------------------------------------------|:--------------------------------------------------------------|:----------------------------------|
| `postgresql.enabled`                            | Switch to enable or disable the PostgreSQL helm chart         | `true`                            |
| `postgresql.postgresqlDatabase`                 | KoboToolbox Postgresql database                               | `kobocat`                         |
| `postgresql.postgresqlUsername`                 | KoboToolbox Postgresql username                               | `kobo`                            |
| `postgresql.postgresqlPassword`                 | KoboToolbox Postgresql password                               | `random alphanumeric string (10)` |
| `postgresql.externalDatabase.host`              | External PostgreSQL host                                      | `nil`                             |
| `postgresql.externalDatabase.port`              | External PostgreSQL port                                      | `nil`                             |
| `postgresql.externalDatabase.user`              | External PostgreSQL user                                      | `nil`                             |
| `postgresql.externalDatabase.existingSecret`    | Name of an existing secret containing the PostgreSQL password | `nil`                             |
| `postgresql.externalDatabase.passwordSecretKey` | Key of existingSecret containing password to PostgreSQL       | `postgresql-password`             |
| `postgresql.externalDatabase.kpiDatabase`       | External PostgreSQL KPI database name                         | `nil`                             |
| `postgresql.externalDatabase.kobocatDatabase`   | External PostgreSQL Kobocat database name                     | `nil`                             |
| `postgresql.image.tag`                          | MongoDB container image tag                                   | `10.12.0`                         |

### Mongodb parameters
| Parameter                                        | Description                                                | Default                           |
|:-------------------------------------------------|:-----------------------------------------------------------|:----------------------------------|
| `mongodb.enabled`                                | Switch to enable or disable the MongoDB helm chart         | `true`                            |
| `mongodb.mongodbDatabase`                        | KoboToolbox MonogoDB database                              | `formhub`                         |
| `mongodb.mongodbUsername`                        | KoboToolbox MonogoDB username                              | `kobo`                            |
| `mongodb.mongodbPassword`                        | KoboToolbox MonogoDB password                              | `random alphanumeric string (10)` |
| `mongodb.externalDatabase.mongodbHost`           | External MongoDB host                                      | `nil`                             |
| `mongodb.externalDatabase.mongodbUsername`       | External MongoDB  username                                 | `nil`                             |
| `mongodb.externalDatabase.mongodbDatabase`       | External MongoDB database                                  | `nil`                             |
| `mongodb.externalDatabase.existingSecret`        | Name of an existing secret containing the MongoDB password | `nil`                             |
| `mongodb.externalDatabase.existingSecretKey`     | Key of existingSecret containing password to MongoDB       | `mongodb-password`                |
| `mongodb.externalDatabase.rootPasswordSecretKey` | Key of existingSecret containing root password to MongoDB  | `mongodb-root-password`           |
| `mongodb.image.tag`                              | MongoDB container image tag                                | `4.0.16-ol-7-r21`                 |

### Redis Main parameters
| Parameter                    | Description                                      | Default           |
|:-----------------------------|:-------------------------------------------------|:------------------|
| `redismain.enabled`          | Switch to enable or disable the Redis helm chart | `true`            |
| `redismain.fullnameOverride` | SMTP Host for sending emails                     | `redis-main`      |
| `redismain.image.tag`        | Redis container image tag                        | `4.0.16-ol-7-r21` |

### Redis Cache parameters
| Parameter                     | Description                                      | Default           |
|:------------------------------|:-------------------------------------------------|:------------------|
| `rediscache.enabled`          | Switch to enable or disable the Redis helm chart | `true`            |
| `rediscache.fullnameOverride` | SMTP Host for sending emails                     | `redis-cache`     |
| `rediscache.image.tag`        | Redis container image tag                        | `4.0.16-ol-7-r21` |

### Kobocat service parameters 
| Parameter              | Description                                                | Default                        |
|:-----------------------|:-----------------------------------------------------------|:-------------------------------|
| `kobocat.subdomain`    | Subdomain for kobocat (will be combined with ingress.host) | `kc`                           |
| `kobocat.image`        | Kobocat image                                              | `kobotoolbox/kobocat:2.020.25` |
| `kobocat.service.type` | Service type for Kobocat                                   | `ClusterIP`                    |
| `kobocat.replicas`     | Number of Kobocat pod replicas                             | `1`                            |
| `kobocat.resources`    | Kobocat resource requests/limit                            | `{}`                           |
| `kobocat.podLabels`    | Additional labels for the pod(s)                           | `{}`                           |
| `kobocat.labels`       | Additional labels for the deployment or statefulsets       | `{}`                           |
| `kobocat.annotations`  | Annotations to be added to the deployment or statefulsets  | `{}`                           |
| `kobocat.nodeSeletor`  | Node labels for pod assignment                             | `{}`                           |
| `kobocat.affinity`     | Affinity for pod assignment                                | `{}`                           |

### Kpi service parameters 
| Parameter          | Description                                               | Default                    |
|:-------------------|:----------------------------------------------------------|:---------------------------|
| `kpi.subdomain`    | Subdomain for Kpi (will be combined with ingress.host)    | `kf`                       |
| `kpi.image`        | kpi image                                                 | `kobotoolbox/kpi:2.020.25` |
| `kpi.service.type` | Service type for Kpi                                      | `ClusterIP`                |
| `kpi.replicas`     | Number of Kpi pod replicas                                | `1`                        |
| `kpi.resources`    | kpi resource requests/limit                               | `{}`                       |
| `kpi.podLabels`    | Additional labels for the pod(s)                          | `{}`                       |
| `kpi.labels`       | Additional labels for the deployment or statefulsets      | `{}`                       |
| `kpi.annotations`  | Annotations to be added to the deployment or statefulsets | `{}`                       |
| `kpi.nodeSeletor`  | Node labels for pod assignment                            | `{}`                       |
| `kpi.affinity`     | Affinity for pod assignment                               | `{}`                       |

### Enketo service parameters 
| Parameter             | Description                                               | Default                                          |
|:----------------------|:----------------------------------------------------------|:-------------------------------------------------|
| `enketo.subdomain`    | Subdomain for Enketo (will be combined with ingress.host) | `ek`                                             |
| `enketo.image`        | Enketo image                                              | `kobotoolbox/enketo-express-extra-widgets:2.3.3` |
| `enketo.service.type` | Service type for Enketo                                   | `ClusterIP`                                      |
| `enketo.replicas`     | Number of Enketo pod replicas                             | `1`                                              |
| `enketo.resources`    | Enketo resource requests/limit                            | `{}`                                             |
| `enketo.podLabels`    | Additional labels for the pod(s)                          | `{}`                                             |
| `enketo.labels`       | Additional labels for the deployment or statefulsets      | `{}`                                             |
| `enketo.annotations`  | Annotations to be added to the deployment or statefulsets | `{}`                                             |
| `enketo.nodeSeletor`  | Node labels for pod assignment                            | `{}`                                             |
| `enketo.affinity`     | Affinity for pod assignment                               | `{}`                                             |                                          |

Specify each parameter using the `--set key=value[,key=value]` argument to `helm install`. For example,

```bash
$ helm install my-release \
  --set postgresql.postgresqlPassword=secretpassword,kobotoolbox.superuserPassword=secretpasssword \
    unicef/kobo
```

The above command sets the PostgreSQL `postgres` account password to `secretpassword` and the KoboToolBox account password to `secretpassword`.

Alternatively, a YAML file that specifies the values for the parameters can be provided while installing the chart. For example,

```bash
$ helm install my-release -f values.yaml unicef/kobo
```

> **Tip**: You can use the default [values.yaml](values.yaml)


## Persistence

The Unicef KoboToolbox chart relies on the bitnami/postgresql, bitnami/mongodb and bitnami/redis chart persistence. This means that KoboToolbox does not persist anything.

--- 
## Local setup
- Requirements:
  - [minikube](https://github.com/kubernetes/minikube)
  - [minikube ingress-dns](https://github.com/kubernetes/minikube/tree/master/deploy/addons/ingress-dns)(`use 'test' domain in resolvconf/resolver[linux/osx]`)
  - [minikube ingress](https://kubernetes.io/docs/tasks/access-application-cluster/ingress-minikube/)
  - [helm v3](https://helm.sh/docs/intro/install/)

- Steps:
  - `minikube start`
  - `helm upgrade --install --set redismain.password=redisPassword --set rediscache.password=redisPassword --set postgresql.postgresqlPassword=postgresPassword --set mongodb.mongodbPassword=mongodbPassword kobo .` will return command that you need to run to get KOBO Superuser password(looking like this `export KOBO_PASSWORD=$(kubectl get secret --namespace default "kobo-su-secret" -o jsonpath="{.data.password}" | base64 --decode)`)
  - `echo "$KOBO_PASSWORD"` -> it will print Kobo superuser password
  - `GO TO` `kf.kobotoolbox.test` `username: superuser` `password: FROM PREVIOUS STEP` 
``````
