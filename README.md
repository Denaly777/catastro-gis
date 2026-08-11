# Catastro GIS

Aplicación web desarrollada en Django para visualizar información geográfica del Catastro utilizando datos publicados por la Dirección General del Catastro mediante los servicios INSPIRE.

## Objetivo

La aplicación permite descargar, procesar y visualizar información catastral a partir de los servicios públicos INSPIRE del Catastro español.

Fuente oficial de datos:

[Servicios INSPIRE del Catastro](https://www.catastro.hacienda.gob.es/webinspire/index.html)

## Arquitectura

### Backend

- Django
- Gunicorn
- PostgreSQL
- PostGIS

### Frontend

- HTML
- JavaScript
- Leaflet
- OpenStreetMap

### Infraestructura

- Docker
- Docker Compose
- AWS Lightsail

## Flujo general

1. La aplicación se conecta a los servicios INSPIRE del Catastro.
2. Localiza los ficheros publicados mediante feeds ATOM.
3. Descarga la información geográfica disponible.
4. Procesa los datos descargados.
5. Almacena la información en PostgreSQL/PostGIS.
6. Publica la información mediante una aplicación web basada en Django.
7. La visualización cartográfica se realiza con Leaflet y OpenStreetMap.

## Fuente de datos

Los datos proceden de los servicios INSPIRE publicados por la Dirección General del Catastro.

Tecnología utilizada por la fuente:

- Feed ATOM
- GML
- INSPIRE
- Servicios geográficos europeos

## Estructura del proyecto

backend/
    config/
    ingest/
    templates/

## Punto de entrada

Ruta principal:

```python
path('', map_view, name='home')
```

Vista asociada:

```python
def map_view(request):
    return render(
        request,
        "ingest/map.html",
        ...
    )
```

## Despliegue

El repositorio se encuentra en GitHub.

El despliegue productivo se realiza en AWS Lightsail mediante Docker.

## Pendientes

- Automatizar descargas ATOM.
- Mejorar visualización GIS.
- Incorporar búsquedas por referencia catastral.
- Incorporar análisis espacial mediante PostGIS.