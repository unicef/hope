---
description: 'Technical details for handling identities, authentication and authorization'
---

# Identity and Access

**Auth:**

There is an app registered on our Unicef Azure AD Instance \(unicef.onmicrosoft.com\) the app name is uni-hct-ims-dev. The assignment to the app is based on our groups \(people on these groups will see the app on their Apps panel and will be able to login\)

The Client ID and Client Secrets are configured on the DEV namespace as secrets:

* hct-dev-client-id
* hct-dev-client-secret 

These should be declares on the POD definition for the container\(s\) that need them: I.E.

```text
env:
      - name: HCT_DEV_CLIENT_SECRET
        valueFrom:
          secretKeyRef:
            name: hct-dev-client-secret
            key: password
```

On the app there are two redirect URLs configured, one for the deployment on the dev cluster and the other for local development:

Sample config 

CLIENT\_ID = os.environ.get\('HCT\_DEV\_CLIENT\_ID'\) 

CLIENT\_SECRET = os.environ.get\('HCT\_DEV\_CLIENT\_SECRET'\) 

// REDIRECT\_URI = '[http://localhost:5000/login/authorized](http://localhost:5000/login/authorized)' 

REDIRECT\_URI = '[https://hct-ims.unitst.org/login/authorized](https://hct-ims.unitst.org/login/authorized)'

