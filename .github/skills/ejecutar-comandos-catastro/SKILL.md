---
name: ejecutar-comandos-catastro
description: "Use when the user asks to execute Django management commands in this repository, especially Catastro ATOM workflow commands like atom_root, atom_region, atom_municipality, atom_find_municipio, atom_search, atom_download, atom_import, atom_refresh, inspect_gml, inspect_schema, inspect_features, unzip_downloads, import_parcels, or delete_municipio."
---

# Ejecutar Comandos Catastro

## Objective

Run project commands safely and consistently from the Django backend, with quick validation and clear status reporting.

## Repository Context

- Main working directory for commands: `backend/`
- Django entrypoint: `backend/manage.py`
- Command modules:
  - `backend/ingest/management/commands/atom_root.py`
  - `backend/ingest/management/commands/atom_region.py`
  - `backend/ingest/management/commands/atom_municipality.py`
  - `backend/ingest/management/commands/atom_find_municipio.py`
  - `backend/ingest/management/commands/atom_search.py`
  - `backend/ingest/management/commands/atom_download.py`
  - `backend/ingest/management/commands/atom_import.py`
  - `backend/ingest/management/commands/atom_refresh.py`
  - `backend/ingest/management/commands/inspect_gml.py`
  - `backend/ingest/management/commands/inspect_schema.py`
  - `backend/ingest/management/commands/inspect_features.py`
  - `backend/ingest/management/commands/unzip_downloads.py`
  - `backend/ingest/management/commands/import_parcels.py`
  - `backend/ingest/management/commands/delete_municipio.py`

## Execution Policy

1. Confirm command intent and required parameters.
2. Use one-shot terminal runs in sync mode for command execution.
3. Run from `backend/`:
   - `python manage.py <command> [args]`
4. If the user provides only municipality name (without province), resolve province first with `atom_find_municipio`.
5. Before ATOM commands, verify `requests` is installed in the selected Python environment.
6. If HTTPS fails with `CERTIFICATE_VERIFY_FAILED`, retry using the system CA bundle:
  - `SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt`
  - `REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt`
7. Prefer non-destructive checks before destructive commands.
8. Report useful output only:
   - records processed
   - files created/downloaded
   - warnings and errors
9. If command fails, capture the exact error and propose the next fix command.

## Safety Checklist

Before execution:

1. Verify current directory includes `manage.py`.
2. If parameters are missing, ask for only the missing values.
3. For destructive commands (example: `delete_municipio`), request explicit confirmation.

After execution:

1. Verify expected artifacts (database changes, files, or logs).
2. Summarize result in concise Spanish.
3. Distinguish downloaded datasets from imported datasets. The current `import_parcels` command imports only cadastral parcels (`CP`).

## Common Command Patterns

- Discover root feed:
  - `cd backend && python manage.py atom_root`
- List region or municipality feeds:
  - `cd backend && python manage.py atom_region <provincia_codigo_o_nombre> --dataset cp`
  - `cd backend && python manage.py atom_municipality <provincia_codigo_o_nombre> <municipio_codigo_o_nombre> --dataset cp`
- Search and download:
  - `cd backend && python manage.py atom_search <provincia_codigo_o_nombre> <municipio_codigo_o_nombre> --dataset all`
  - `cd backend && python manage.py atom_download <provincia_codigo_o_nombre> <municipio_codigo_o_nombre> --dataset all`
- Find municipality by name across all provinces:
  - `cd backend && python manage.py atom_find_municipio <nombre_o_codigo> --dataset cp --limit 20`
- Import and refresh:
  - `cd backend && python manage.py atom_import <municipio_codigo>`
  - `cd backend && python manage.py atom_refresh`
- Inspection helpers:
  - `cd backend && python manage.py inspect_gml`
  - `cd backend && python manage.py inspect_schema`
  - `cd backend && python manage.py inspect_features`
- Utility:
  - `cd backend && python manage.py unzip_downloads`
  - `cd backend && python manage.py import_parcels <codigo_5_digitos>`

## Local Runtime Notes

- `requests` is required by `ingest.services.atom`. If it is missing, install it in the active venv before running ATOM commands.
- The project can be run under Docker paths (`/app/backend/downloads`) or locally. `unzip_downloads` should use `Path.cwd() / "downloads"` when run from `backend/`.
- Do not use `unzip_downloads --force` blindly: existing sample directories may be owned by another user. Prefer normal mode, or extract only the requested ZIP files when a permission error occurs.
- The system `unzip` utility may be unavailable. Use Python's standard `zipfile` module as a local fallback rather than requesting elevated package installation.
- A successful `atom_download --dataset all` downloads `CP`, `AD`, and `BU`; it does not import all three into the database.

## Response Template

Use this structure when reporting command execution:

1. Command run
2. Outcome (success/failure)
3. Key metrics (rows/features/files)
4. Next suggested command (if applicable)

## Name-Only Municipality Flow

When the user asks by municipality name only (example: "descarga e importa Mijares"):

1. Run `atom_find_municipio Mijares --dataset cp`.
2. If exactly one result, continue with that province + municipality code.
3. If multiple results, ask user to choose one option by province/code.
4. Continue with `atom_search <region_query> <municipality_query> --dataset all`.
5. Run `atom_download <region_query> <municipality_query> --dataset all`.
6. Extract the requested ZIPs and run `import_parcels <municipality_code>` for the CP dataset.
