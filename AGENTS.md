# AGENTS.md

This repository is a Django + PostGIS application for discovering, downloading, importing, and visualizing Spanish cadastral data from the Catastro INSPIRE feeds. Use this file as the shortest high-signal guide before making changes.

## Start here

- Project docs: [README.md](README.md)
- Django settings: [backend/config/settings.py](backend/config/settings.py)
- Main web entry: [backend/ingest/views.py](backend/ingest/views.py)
- Docker stack: [docker-compose.yml](docker-compose.yml)
- Container runtime: [Dockerfile](Dockerfile)

## Project layout

- [backend/](backend/): Django project and apps
  - [backend/config/](backend/config/): settings, URLs, ASGI/WSGI setup
  - [backend/ingest/](backend/ingest/): data ingestion, management commands, templates, views
  - [backend/catastro/](backend/catastro/): cadastral domain logic/models
  - [backend/mapas/](backend/mapas/): map-related app and routes
- [backend/downloads/](backend/downloads/): downloaded sample ZIPs and inspection files used during development

## Practical workflow

The app is built around the ATOM discovery/import pipeline. The main entry points are the management commands in [backend/ingest/management/commands/](backend/ingest/management/commands/).

Common commands to keep in mind:

- `cd backend && python manage.py runserver 0.0.0.0:8000`
- `cd backend && python manage.py migrate`
- `cd backend && python manage.py <command_name>` for the Atom/inspection scripts
- `docker compose up --build` for the project stack

The most relevant command files are:

- [backend/ingest/management/commands/atom_root.py](backend/ingest/management/commands/atom_root.py)
- [backend/ingest/management/commands/atom_region.py](backend/ingest/management/commands/atom_region.py)
- [backend/ingest/management/commands/atom_municipality.py](backend/ingest/management/commands/atom_municipality.py)
- [backend/ingest/management/commands/atom_search.py](backend/ingest/management/commands/atom_search.py)
- [backend/ingest/management/commands/atom_download.py](backend/ingest/management/commands/atom_download.py)
- [backend/ingest/management/commands/atom_import.py](backend/ingest/management/commands/atom_import.py)
- [backend/ingest/management/commands/atom_refresh.py](backend/ingest/management/commands/atom_refresh.py)

## Environment and conventions

- Settings rely on environment variables and a local `.env` file for runtime configuration.
- The project defaults to PostGIS (`django.contrib.gis.db.backends.postgis`) and expects the database to be reachable via the env config in [backend/config/settings.py](backend/config/settings.py).
- The application is built around INSPIRE GML data and ZIP downloads from the Catastro public feeds, so changes involving ingestion should preserve the existing command-driven structure rather than introducing ad hoc scripts.
- Prefer extending the existing management command pattern when adding new import or inspection steps.
- The main map view is intentionally simple and lives in [backend/ingest/views.py](backend/ingest/views.py); avoid broad UI rewrites unless the task specifically targets the frontend.

## Typical agent expectations

- If a task concerns data import, inspect the commands under [backend/ingest/management/commands/](backend/ingest/management/commands/) first.
- If a task concerns the web app or routes, inspect [backend/config/urls.py](backend/config/urls.py) and the app-specific views before writing new code.
- If a task concerns environment or deployment, check [docker-compose.yml](docker-compose.yml), [Dockerfile](Dockerfile), and [backend/config/settings.py](backend/config/settings.py) together.
- Keep changes aligned with the project’s existing Django conventions rather than introducing a different architecture.

## Validation

- Prefer project-native Django commands and the provided Docker workflow over ad hoc scripts.
- When adding or changing import logic, validate with the smallest relevant management command or a focused Django check.
- For new app code, keep logic readable and close to the existing app patterns instead of creating unrelated abstractions.
