from django.core.management.base import BaseCommand, CommandError

from ingest.services.atom import AtomService


class Command(BaseCommand):
    help = "Lista municipios de una provincia ATOM para un dataset concreto."

    def add_arguments(self, parser):
        parser.add_argument("region_query", help="Código o nombre de provincia, por ejemplo 05 o Ávila")
        parser.add_argument("--dataset", default="cp", choices=("cp", "ad", "bu"), help="Dataset ATOM a consultar")

    def handle(self, *args, **options):
        region_query = options["region_query"]
        dataset = options["dataset"]
        if not region_query:
            raise CommandError("Debes indicar una provincia.")

        service = AtomService()
        region_entry = service.find_region_entry(region_query, dataset)
        entries = service.find_region(region_query, dataset)

        if not entries:
            self.stdout.write(self.style.WARNING(f"No se encontraron entradas para la región {region_query}."))
            return

        self.stdout.write(f"{region_entry.title}\t{region_entry.href}")
        for entry in entries:
            self.stdout.write(f"{entry.title}\t{entry.href}")
