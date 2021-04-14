# DevOps / Infra

### CI / CD

For CI and CD we will leverage [CodeFresh](https://codefresh.io/) \(CF\). Builds will be triggered by commits to our git repository in Github. There will be as many pipelines as environments \(see below\).

CodeFresh will build all images \(one per service\), run [unit and E2E tests](../development-setup/testing-strategy.md) and if successful push the images to the CF registry and eventually push to the images for deployment to the appropriate environment.

### Infra

It has been decided to centrally host HCT MIS on Microsoft Azure. We will leverage [Rancher](https://rancher.com) and [Kubernetes](https://kubernetes.io/) to run all our dockerized services. These would run on Azure compute nodes.

#### Setup

Ideally we would like to leverage [Terraform](https://www.terraform.io/docs/providers/azurerm/index.html) to have a replicable infrastructure setup that is documented in code.

#### Environments

We will have a development, staging, UAT and production environment ideally, each of which are identical and run in their own sandboxed setup.

#### PostgreSQL

For the relational database we will leverage [Azure PostgreSQL](https://azure.microsoft.com/en-us/services/postgresql/) as provisioned by UNICEF IT Services.



