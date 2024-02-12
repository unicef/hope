# Dev

How to call the tests (from root of the project):

```bash
docker compose -f compose.selenium.yml up --build --exit-code-from selenium --abort-on-container-exit
```