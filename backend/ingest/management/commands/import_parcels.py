from pathlib import Path

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry
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

        municipio_codigo = options[
            "municipio_codigo"
        ]

        downloads_path = Path(
            "downloads"
        )

        patron = (
            f"**/{municipio_codigo}-* CADASTRAL PARCELS-cp/"
            f"A.ES.SDGC.CP.{municipio_codigo}.cadastralparcel.gml"
        )

        resultados = list(
            downloads_path.glob(
                patron
            )
        )

        if not resultados:

            self.stdout.write(
                self.style.ERROR(
                    f"No se encontró GML para {municipio_codigo}"
                )
            )

            self.stdout.write(
                f"Ruta buscada: "
                f"{downloads_path.resolve()}"
            )

            self.stdout.write(
                f"Patrón: {patron}"
            )

            return

        fichero = str(
            resultados[0]
        )

        self.stdout.write(
            f"Importando: {fichero}"
        )

        ds = DataSource(
            fichero
        )

        capa = ds[0]

        Parcela.objects.filter(
            municipio_codigo=municipio_codigo
        ).delete()

        contador = 0
        duplicados = 0

        referencias_vistas = set()

        for elemento in capa:

            referencia = elemento.get(
                "nationalCadastralReference"
            )

            if not referencia:
                continue

            if referencia in referencias_vistas:

                duplicados += 1

                continue

            referencias_vistas.add(
                referencia
            )

            geom_25830 = GEOSGeometry(
                elemento.geom.wkt,
                srid=25830,
            )

            geom_4326 = geom_25830.transform(
                4326,
                clone=True,
            )

            try:

                Parcela.objects.create(
                    municipio_codigo=municipio_codigo,
                    local_id=elemento.get(
                        "localId"
                    ),
                    referencia_catastral=referencia,
                    etiqueta=(
                        elemento.get(
                            "label"
                        )
                        or ""
                    ),
                    area=elemento.get(
                        "areaValue"
                    ),
                    fecha_alta=(
                        elemento.get(
                            "beginLifespanVersion"
                        )
                        or ""
                    ),
                    geom_25830=geom_25830,
                    geom_4326=geom_4326,
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
            f"Parcelas en BD: "
            f"{Parcela.objects.count()}"
        )