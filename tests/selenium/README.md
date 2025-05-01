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

<b><h3>Preconditions:</h3></b>
- Check your arch
```bash
arch
```
The result should be **arm64**.


<b><h3>Installation:</h3></b>
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

- Check your brew config
```bash
brew config
```
The result of HOMEBREW_PREFIX should be /opt/homebrew

```bash
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
pyenv install 3.12.7
pyenv virtualenv 3.12.7 new-venv
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
brew install nvm
nano ~/.bash_profile
```
- Include the following in the file:
```bash
export NVM_DIR=~/.nvm
source $(brew --prefix nvm)/nvm.sh
. "$HOME/.cargo/env"
```
- In terminal:
```bash
source ~/.bash_profile
source ../development_tools/local_selenium_init.sh

# second tab:
docker compose -f ./development_tools/compose.yml --profile services up --build
# first tab:
python -m pytest -n auto -rP --reuse-db -p no:warnings --cov-report= --capture=sys --html-report=$OUTPUT_DATA_ROOT/report/report.html tests/selenium
```

<b><h3>Hints:</h3></b>
- Uninstall brew from wrong path (in this case /usr/local):
```bash
curl -fsSLO https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh
/bin/bash uninstall.sh --path /usr/local
```
