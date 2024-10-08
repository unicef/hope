# Dev

How to call the tests (from root of the project) - is incompatible with M1/M2/M3 chips:

```bash
docker compose -f compose.selenium.yml build ; docker compose -f compose.selenium.yml run --rm selenium
```

How to simulate a CI run (from `deployment` dir) - is incompatible with M1/M2/M3 chips:
```bash
sh -c "cd .. && docker build . -f ./docker/Dockerfile --target dev --tag unicef/hct-mis-backend-dev && docker build . -f ./docker/Dockerfile --target dist --tag unicef/hct-mis-backend-dist" && dev_backend_image=unicef/hct-mis-backend-dev dist_backend_image=unicef/hct-mis-backend-dist docker compose -f docker-compose.selenium.yml run --build --rm selenium; dev_backend_image=unicef/hct-mis-backend-dev dist_backend_image=unicef/hct-mis-backend-dist docker compose -f docker-compose.selenium.yml down --remove-orphans
```

<b><h2>How to run tests locally on Macs with M1/M2/M3:</h2></b>

<b><h3>Installation:</h3></b>
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)
curl https://pyenv.run | bash
brew install pyenv
vim ~/.zshrc
```
Include the following in the file:
```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

- In new terminal tab
```bash
pyenv install 3.11.7
pyenv virtualenv 3.11.7 new-venv
pyenv activate new-venv
brew install pdm
curl -sSL https://pdm-project.org/install-pdm.py | python -
pdm sync --no-editable --no-self --no-isolation

# admin required:
brew install wkhtmltopdf pango postgis gdal
```

<b><h3>Start tests:</h3></b>
```bash
pyenv activate new-venv
cd src
source ../development_tools/local_selenium_env.sh 

# second tab: 
docker compose -f ../development_tools/compose.selenium.local.yml up --build 
# first tab: 
python -m pytest -svvv ../tests/selenium --html-report=../tests/selenium/report/report.html
```