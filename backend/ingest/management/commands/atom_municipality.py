from django.core.management.base import BaseCommand, CommandError

from ingest.services.atom import AtomService


class Command(BaseCommand):
    help = "Muestra la entrada ATOM real de un municipio dentro de su provincia para un dataset concreto."

    def add_arguments(self, parser):
        parser.add_argument("region_query", help="Código o nombre de provincia, por ejemplo 05 o Ávila")
        parser.add_argument("municipality_query", help="Código o nombre de municipio, por ejemplo 05127 o Mijares")
        parser.add_argument("--dataset", default="cp", choices=("cp", "ad", "bu"), help="Dataset ATOM a consultar")

    def handle(self, *args, **options):
        region_query = options["region_query"]
        municipality_query = options["municipality_query"]
        dataset = options["dataset"]
        if not region_query or not municipality_query:
            raise CommandError("Debes indicar una provincia y un municipio.")

        service = AtomService()
        entries = service.find_municipality(region_query, municipality_query, dataset)

        if not entries:
            self.stdout.write(self.style.WARNING(f"No se encontraron entradas para el municipio {municipality_query}."))
            return

        for entry in entries:
            self.stdout.write(f"{entry.title}\t{entry.href}")
