---
title: Running
---

# Running the Application

HOPE supports three development workflows. Choose the one that best fits your needs.

## Prerequisites

Before running the application, ensure:

1. [Environment is set up](setup.md)
2. Services are running (PostgreSQL, Redis, Elasticsearch)
3. Python and frontend dependencies are installed

## Option 1: Local Backend + Frontend Build with Watch (Recommended)

This is the recommended approach for most development work. It builds the frontend into Django's static directory and watches for changes.

### Start Services

```bash
cd development_tools
docker compose up db redis elasticsearch -d
```

### Run Application

From the project root:

```bash
python manage.py runserver
```

This command automatically:
- Starts the Django development server on port `8000`
- Runs `yarn build-and-watch` in the background
- Builds frontend to `src/hope/apps/web/static/web/`
- Watches for frontend changes and rebuilds automatically

### Access

- **Application:** http://localhost:8000/
- **Admin Panel:** http://localhost:8000/api/unicorn/

### When to Use

- Full integration testing
- Backend-focused development
- When you need Django to serve the frontend

---

## Option 2: Local Backend + Vite Dev Server

This approach gives you Hot Module Replacement (HMR) for faster frontend development.

### Start Services

```bash
cd development_tools
docker compose up db redis elasticsearch -d
```

### Run Backend

From the project root:

```bash
python manage.py runserver --classic
```

The `--classic` flag runs only the Django server without the frontend build process.

### Run Frontend

In a separate terminal:

```bash
cd src/frontend
yarn dev
```

This starts the Vite dev server on port `3000` with:
- Hot Module Replacement (HMR)
- Fast refresh for React components
- Proxy to backend API on port `8080`

### Access

- **Frontend:** http://localhost:3000/
- **Admin Panel:** http://localhost:8080/api/unicorn/
- **Backend API:** http://localhost:8080/api/

### When to Use

- Frontend-focused development
- When you need fast feedback on UI changes
- Component development with HMR

---

## Option 3: Full Docker

This approach runs everything in Docker containers, closest to production.

### Setup

```bash
cd development_tools
cp .env.example .env  # if not done yet
```

### Build and Run

```bash
docker compose --profile default build
docker compose --profile default up
```

This starts:
- Backend container on port `8080`
- PostgreSQL, Redis, Elasticsearch
- Celery worker, beat, and flower

### Run Frontend

In a separate terminal:

```bash
cd src/frontend
yarn dev
```

### Access

- **Frontend:** http://localhost:3000/
- **Admin Panel:** http://localhost:8080/api/unicorn/
- **Flower (Celery monitoring):** http://localhost:5555/

### When to Use

- Production-like environment testing
- Celery task debugging with real workers
- When you need containerized backend

---

## First-Time Initialization

After starting the application for the first time, you need to initialize the database.

### Run Migrations

```bash
python manage.py migrate
```

Or with Docker:
```bash
docker compose run --rm backend python manage.py migrate
```

### Load Demo Data

```bash
python manage.py initdemo
```

Or with Docker:
```bash
docker compose run --rm backend python manage.py initdemo
```

### Create Superuser

```bash
python manage.py createsuperuser
```

Or with Docker:
```bash
docker compose run --rm backend python manage.py createsuperuser
```

### Configure User Access

1. Log in to Admin Panel at `/api/unicorn/`
2. Go to **Account > Users** and select your superuser
3. Add a **User Role** at the bottom:
   - Business Area: `Afghanistan` (has test data)
   - Role: `Role with all Permissions (HOPE)`
4. Save

You can now access the main application.

---

## Running Celery

By default, development uses `CELERY_TASK_ALWAYS_EAGER=true`, which runs Celery tasks synchronously without needing workers.

For testing with real Celery workers:

### Celery Worker

```bash
celery -A hope.apps.core.celery worker -l info
```

### Celery Beat (Scheduled Tasks)

```bash
celery -A hope.apps.core.celery beat -l INFO --scheduler hope.apps.core.models:CustomDatabaseScheduler
```

### Flower (Monitoring)

```bash
celery -A hope.apps.core.celery flower --port=5555
```

Access Flower at http://localhost:5555/

---

## Summary

| Option | Command | Frontend URL | Backend URL |
|--------|---------|--------------|-------------|
| **1. Build + Watch** | `python manage.py runserver` | :8000 | :8000 |
| **2. Vite Dev** | `runserver --classic` + `yarn dev` | :3000 | :8080 |
| **3. Full Docker** | `docker compose up` + `yarn dev` | :3000 | :8080 |
