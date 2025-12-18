---
title: Setup
---

# Development Environment Setup

This guide will help you set up your local development environment for HOPE.

## Prerequisites

### macOS

Install system dependencies using Homebrew:

```bash
brew install wkhtmltopdf pango postgis gdal
```

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.13 | Backend runtime |
| Node.js | 20+ | Frontend tooling |
| yarn | latest | Frontend package manager |
| uv | latest | Python package manager |
| direnv | latest | Environment variable management |
| Docker | latest | Services (PostgreSQL, Redis, Elasticsearch) |

#### Installing Node.js with nvm (recommended)

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install and use Node.js 20
nvm install 20
nvm use 20
```

#### Installing uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Installing direnv

```bash
# macOS
brew install direnv

# Add to your shell (bash)
echo 'eval "$(direnv hook bash)"' >> ~/.bashrc

# Add to your shell (zsh)
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
```

## Clone Repository

```bash
git clone git@github.com:unicef/hope.git
cd hope
```

## Environment Configuration

### Using direnv (Recommended)

The project includes an `.envrc` file that automatically sets up environment variables when you enter the project directory.

1. Copy the example file if needed:
   ```bash
   cp .envrc.example .envrc
   ```

2. Allow direnv to load the file:
   ```bash
   direnv allow
   ```

This will:
- Create a virtual environment in `.venv/`
- Activate the virtual environment
- Set all required environment variables for local development

### Key Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://postgres:postgres@localhost:5432/postgres` |
| `CELERY_BROKER_URL` | Redis URL for Celery | `redis://localhost:6379/0` |
| `ELASTICSEARCH_HOST` | Elasticsearch URL | `http://localhost:9200` |
| `CELERY_TASK_ALWAYS_EAGER` | Run Celery tasks synchronously | `true` |
| `DEBUG` | Django debug mode | `true` |

## Services Setup

HOPE requires three external services:
- **PostgreSQL** - Primary database
- **Redis** - Celery broker and cache
- **Elasticsearch** - Search engine

### Option A: Docker (Recommended)

Run services using Docker Compose:

```bash
cd development_tools
cp .env.example .env  # if not done yet
docker compose up db redis elasticsearch -d
```

This starts:
- PostgreSQL on port `5432`
- Redis on port `6379`
- Elasticsearch on port `9200`

To stop services:
```bash
docker compose down
```

To stop and remove volumes (clean start):
```bash
docker compose down -v
```

### Option B: Local Installation

If you prefer to run services locally without Docker:

**PostgreSQL:**
```bash
# macOS
brew install postgresql@14
brew services start postgresql@14
createdb postgres
```

**Redis:**
```bash
# macOS
brew install redis
brew services start redis
```

**Elasticsearch:**
```bash
# macOS
brew tap elastic/tap
brew install elastic/tap/elasticsearch-full
brew services start elasticsearch-full
```

Make sure your `.envrc` points to `localhost` for all services (this is the default).

## Python Dependencies

With direnv active, your virtual environment should be ready. Install dependencies:

```bash
uv sync
```

This installs all dependencies from `pyproject.toml` and `uv.lock`.

## Frontend Dependencies

```bash
cd src/frontend
yarn install
```

## Pre-commit Hooks

Pre-commit automatically checks and formats code before each commit. When frontend files change, it automatically rebuilds the frontend.

### Installation

```bash
# Install pre-commit (if not already installed)
uv tool install pre-commit

# Activate hooks in the repository
pre-commit install
```

### Hooks Used

| Hook | Description |
|------|-------------|
| `ruff` | Python linting with auto-fix |
| `ruff-format` | Python code formatting |
| `djade` | Django template formatting |
| `pyproject-fmt` | pyproject.toml formatting |
| `tox-ini-fmt` | tox.ini formatting |
| `trailing-whitespace` | Remove trailing whitespace |
| `end-of-file-fixer` | Ensure files end with newline |
| `frontend-build-check` | When `src/frontend/` changes, runs `yarn build-for-backend` and requires staging generated files |

### Manual Execution

```bash
# Run on all files
pre-commit run --all-files

# Or via tox
direnv exec . tox -e lint
```

## Next Steps

Your environment is now ready! Continue to [Running](running.md) to start the application.
