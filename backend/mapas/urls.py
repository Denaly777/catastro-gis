from django.urls import path

from .views import (
    mapa,
    parcelas_geojson,
)

urlpatterns = [
    path(
        "",
        mapa,
        name="mapa",
    ),

    path(
        "api/parcelas/",
        parcelas_geojson,
        name="parcelas_geojson",
    ),
]