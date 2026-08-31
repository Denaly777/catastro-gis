import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

from catastro.models import Parcela


def _simplify_geometry(geometry, zoom):
    if zoom is None or zoom >= 16:
        return geometry

    if zoom >= 13:
        tolerance = 0.00001
    elif zoom >= 10:
        tolerance = 0.00002
    else:
        tolerance = 0.00005

    return geometry.simplify(
        tolerance,
        preserve_topology=True,
    )


def mapa(request):
    return render(
        request,
        "mapas/index.html",
        {
            "google_maps_api_key": settings.GOOGLE_MAPS_API_KEY,
        },
    )


def parcelas_geojson(request):
    municipio_codigo = request.GET.get("municipio")
    zoom = request.GET.get("zoom")

    parcelas = Parcela.objects.only(
        "id",
        "municipio_codigo",
        "referencia_catastral",
        "etiqueta",
        "geom_4326",
    )

    if (
        municipio_codigo
        and len(municipio_codigo) == 5
        and municipio_codigo.isdigit()
    ):
        parcelas = parcelas.filter(
            municipio_codigo=municipio_codigo
        )

    zoom_value = (
        int(zoom)
        if zoom and zoom.isdigit()
        else None
    )

    features = []

    for parcela in parcelas.iterator(chunk_size=500):

        geometry = _simplify_geometry(
            parcela.geom_4326,
            zoom_value,
        )

        features.append(
            {
                "type": "Feature",
                "geometry": json.loads(
                    geometry.geojson
                ),
                "properties": {
                    "id": parcela.id,
                    "referencia": parcela.referencia_catastral,
                    "municipio": parcela.municipio_codigo,
                    "etiqueta": parcela.etiqueta,
                },
            }
        )

    return JsonResponse(
        {
            "type": "FeatureCollection",
            "features": features,
        }
    )