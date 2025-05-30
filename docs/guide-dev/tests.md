# Test Suite

The test suite is located within the tests directory and is organized into two subdirectories: unit and selenium. 
The unit directory contains unit tests, which focus on testing individual components of the project in isolation. 
The selenium directory contains tests that utilize Selenium for browser-based testing,
ensuring that the user interface and web interactions function as expected.

## Run "Unit" tests 
Unit tests are executed within a Docker container using the pytest framework.
This ensures a consistent testing environment, isolated from local machine configurations.
   ```bash
    docker compose run --rm backend pytest -n auto --reruns 3  -rP -p no:warnings --cov-report= --capture=sys  ./tests/unit
   ```


## Run "Selenium" functional test


Selenium tests run on the host machine. 
This is due to the fact that Selenium does not currently support the ARM64 architecture for Linux Docker images.
This will require some more steps to be taken before running the tests.
### Prerequisites
- uv

### Installation
1. **Services**

   To run the tests locally, the following services are required:
   
   1. **Postgres**
   1. **Redis**
   1. **Elasticsearch**
   
   You can either install these services manually or use the `docker-compose` file located in the `development_tools` directory.

2. **Running Services with Docker Compose**
   
   Make sure you have the required `.env` file from the backend setup, then you can run the services using the following command:

   ```bash
   cd development_tools
   docker compose --profile services up
   ```
3. **Running tests**

1. Install system requirements on MACOS:
   `brew install wkhtmltopdf pango postgis gdal`
2. Create virtualenvironment:
    `uv venv .venv --python 3.12.0`
3. Register the created venv for the project with: 
    `uv sync` 
4. Activate your venv: 
    `source .venv/bin/activate`
5. Check your environment:
    eg. `$python --version` -> see that it uses Python 3.12.*
6. Install the packages:
    `uv build`
7. Run the tests:
    ```bash
      source ./development_tools/local_selenium_init.sh`
      python -m pytest -svvv tests/selenium --html-report=./report/report.html`
    ```
