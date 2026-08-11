from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand

from catastro.models import Parcela


class Command(BaseCommand):

    help = "Importa todas las parcelas catastrales"

    def handle(self, *args, **options):

        fichero = (
            "/app/backend/downloads/"
            "05127-MIJARES CADASTRAL PARCELS-cp/"
            "A.ES.SDGC.CP.05127.cadastralparcel.gml"
        )

        ds = DataSource(fichero)

        capa = ds[0]

        Parcela.objects.all().delete()

        contador = 0

        for elemento in capa:

            referencia = elemento.get(
                "nationalCadastralReference"
            )

            Parcela.objects.create(
                municipio_codigo=referencia[:5],
                local_id=elemento.get("localId"),
                referencia_catastral=referencia,
                etiqueta=elemento.get("label") or "",
                area=elemento.get("areaValue"),
                fecha_alta=elemento.get(
                    "beginLifespanVersion"
                ) or "",
                geom=GEOSGeometry(
                    elemento.geom.wkt,
                    srid=25830,
                ),
            )

            contador += 1

            if contador % 500 == 0:

                self.stdout.write(
                    f"Importadas {contador} parcelas..."
                )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Importación completada: {contador}"
            )
        )

        self.stdout.write(
            f"Parcelas en BD: {Parcela.objects.count()}"
        )