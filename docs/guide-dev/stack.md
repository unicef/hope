---
title: Stack
---

# Technology Stack

## Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.13 | Runtime |
| **Django** | 5.2 | Web framework |
| **Django REST Framework** | 3.x | REST API |
| **Celery** | 5.x | Task queue |
| **PostgreSQL** | 14 | Primary database |
| **Redis** | 4.x | Cache & message broker |
| **Elasticsearch** | 8.14 | Search engine |

### Key Django Packages

- **django-celery-beat** - Periodic task scheduling
- **django-elasticsearch-dsl** - Elasticsearch integration
- **django-filter** - API filtering
- **django-storages** - Azure blob storage
- **drf-spectacular** - OpenAPI documentation
- **social-auth-app-django** - OAuth authentication

## Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19 | UI framework |
| **TypeScript** | 5.5 | Type safety |
| **Vite** | 7.x | Build tool |
| **MUI (Material-UI)** | 7.x | Component library |
| **React Query** | 5.x | Data fetching |
| **React Router** | 7.x | Routing |

### Key Frontend Packages

- **@tanstack/react-query** - Server state management
- **formik** + **yup** - Form handling and validation
- **i18next** - Internationalization
- **chart.js** - Data visualization
- **@sentry/react** - Error tracking

## Build & Development Tools

| Tool | Purpose |
|------|---------|
| **uv** | Python package management |
| **yarn** | JavaScript package management |
| **tox** | Test automation |
| **pre-commit** | Git hooks |
| **ruff** | Python linting & formatting |
| **Docker** | Containerization |

## Infrastructure

| Service | Purpose |
|---------|---------|
| **Azure Blob Storage** | File storage |
| **Sentry** | Error monitoring |
| **Gunicorn** | WSGI server (production) |

## Project Structure

```
hope/
├── src/
│   ├── hope/                    # Django project
│   │   ├── config/              # Django settings (settings.py, env.py)
│   │   ├── models/              # All models (yes, ALL of them here)*
│   │   ├── admin/               # All admin classes (here too)*
│   │   ├── api/                 # REST API endpoints
│   │   ├── apps/                # Django apps (without models/admin)
│   │   │   ├── core/            # Core functionality, Celery
│   │   │   ├── web/             # Web app serving frontend
│   │   │   │   └── static/web/  # Frontend build output**
│   │   │   └── ...
│   │   └── ...
│   └── frontend/                # React application (Vite)
│       ├── src/                 # React source code
│       └── build/               # Local build output
├── tests/
│   ├── unit/                    # Unit tests
│   └── e2e/                     # End-to-end tests
├── docker/                      # Docker configuration
├── development_tools/           # Docker Compose for local dev
├── docs/                        # Documentation
├── manage.py                    # Django management script
├── pyproject.toml               # Python project configuration
├── tox.ini                      # Test configuration
└── uv.lock                      # Python dependency lock file
```

### Architectural Curiosities

**\* Centralized models and admin:** Unlike typical Django projects where each app has its own `models.py` and `admin.py`, HOPE keeps all models in `src/hope/models/` and all admin classes in `src/hope/admin/` as separate files per entity.

**\*\* Committed build artifacts:** The frontend build output (`src/hope/apps/web/static/web/`) is committed to the repository. This is unconventional - most projects gitignore build artifacts. Here, it ensures Django can serve the frontend without requiring a Node.js build step in production. The `manage.py runserver` command automatically rebuilds and watches for changes during development.

## Dependencies

Full list of Python dependencies is in [`pyproject.toml`](https://github.com/unicef/hope/blob/develop/pyproject.toml).

Frontend dependencies are in [`src/frontend/package.json`](https://github.com/unicef/hope/blob/develop/src/frontend/package.json).

## Version Requirements

- Python: `==3.13.*`
- Node.js: `>=20.0.0`
