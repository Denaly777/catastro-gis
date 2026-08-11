# Catastro GIS

Aplicación para la descarga, tratamiento y visualización de información catastral INSPIRE publicada por la Dirección General del Catastro.

## Fuente de datos

La aplicación utiliza los servicios INSPIRE publicados por la Dirección General del Catastro:

[Catastro INSPIRE](https://www.catastro.hacienda.gob.es/webinspire/index.html)

Los datos se distribuyen mediante feeds ATOM que contienen enlaces a ficheros ZIP.

## Flujo de trabajo

### 1. Descubrimiento de fuentes

La aplicación navega por la estructura de feeds ATOM del Catastro para localizar la información disponible por provincia y municipio.

Los comandos relacionados se encuentran en:

```text
backend/ingest/management/commands/
```

Entre ellos:

```text
atom_root.py
atom_region.py
atom_municipality.py
atom_search.py
```

### 2. Descarga

Una vez localizado un municipio, se descargan los ZIP publicados por el Catastro.

Ejemplos:

```text
05127-MIJARES ADDRESSES-ad.zip
05127-MIJARES BUILDINGS-bu.zip
05127-MIJARES CADASTRAL PARCELS-cp.zip

05054-CASAVIEJA ADDRESSES-ad.zip
05054-CASAVIEJA BUILDINGS-bu.zip
05054-CASAVIEJA CADASTRAL PARCELS-cp.zip
```

Los archivos descargados se almacenan temporalmente en:

```text
backend/downloads/
```

### 3. Tipos de información descargada

#### ADDRESSES

Información de direcciones catastrales.

Sufijo:

```text
-ad.zip
```

#### BUILDINGS

Información de construcciones.

Sufijo:

```text
-bu.zip
```

#### CADASTRAL PARCELS

Información de parcelas catastrales.

Sufijo:

```text
-cp.zip
```

### 4. Importación

Los ZIP contienen ficheros GML conforme a la especificación INSPIRE.

El procesamiento e importación se realiza mediante:

```text
atom_import.py
```

### 5. Actualización

La actualización periódica de los datos se realiza mediante:

```text
atom_refresh.py
```

### 6. Visualización

La aplicación web utiliza:

- Django
- Leaflet
- OpenStreetMap

Ruta principal:

```python
path('', map_view, name='home')
```

Template principal:

```text
backend/ingest/templates/ingest/map.html
```

Actualmente la vista principal muestra un mapa Leaflet centrado sobre el municipio configurado.

## Estructura relevante

```text
backend/
│
├── downloads/
│   ├── *.zip
│
├── ingest/
│   ├── management/
│   │   └── commands/
│   │       ├── atom_root.py
│   │       ├── atom_region.py
│   │       ├── atom_municipality.py
│   │       ├── atom_search.py
│   │       ├── atom_download.py
│   │       ├── atom_import.py
│   │       └── atom_refresh.py
│   │
│   ├── views.py
│   └── templates/
│
└── config/
```

## Municipios de prueba actuales

```text
05127 - Mijares (Ávila)
05054 - Casavieja (Ávila)
```