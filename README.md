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
atom_find_municipio.py
atom_search.py
atom_download.py
unzip_downloads.py
import_parcels.py
delete_municipio.py
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

El procesamiento e importación de parcelas se realiza mediante:

```text
import_parcels.py
```

El comando `import_parcels` importa actualmente las parcelas catastrales (`CP`) en PostGIS. Los datasets de direcciones (`AD`) y edificios (`BU`) pueden descargarse y extraerse, pero no se importan mediante este comando.

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
backend/mapas/templates/mapas/index.html
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
│   │       ├── atom_find_municipio.py
│   │       ├── atom_search.py
│   │       ├── atom_download.py
│   │       ├── unzip_downloads.py
│   │       ├── import_parcels.py
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

## Ejecución en AWS Lightsail con Docker

Esta secuencia está pensada para ejecutar el proyecto en una instancia AWS Lightsail mediante Docker Compose y PostgreSQL/PostGIS.

### 1. Actualizar y arrancar

```bash
cd ~/catastro-gis
git pull
sudo docker compose up -d --build
sudo docker compose ps
```

El contenedor `postgis` debe aparecer como `Healthy` y `catastro-gis` como `Up`.

### 2. Aplicar migraciones

```bash
sudo docker compose exec web python manage.py migrate
```

### 3. Buscar un municipio por nombre

La búsqueda devuelve la provincia y el código municipal:

```bash
sudo docker compose exec web \
	python manage.py atom_find_municipio "Gavilanes" \
	--dataset cp --limit 20
```

Ejemplo de resultado:

```text
[05] Territorial office 05 Avila [05082] 05082-GAVILANES
```

En este caso, la provincia es `05` y el código municipal es `05082`.

### 4. Descargar los datasets

```bash
sudo docker compose exec web \
	python manage.py atom_download 05 05082 --dataset all
```

Este comando descarga `CP`, `AD` y `BU` en `backend/downloads/`.

### 5. Descomprimir los ZIP

```bash
sudo docker compose exec -it web \
	python manage.py unzip_downloads
```

Si pregunta por una carpeta existente, responde `n` para conservarla. Para una carpeta nueva, responde `s`.

No uses `--force` si existen carpetas antiguas con permisos diferentes.

### 6. Importar las parcelas en PostGIS

```bash
sudo docker compose exec web \
	python manage.py import_parcels 05082
```

El comando busca el GML de parcelas (`CP`), elimina las parcelas anteriores del municipio e importa las nuevas geometrías en PostGIS.

### 7. Verificar la importación

```bash
sudo docker compose exec web python manage.py shell -c '
from catastro.models import Parcela
print(Parcela.objects.filter(municipio_codigo="05082").count())
'
```

La descarga incluye `CP`, `AD` y `BU`, pero la importación implementada actualmente solo carga las parcelas `CP`.

### 8. Secuencia completa

```bash
cd ~/catastro-gis
sudo docker compose up -d --build
sudo docker compose exec web python manage.py migrate

sudo docker compose exec web \
	python manage.py atom_find_municipio "Gavilanes" \
	--dataset cp --limit 20

# Sustituir 05 y 05082 por los valores devueltos por la búsqueda.
sudo docker compose exec web \
	python manage.py atom_download 05 05082 --dataset all
sudo docker compose exec -it web \
	python manage.py unzip_downloads
sudo docker compose exec web \
	python manage.py import_parcels 05082
```

### 9. Ejemplo con Gijón

```bash
sudo docker compose exec web \
	python manage.py atom_find_municipio "Gijón" \
	--dataset cp --limit 20
sudo docker compose exec web \
	python manage.py atom_download 52 52024 --dataset all
sudo docker compose exec web \
	python manage.py import_parcels 52024
```