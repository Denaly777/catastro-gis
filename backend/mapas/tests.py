from django.contrib.gis.geos import GEOSGeometry
from django.test import TestCase

from catastro.models import Parcela


class ParcelasGeojsonViewTests(TestCase):
    def test_default_response_returns_all_parcels_without_limit(self):
        Parcela.objects.create(
            municipio_codigo="05127",
            local_id="test-1",
            referencia_catastral="05127A00100001",
            etiqueta="Test",
            geom=GEOSGeometry(
                "MULTIPOLYGON (((0 0,0 1,1 1,1 0,0 0)))",
                srid=25830,
            ),
        )
        Parcela.objects.create(
            municipio_codigo="05127",
            local_id="test-2",
            referencia_catastral="05127A00100002",
            etiqueta="Test",
            geom=GEOSGeometry(
                "MULTIPOLYGON (((2 2,2 3,3 3,3 2,2 2)))",
                srid=25830,
            ),
        )

        response = self.client.get("/api/parcelas/")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["features"]), 2)
        referencias = {
            feature["properties"]["referencia"]
            for feature in data["features"]
        }
        self.assertEqual(referencias, {"05127A00100001", "05127A00100002"})

    def test_bbox_param_filters_visible_parcels(self):
        Parcela.objects.create(
            municipio_codigo="05127",
            local_id="test-visible",
            referencia_catastral="05127A00100003",
            etiqueta="Visible",
            geom=GEOSGeometry(
                "POINT(343045.1352 4462769.17525)",
                srid=25830,
            ),
        )
        Parcela.objects.create(
            municipio_codigo="05127",
            local_id="test-hidden",
            referencia_catastral="05127A00100004",
            etiqueta="Hidden",
            geom=GEOSGeometry(
                "POINT(1000000 1000000)",
                srid=25830,
            ),
        )

        response = self.client.get(
            "/api/parcelas/",
            {
                "bbox": "-4.85,40.30,-4.84,40.31",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["features"]), 1)
        self.assertEqual(
            data["features"][0]["properties"]["referencia"],
            "05127A00100003",
        )

    def test_zoom_param_simplifies_geometry(self):
        geom = GEOSGeometry(
            "POLYGON ((0 0, 0 10, 1 10, 1 9, 2 9, 2 8, 3 8, 3 0, 0 0))",
            srid=25830,
        )
        Parcela.objects.create(
            municipio_codigo="05127",
            local_id="test-simplified",
            referencia_catastral="05127A00100005",
            etiqueta="Simplified",
            geom=geom,
        )

        response = self.client.get(
            "/api/parcelas/",
            {
                "zoom": 10,
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["features"]), 1)
        coordinates = data["features"][0]["geometry"]["coordinates"]
        self.assertLess(len(coordinates[0][0]), 9)
