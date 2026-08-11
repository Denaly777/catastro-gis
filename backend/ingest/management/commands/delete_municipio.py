from django.core.management.base import BaseCommand

from catastro.models import Parcela


class Command(BaseCommand):

    help = "Borra todas las parcelas de un municipio"

    def add_arguments(self, parser):

        parser.add_argument(
            "municipio_codigo",
            type=str,
        )

    def handle(self, *args, **options):

        municipio_codigo = options[
            "municipio_codigo"
        ]

        total = (
            Parcela.objects
            .filter(
                municipio_codigo=municipio_codigo
            )
            .count()
        )

        self.stdout.write(
            f"Encontradas {total} parcelas"
        )

        borradas, _ = (
            Parcela.objects
            .filter(
                municipio_codigo=municipio_codigo
            )
            .delete()
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Eliminados {borradas} registros"
            )
        )