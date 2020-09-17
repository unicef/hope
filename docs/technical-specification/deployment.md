# Deployment

## Purpose of this document/section is to describe current deployment and infrastructure status of the HOPE project.

## Overview

Core of HOPE project is based on 3 indepenedent container images, for three different services. This services are Backend\(written in Django\), Frontend\(written in React\) and Airflow. For building images and local development we are using Docker, which is well adopted and most popular tool for build and managing containers. It's easy to use for developers, and allows as to have idempotent environments no matter if we are running our stack locally or in cloud. We builded our application and deployment setup with containers and container orchestration in mind. For orchestration tool we decided to go with Kubernetes as it's the most supported tool in the market, and is widely used and adpoted at Unicef.

## Helm Chart

For bundling our app we are using Helm, which is package manager for Kubernetes. Our chart is available at [HOPE Chart](https://github.com/unicef/hct-mis/tree/develop/deployment/hope). There are three core parts of a chart:

* Chart.yaml - describes: name, version and dependencies of your chart
* values.yaml - describes variables that are available to modify in your chart like \(docker image tags, domain under which you want your service available or things like secret keys\)
* `/templates` - contains templates of Kubernetes manifests that are rendered based on `values.yaml` file.

## CI/CD

For building and deploying HOPE we are using Azure Pipelines. An example of pipeline definitions is [develop pipeline](https://github.com/unicef/hct-mis/blob/develop/deployment/pipeline-develop.yaml)

* Defines branches based on which this pipeline should be triggered\(`trigger:`\)
* Variables that are used at different stages of the pipeline\(`variables:`\)
* Stages that break our pipeline in to smaller steps\(`stages:`\)
* \[Build&Push\] stage that takes care of building our Docker images and pushing them to registry\(splitted in 3 concurrent jobs\)
* \[Deploy\] stage that updates dependencies for our Helm Chart and makes Helm release of HOPE Chart in which overwrites values with Pipeline variables/secrets

## Infrastructure

For infrastructure we are using k8s namespaces provider by Unicef via AKS\(Kubernetes\)clusters. We have access to operate only in our namespaces. For DEV environment we are using DB\(elasticsearch, postgresql\) as a container via Helm Chart dependencies. For Staging/UAT/PROD Unicef will provide us databases.

### **Databases**

**default**: the main database of the application, all core operations are executed on this database, stores Programmes, Cash Plans, Golden Record Households, and Individuals, Payments Data, Targeting Data, etc.

**cash assist datahub**: a database that has 3 schemas \(**CA, MIS**, and **ERP**\).

* **CA** is used to store data pulled from Cash Assist \(Programmes, Target Populations, Cash Plans, and Payment Data\)
* **MIS** holds Programmes, Target Populations, and connected with them Individuals and Households, data from this database is sent to Cash Assist
* **ERP** used to store data needed for integration with ERP system

**registration datahub**: database for RDI process, used as a staging area for Imported Individuals and Households.

**elasticsearch**: a search engine used in the process of deduplication and sanctions list check.

## Environments

### DEV

* Based on `develop` branch
* Uses container databases via Helm Chart dependencies
* HOPE accessible at: `https://dev-hope.unitst.org`
* Airflow accessible at: `https://airflow-hope-dev.unitst.org`
* Pipeline accessible at: `https://unicef.visualstudio.com/ICTD-HCT-MIS/_build?definitionId=436`
* Deployed on cluster: `uni-apps-aks-dev`
* Deployed in namespace: `ictd-hope-dev`

## Developer access and working with Kubernetes

List of developers with access:

* Jan Romaniak - jan.romaniak@tivix.com
* Sumit Chachra - sumit@tivix.com
* Wojciech Nosal - wojciech.nosal@tivix.com

### Prerequisites

* kubectl `brew install kubectl`
* Azure CLI `brew install azure-cli`

### Credentials, authorization

#### Dev cluster

1. `az login` -&gt; use your @tivix.com account
2. `az account set --s 83098d8e-02cd-4f17-9f08-be5bd22c590b` -&gt; set's your subscription to `83098d8e-02cd-4f17-9f08-be5bd22c590b`
3. `az aks get-credentials -g rs-uni-apps-aks-dev -n uni-apps-aks-dev` -&gt; get's your K8s access credentials -&gt; merges them into `~.kube/config` -&gt; should return something like `Merged "uni-apps-aks-dev" as current context in /Users/YOUR-USER/.kube/config`
4. You should have access to cluster. Run this command to check `kubectl get pods -n ictd-hope-dev` \(get all pods in namespace: ictd-hope-dev\) -&gt; it should return table with names of the pods, status, restarts and age
5. `kubectl config set-context --namespace ictd-hope-dev --current`

### Working with Kubernetes

#### Setting default namespace

To set default namespace for our Kubernetes context: `kubectl config set-context --namespace <namespace-name> --current`. This way you don't need to include `-n/--namespace` flag in your commands.

#### Getting list of running pods

`kubectl get pods`

#### Getting information about running pod/resource

`kubectl describe pod <name-of-the-pod>`

#### Exec into pod

`kubectl exec -it <name-of-the-pod> -- <command>`

#### Getting logs from a pod

`kubectl logs <name-of-the-pod>`

#### Port-forwarding to local network

Kubernetes has ability to forward pod port to our own network you can do this via: `kubectl port-forward <name-of-the-pod> <port-on-your-machine>:<pod-port-to-forward>`

