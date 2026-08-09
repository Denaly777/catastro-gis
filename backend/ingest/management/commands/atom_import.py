from django.core.management.base import BaseCommand, CommandError

from ingest.services.atom import AtomService


class Command(BaseCommand):
    help = "Prepara la importación del municipio desde ATOM."

    def add_arguments(self, parser):
        parser.add_argument("municipality_code", help="Código de municipio, por ejemplo 28006")

    def handle(self, *args, **options):
        municipality_code = options["municipality_code"]
        if not municipality_code:
            raise CommandError("Debes indicar un código de municipio.")

        service = AtomService()
        entries = service.find_downloads(municipality_code)

        if not entries:
            self.stdout.write(self.style.WARNING(f"No se encontraron datos para importar en {municipality_code}."))
            return

        for entry in entries:
            self.stdout.write(f"{entry.title}\t{entry.href}")
