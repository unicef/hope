# Overview

This service helps in E2E testing of the web application. It supports running it in headless mode in a local development environment or as part of a CI/CD environment.

Example spec files: https://github.com/cypress-io/cypress-example-kitchensink/tree/master/cypress/integration/examples

Example commands: https://example.cypress.io/


## Local development / testing

In this directory run ```yarn``` (install yarn if you don't have it locally)

Create a ```cypress.env.json``` file (copy the ```cypress.env.json.example``` file and fill in the appropriate values).

Make sure your local development environment is up and running on http://localhost:*/

To start then run ```$(npm bin)/cypress open``` in this directory. You can now run the tests.
