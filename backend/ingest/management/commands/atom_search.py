from django.core.management.base import BaseCommand, CommandError

from ingest.services.atom import AtomService


class Command(BaseCommand):
    help = "Busca provincia y municipio en el flujo ATOM real y muestra los ZIP finales."

    def add_arguments(self, parser):
        parser.add_argument("region_query", help="Código o nombre de provincia, por ejemplo 05 o Ávila")
        parser.add_argument("municipality_query", help="Código o nombre de municipio, por ejemplo 05127 o Mijares")
        parser.add_argument(
            "--dataset",
            default="all",
            choices=("cp", "ad", "bu", "all"),
            help="Dataset ATOM a consultar",
        )

    def handle(self, *args, **options):
        region_query = options["region_query"]
        municipality_query = options["municipality_query"]
        dataset = options["dataset"]

        if not region_query or not municipality_query:
            raise CommandError("Debes indicar una provincia y un municipio.")

        service = AtomService()

        region_entry = service.find_region_entry(region_query, "cp")
        if dataset == "all":
            downloads = service.find_all_downloads(region_query, municipality_query)
        else:
            downloads = [(dataset, service.find_municipality_entry(region_query, municipality_query, dataset))]

        self.stdout.write(self.style.SUCCESS(f"Provincia: {region_entry.title}\t{region_entry.href}"))
        for item_dataset, municipality_entry in downloads:
            download_url = municipality_entry.href
            output_name = service.build_download_filename(municipality_entry, item_dataset)
            self.stdout.write(self.style.SUCCESS(f"Municipio: {municipality_entry.title}\t{municipality_entry.href}"))
            self.stdout.write(self.style.SUCCESS(f"Archivo: {output_name}"))
            self.stdout.write(self.style.SUCCESS(f"ZIP: {download_url}"))