---
description: Details on the K8S config maps and secrets
---

# App configuration and secrets

The app will use a combination of secrets and config maps local to the App Namespace

The secrets are

```text
hct-dev-client-id -> AAD App Client ID (OAuth)
hct-dev-client-secret -> AAD App Client Secret (OAuth)
hct-dev-db-password -> Postgres DB User Password (dev and tst)
hct-dev-storage-key -> Storage Account Key
```

The config map contains the following

```text
apiVersion: v1
kind: ConfigMap
metadata:
  name: hct-dev-config-map
  namespace: hct-ims-dev
data:
  DB_SERVER: pgsql-hctmis-dev.postgres.database.azure.com
  DB_DEV: hctmis_app_devdb
  DB_TST: hctmis_stg_devdb
```

