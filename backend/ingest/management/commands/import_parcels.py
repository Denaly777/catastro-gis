from pathlib import Path

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal import DataSource
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from catastro.models import Parcela


class Command(BaseCommand):

    help = "Importa parcelas de un municipio"

    def add_arguments(self, parser):

        parser.add_argument(
            "municipio_codigo",
            type=str,
        )

    def handle(self, *args, **options):

        municipio_codigo = options["municipio_codigo"]

        patron = (
            f"**/{municipio_codigo}-* CADASTRAL PARCELS-cp/"
            f"A.ES.SDGC.CP.{municipio_codigo}.cadastralparcel.gml"
        )

        resultados = list(
            Path("/app/backend/downloads").glob(patron)
        )

        if not resultados:

            self.stdout.write(
                self.style.ERROR(
                    f"No se encontró GML para {municipio_codigo}"
                )
            )

            return

        fichero = str(resultados[0])

        self.stdout.write(
            f"Importando: {fichero}"
        )

        ds = DataSource(fichero)

        capa = ds[0]

        Parcela.objects.filter(
            municipio_codigo=municipio_codigo
        ).delete()

        contador = 0
        duplicados = 0

        for elemento in capa:

            referencia = elemento.get(
                "nationalCadastralReference"
            )

            try:

                Parcela.objects.create(
                    municipio_codigo=municipio_codigo,
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

            except IntegrityError:

                duplicados += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"DUPLICADO: {referencia}"
                    )
                )

                continue

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Importadas: {contador}"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f"Duplicados: {duplicados}"
            )
        )

        self.stdout.write(
            f"Parcelas en BD: {Parcela.objects.count()}"
        )